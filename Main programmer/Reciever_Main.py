import socket
import json
import time
import threading
import RPi.GPIO as GPIO
import spidev
import numpy as np


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

# Define center values for both joysticks (neutral joystick positions). These are used for the failsafe.
CENTER_X_LEFT = 3.85  # Center value for X joystick (AD0 for left)
CENTER_Y_LEFT = 3.9   # Center value for Y joystick (AD1 for left)
CENTER_X_RIGHT = 3.85 # Center value for X joystick (AD0 for right)
CENTER_Y_RIGHT = 3.9  # Center value for Y joystick (AD1 for right)

# Timeout threshold (in seconds) - No data for this long before using center values
TIMEOUT = 1.0  # seconds



# This function updates the value for one of the resistors.
# VnV determines if it writes to volatile or nonvolatile memory, 0 is volatile.
# The stick defines if its the left or right stick, 0 is left, 1 is right.
# The axis defines whether is up/down or sideways, 0 is horizontal, 1 is vertical.

def UpdateResistance(VnV, Stick, Axis, Value):
    # Initializes double byte
    InitB = 0x8000

    # Defines that it needs to write
    CommandB = 0x00

    # Defines which pot to write to
    if Axis == 0:
        AxisB = 0x00
    elif Axis == 1:
        AxisB = 0x1000

    # Defines whether to write to volatile or nonvolatile
    if VnV == 0:
        VnVB = 0x00
    elif VnV == 1:
        VnVB = 0x2000

    # Converts value to integer to set pot to. Arbitratily rounded down
    # R_WB = R_AB*N/256+RW
    # N = (R_WB-RW)*256/R_AB
    N = int(np.floor((Value-75)*256/10000))

    # Checks if value for N is within range (0-256)
    if (N > 256 or N < 0):
        print("Error! Value for resistance is out of range at N = " + str(N))
        if N > 256:
            N = 256
        if N < 0:
            N = 0

    # Assembles byte
    Byte = InitB | CommandB | AxisB | VnVB | N

    # Sets bit 16 and 9 to zero
    Byte = Byte & 0x7EFF
    
    # Splits byte into two eights
    Byte1 = Byte >> 8
    Byte2 = Byte & 0b11111111

    if not Stick:
        CurrOutPin = CSL
    else:
        CurrOutPin = CSR
        
    # Initialize response
    Response = 0b1
    
    #Sends output
    try:
        print("First byte is {:08b} & second byte is {:08b}".format(Byte1, Byte2))
        GPIO.output(31, GPIO.LOW)
        Response = spi.xfer2([Byte1, Byte2])    # Send 2-byte SPI command
        GPIO.output(31, GPIO.HIGH)
        time.sleep(0.01)
    except Exception as Excp:
        print("Exception when sending:\n")
        print(Excp)

        
    # Prints response
    if Response != 0b1:
        print("Recieved response:\n")
        print(Response)

    # Sets both CS-pins to be high to be sure
    GPIO.output(CSL, GPIO.HIGH)
    GPIO.output(CSR, GPIO.HIGH)

    print("Updated digipot {} wiper {} to value N= {}, for potentionemter".format(Stick+1,Axis,N))





# Define functions for the TCP actions
def turn_on_controller_pwr():
    GPIO.output(CtrPwP, GPIO.HIGH)
    print("Controller turned on (not implemented!)")

def turn_off_controller_pwr():
    GPIO.output(CtrPwrP, GPIO.LOW)
    print("Controller turned off (not implemented!)")
    
    
def turn_on_controller():
    # First a short press, then a long
    GPIO.output(P8, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(P8, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(P8, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(P8, GPIO.LOW)

def turn_on_drone():
    print("Drone turned on (not implemented!)")

def turn_off_drone():
    print("Drone turned off (not implemented!)")

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
# Command dictionary
commands = {
    1: "turn_on_controller_pwr",
    2: "turn_off_controller_pwr",
    3: "turn_on_controller",
    3: "turn_off_controller",
    4: "turn_on_drone",
    4: "turn_off_drone",
    11: "start_charging",
    12: "stop_charging",
    13: "start_controls",
    14: "stop_controls",
}

# Function to process joystick data
def process_joystick_data(data):
    LeftJoystickX = data.get('LeftJoystickX', CENTER_X_LEFT)  # Default to center value if missing
    LeftJoystickY = data.get('LeftJoystickY', CENTER_Y_LEFT)  # Default to center value if missing

    RightJoystickX = data.get('RightJoystickX', CENTER_X_RIGHT)  # Default to center value if missing
    RightJoystickY = data.get('RightJoystickY', CENTER_Y_RIGHT)  # Default to center value if missing

    print(f"Received Left Joystick -> X: {LeftJoystickX:.2f}, Y: {LeftJoystickY:.2f}")
    print(f"Received Right Joystick -> X: {RightJoystickX:.2f}, Y: {RightJoystickY:.2f}")

    #UpdateResistance(0,)


# Thread: UDP listener for joystick data
def udp_listener():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((UDP_IP, UDP_PORT))
    udp_sock.settimeout(TIMEOUT)  # Set a timeout for failsafe operation
    print(f"Listening for joystick data on UDP {UDP_IP}:{UDP_PORT}")

    last_received_time = time.time()

    while True:
        if IsSending:
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
        else:
            time.sleep(0.1)


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
