import socket
import json
import time
import threading
import RPi.GPIO as GPIO
import spidev
import numpy as np

# WriteDelay, between each write operation
global WriteDelay
WriteDelay = 0.05

# GPIO setup
GPIO.setmode(GPIO.BOARD)  # Use board pins instead of the GPI index

# Defines pins corresponding to functions
P8 = 8
P10 = 10
P12 = 12
P16 = 16
P18 = 18
P22 = 22
CSL = 31
CSR = 29
CtrPwP = 36

# Sets up pins and initial states
GPIO.cleanup
GPIO.setup(P8, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(P10, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(P12, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(P16, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(P18, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(P22, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(CSL, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(CSR, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(CtrPwP, GPIO.OUT, initial = GPIO.LOW)

# SPI setup
# Setup SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 10**6

# Whether or not digipots should be updated:
global IsSending
IsSending = False


# Define UDP settings for joystick data
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
UDP_PORT = 5005

# Define TCP settings for numeric commands
TCP_IP = "0.0.0.0"
TCP_PORT = 5006

# Define statd bytes for both joysticks (neutral joystick positions). These are used for the failsafe.
StdB1LHor = 0  # Standard first byte for left horizontal
StdB1LVer = 0  # Standard first byte for left vertical
StdB1RHor = 0 # Standard first byte for right horizontal
StdB1RVer = 0  # Standard first byte for right vertical

StdB2LHor = 143  # Standard second byte for left horizontal
StdB2LVer = 147   # Standard second byte for left vertical
StdB2RHor = 140 # Standard second byte for right horizontal
StdB2RVer = 145  # Standard second byte for right vertical
print("Joystick standard bytes not defined!")

# Timeout threshold (in seconds) - No data for this long before cycling
TIMEOUT = 0.3  # seconds



# This function updates the value for one of the resistors.
# VnV determines if it writes to volatile or nonvolatile memory, 0 is volatile.
# The stick defines if its the left or right stick, 0 is left, 1 is right.
# The axis defines whether is up/down or sideways, 0 is horizontal, 1 is vertical.






# Define functions for the TCP actions
def func1():
    # Turns on power for controller
    GPIO.output(CtrPwP, GPIO.HIGH)
    print("Controller turned on (not implemented!)")

def func2():
    # Turns off power for controller
    GPIO.output(CtrPwrP, GPIO.LOW)
    print("Controller turned off (not implemented!)")
    
    
def func3():
    # Turns on and off controller
    # First a short press, then a long
    print("Func3 ran")
    GPIO.output(P8, GPIO.HIGH)
    time.sleep(0.55)
    GPIO.output(P8, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(P8, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(P8, GPIO.LOW)

def func4():
    # Turns on/off drone (battery)
    print("Drone turned on (not implemented!)")

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
    print("Start Charging Drone (not implemented)")


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
    print("Stop Charging Drone (not implemented)")

def func13():
    # Starts control sending
    global IsSending
    IsSending = True

def func14():
    # Stops control sending
    global IsSending
    IsSending = False



# Map numbers to functions
# Command dictionary
commands = {
    "turn_on_controller_pwr": func1,
    "turn_off_controller_pwr": func2,
    "turn_on_controller": func3,
    "turn_off_controller": func3,
    "turn_on_drone": func4,
    "turn_off_drone": func4,
    "start_charging": "func11",
    "stop_charging": "func12",
    "start_controls": func13,
    "stop_controls": func14,
}

# Function to process joystick data
def process_joystick_data(data):

    # Set to defaults if no data recieved
    B1LHor = data.get('B1LHor', StdB1LHor)  
    B1LVer = data.get('B1LVer', StdB1LVer)  
    B1RHor = data.get('B1RHor', StdB1RHor)  
    B1RVer = data.get('B1RVer', StdB1RVer)
    
    B2LHor = data.get('B2LHor', StdB2LHor)  
    B2LVer = data.get('B2LVer', StdB2LVer)  
    B2RHor = data.get('B2RHor', StdB2RHor)  
    B2RVer = data.get('B2RVer', StdB2RVer)

    print("Recieved bytes {B1LHor:08b} {B2LHor:08b}, {B1LVer:08b} {B2LVer:08b}, {B1RHor:08b} {B2RHor:08b}, {B1RVer:08b} {B2Rver:08b}")
    
    # Send to bytesender
    WriteByte(B1LHor, B2LHor, CSL)
    WriteByte(B1LVer, B2LVer, CSL)
    WriteByte(B1RHor, B2RHor, CSR)
    WriteByte(B1RVer, B2RVer, CSR)
    
    


def WriteByte(Byte1, Byte2, CSLPin):
    global WriteDelay
    print("Sending {} and {} with CS pin {}".format(Byte1, Byte2, CSLPin))
    GPIO.output(CSLPin, GPIO.LOW)
    Response = spi.xfer2([Byte1, Byte2])    # Send 2-byte SPI command
    GPIO.output(CSLPin, GPIO.HIGH)
    time.sleep(WriteDelay)    # Wait so CS can be high for sure
    print(f"Response is {Response}")





# Thread: UDP listener for joystick data
def udp_listener():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((UDP_IP, UDP_PORT))
    udp_sock.settimeout(TIMEOUT)  # Set a timeout for failsafe operation
    print(f"Listening for joystick data on UDP {UDP_IP}:{UDP_PORT}")

    # Initialize last received time and last data, sendnumber
    last_received_time = time.time()
    last_data = {'B1LHor': StdB1LHor, 'B2LHor': StdB2LHor, 'B1LVer': StdB1LVer,'B2LVer': StdB2LVer,
                'B1RHor': StdB1RHor, 'B2RHor': StdB2RHor, 'B1RVer': StdB1RVer, 'B2RVer': StdB2RVer}
    send_number = 0

    while True:
        checktime = time.time()
        if IsSending:
            try:
                data, addr = udp_sock.recvfrom(1024)  # Buffer size of 1024 bytes
                message = data.decode('utf-8')

                try:
                    decoded_data = json.loads(message)
                    last_received_time = time.time()  # Update the last received time
                    last_data = decoded_data # Update last_data
                    process_joystick_data(decoded_data)

                    # Print every tenth
                    send_number = send_number+1
                    if send_number % 10 == 0:
                        print(f"Received data {decoded_data}")
                    # Stops overflow
                    if send_number > 1000:
                        send_number = 0
                except json.JSONDecodeError:
                    print(f"Invalid joystick data received: {message}")

            except socket.timeout:
                # If no data received within the timeout, use center values if time between commands is more than 0.25 seconds
                if time.time()-last_received_time < 0.25:
                    time.sleep(0.05)
                else:
                    print("Time from last received data > 0.25 seconds, using center values")
                    process_joystick_data({
                        'B1LHor': StdB1LHor, 'B2LHor': StdB2LHor, 'B1LVer': StdB1LVer,'B2LVer': StdB2LVer,
                        'B1RHor': StdB1RHor, 'B2RHor': StdB2RHor, 'B1RVer': StdB1RVer, 'B2RVer': StdB2RVer
                    })

        else:
            time.sleep(0.1)


# Thread: TCP listener for numeric commands
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
                command = message

                try:
                    if command in commands:
                        print("Running function {}".format(commands[command]))
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
