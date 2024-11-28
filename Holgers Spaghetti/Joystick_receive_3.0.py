import socket
import json
import time
import threading

#Uncomment the RPI.GPIO setup when the system i linux based

#import RPi.GPIO as GPIO
# GPIO setup
#GPIO.setmode(GPIO.BOARD)  # Use board pins instead of the GPI index
#GPIO.setup(OUTPUT_PIN, GPIO.OUT)  # Set the pin as an output
# charging_PIN = 20  # Use board pin 20
# uncharging_PIN = 18  # Use board pin 18

# Define UDP settings for joystick data
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
UDP_PORT = 5005

# Define TCP settings for numeric commands
TCP_IP = "0.0.0.0"
TCP_PORT = 5006

# Define center values for both joysticks (neutral joystick positions). These are used for the failsafe.
CENTER_X_LEFT = 3.85  # Center value for X joystick (AD0 for left)
CENTER_Y_LEFT = 3.9   # Center value for Y joystick (AD1 for left)
CENTER_X_RIGHT = 3.85 # Center value for X joystick (AD0 for right)
CENTER_Y_RIGHT = 3.9  # Center value for Y joystick (AD1 for right)

# Timeout threshold (in seconds) - No data for this long before using center values
TIMEOUT = 1.0  # seconds

# Define functions for the TCP actions
def do_nothing():
    print("Not on")

def start_charging():
    # This function starts charging the drone. We set the board pin 20 high, in order to flip a bistable relay.

#uncomment this when linux is implemented
   #try:
  #      print(f"Activating GPIO pin {charging_PIN}")
  #      GPIO.output(charging_PIN, GPIO.HIGH)  # Turn the pin ON (charging starts)
 #       time.sleep(1)  # A brief pulse to flip the relay (adjust based on the relay's needs)
  #      print(f"Deactivating GPIO pin {charging_PIN}")
   #     GPIO.output(charging_PIN, GPIO.LOW)  # Turn the pin OFF (charging stops)
   # except Exception as e:
    #    print(f"Error occurred while controlling the relay: {e}")
    print("Start Charging Drone")


def stop_charging():
# This function stops charging the drone. We set the board pin 18 high, in order to flip a bistable relay.

    # uncomment this when linux is implemented
    # try:
    #      print(f"Activating GPIO pin {uncharging_PIN}")
    #      GPIO.output(uncharging_PIN, GPIO.HIGH)  # Turn the pin ON (uncharging starts)
    #      time.sleep(1)  # A brief pulse to flip the relay (adjust based on the relay's needs)
    #      print(f"Deactivating GPIO pin {uncharging_PIN}")
    #      GPIO.output(uncharging_PIN, GPIO.LOW)  # Turn the pin OFF (uncharging stops)
    # except Exception as e:
    #    print(f"Error occurred while controlling the relay: {e}")
    print("Stop Charging Drone")

def perform_special_task():
    print("Performing other task")

# Map numbers to functions
commands = {
    0: do_nothing,
    1: start_charging,
    2: stop_charging,
    9: perform_special_task,
}


# Function to process joystick data
def process_joystick_data(data):
    LeftJoystickX = data.get('LeftJoystickX', CENTER_X_LEFT)  # Default to center value if missing
    LeftJoystickY = data.get('LeftJoystickY', CENTER_Y_LEFT)  # Default to center value if missing

    RightJoystickX = data.get('RightJoystickX', CENTER_X_RIGHT)  # Default to center value if missing
    RightJoystickY = data.get('RightJoystickY', CENTER_Y_RIGHT)  # Default to center value if missing

    print(f"Received Left Joystick -> X: {LeftJoystickX:.2f}, Y: {LeftJoystickY:.2f}")
    print(f"Received Right Joystick -> X: {RightJoystickX:.2f}, Y: {RightJoystickY:.2f}")


# Thread: UDP listener for joystick data
def udp_listener():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((UDP_IP, UDP_PORT))
    udp_sock.settimeout(TIMEOUT)  # Set a timeout for failsafe operation
    print(f"Listening for joystick data on UDP {UDP_IP}:{UDP_PORT}")

    last_received_time = time.time()

    while True:
        try:
            data, addr = udp_sock.recvfrom(1024)  # Buffer size of 1024 bytes
            message = data.decode('utf-8')

            try:
                decoded_data = json.loads(message)
                last_received_time = time.time()  # Update the last received time
                process_joystick_data(decoded_data)
            except json.JSONDecodeError:
                print(f"Invalid joystick data received: {message}")

        except socket.timeout:
            # If no data received within the timeout, use center values
            print("Failsafe: No data received, using center values")
            process_joystick_data({
                'LeftJoystickX': CENTER_X_LEFT, 'LeftJoystickY': CENTER_Y_LEFT,
                'RightJoystickX': CENTER_X_RIGHT, 'RightJoystickY': CENTER_Y_RIGHT
            })


# Thread: TCP listener for numeric commands
def tcp_listener():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind((TCP_IP, TCP_PORT))
    tcp_sock.listen(5)  # Allow up to 5 pending connections
    print(f"Listening for commands on TCP {TCP_IP}:{TCP_PORT}")

    while True:
        conn, addr = tcp_sock.accept()  # Accept a new connection
        print(f"New TCP connection from {addr}")

        while True:
            try:
                data = conn.recv(1024)  # Receive up to 1024 bytes of data
                if not data:
                    print(f"TCP connection from {addr} closed")
                    break

                message = data.decode('utf-8')
                print(f"Received command: {message}")

                try:
                    command = int(message)  # Try to parse the command as an integer
                    if command in commands:
                        commands[command]()  # Execute the associated command function
                    else:
                        print(f"Unknown command: {command}")
                except ValueError:
                    print(f"Invalid command received: {message}")
            except Exception as e:
                print(f"Error with TCP connection from {addr}: {e}")
                break

        conn.close()


# Start both UDP and TCP listeners in separate threads
udp_thread = threading.Thread(target=udp_listener)
tcp_thread = threading.Thread(target=tcp_listener)

udp_thread.start()
tcp_thread.start()

udp_thread.join()
tcp_thread.join()

# finally:
# Clean up GPIO settings
GPIO.cleanup()
#     print("GPIO cleanup completed")