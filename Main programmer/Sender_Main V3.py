import socket
import json
import time
from inputs import get_gamepad
import math
import threading
import inputimeout
from pynput.keyboard import Key, Listener # For registering keyboard inputs
import numpy as np

## Settings

# Define UDP settings
IP = "10.193.58.153"  # Replace with the receiver device's IP address
UDP_PORT = 5005

# Define server settings (IP and Port should match the TCP server)
SERVER_IP = IP  # Replace with the actual server IP
SERVER_PORT = 5006  # Port number defined for TCP in the server

# The bigger this value is, the bigger the range of inputs that it just sets to center. Recommended no bigger than 12
global CenterRange
CenterRange = 7

## End of setting

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# True if the program should be sending joystick position information
global IsSending
IsSending = False

# How much delay there is between each UDP send
global WriteDelay
WriteDelay = 0.125



class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):
        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def read(self):

        return {
            'LeftJoystickX': self.LeftJoystickX,
            'LeftJoystickY': self.LeftJoystickY,
            'RightJoystickX': self.RightJoystickX,
            'RightJoystickY': self.RightJoystickY,
            'A': self.A,
            'B': self.B,
            'LeftBumper': self.LeftBumper,
            'RightBumper': self.RightBumper,
            'LeftTrigger': self.LeftTrigger,
            'RightTrigger': self.RightTrigger,
        }

    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL
                elif event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.A = event.state
                elif event.code == 'BTN_NORTH':
                    self.Y = event.state
                elif event.code == 'BTN_WEST':
                    self.X = event.state
                elif event.code == 'BTN_EAST':
                    self.B = event.state
                elif event.code == 'BTN_THUMBL':
                    self.LeftThumb = event.state
                elif event.code == 'BTN_THUMBR':
                    self.RightThumb = event.state
                elif event.code == 'BTN_SELECT':
                    self.Back = event.state
                elif event.code == 'BTN_START':
                    self.Start = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY1':
                    self.LeftDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY2':
                    self.RightDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY3':
                    self.UpDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY4':
                    self.DownDPad = event.state

# Instantiate XboxController object with Rs = 10000 (10 kΩ)
joy = XboxController()



# Builds bytes
def ByteBuilder(Dir, JoyPos):
    
    global CenterRange

    # Dir: 1 = LHor, 2 = LVer, 3=RHor, 4=RVer
    # JoyPos is the corresponding position of the joystick between -1 and 1.

    # Finds interpolated N-values

    N = N_interpolater(Dir, JoyPos)

    # Converts N to int
    N = int(np.round(N))

    # Checks if value for N is within range (20-240)
    if (N > 240 or N < 20):
        print("Error! Value for resistance is out of range at N = " + str(N))
        if N > 240:
            N = 240
        if N < 20:
            N = 20
    
    # Rounds to center
    if (N + CenterRange > 145 | N-CenterRange < 145):
        N = 145
    

    # Initializes double byte
    InitB = 0x8000

    # Defines that it needs to write
    CommandB = 0x00

    # Defines which wiper to write to
    if Dir in [1,3]:
        AxisB = 0b0000000000000000
    else:
        AxisB = 0b0001000000000000

    print(f"Dir is {Dir} and AxisB is {AxisB}")

    # Assembles byte
    Byte = InitB | CommandB | AxisB | N

    # Sets bit 16 and 9 to zero
    Byte = Byte & 0x7EFF
    
    # Splits byte into two eights
    Byte1 = Byte >> 8
    Byte2 = Byte & 0b11111111
    
    return Byte1, Byte2





# Values for N-interpolation
NVals = {
    1: 185*1.2,  #LHorL
    2: 145,   #LHorC
    3: 65/1.2, #LHorR
    4: 217*1.2, #LVerD
    5: 145, #LVerC
    6: 113/1.2, #LVerU
    7: 185*1.2, # RHorL
    8: 145, #RHorC
    9: 65/1.2, #RHorR
    10: 113/1.2, #RVerD
    11: 145, #RVerC
    12: 217*1.2, #RVerU
}




def N_interpolater(Dir, pos):
    # Dir: 1 = LHor, 2 = LVer, 3=RHor, 4=RVer
    # pos: position of joystick between -1 and 1

    # Initialize N-output
    Nout = 0

    # Normalize position from -1 to 1 to 0 to 1
    pos = (pos + 1)/2 

    # Interpolates with correct values.
    # LHor
    if Dir == 1:
        if pos <= 0.5:
            Nout = NVals[2] + 2*(NVals[1] - NVals[2])*(0.5-pos)
        else:
            Nout = NVals[2] + 2*(NVals[2] - NVals[3])*(0.5-pos)
    
    # LVer
    if Dir  == 2:
        if pos <= 0.5:
            Nout = NVals[5] + 2*(NVals[4] - NVals[5])*(0.5-pos)
        else:
            Nout = NVals[5] + 2*(NVals[5] - NVals[6])*(0.5-pos)
    
    # RHor
    if Dir == 3:
        if pos <=0.5:
            Nout = NVals[8] + 2*(NVals[7] - NVals[8])*(0.5-pos)
        else:
            Nout = NVals[8] + 2*(NVals[8] - NVals[9])*(0.5-pos)

    # RVer
    if Dir == 4:
        if pos <=0.5:
            Nout = NVals[11] + 2*(NVals[10] - NVals[11])*(0.5-pos)
        else:
            Nout = NVals[11] + 2*(NVals[11] - NVals[12])*(0.5-pos)

    if Nout == 0:
        print(f"Error! Interpolation returned 0!. Inputs were Dir = {Dir} and pos = {pos}. Returning center-ish value instead.")
        Nout = 145
    
    return Nout




def Joy2Bytes(datain):
    B1LHor, B2LHor = ByteBuilder(1, datain['LeftJoystickX'])
    B1LVer, B2LVer = ByteBuilder(2, datain['LeftJoystickY'])
    B1RHor, B2RHor = ByteBuilder(3, datain['RightJoystickX'])
    B1RVer, B2RVer = ByteBuilder(4, datain['RightJoystickY'])

    return{
        'B1LHor': B1LHor,
        'B2LHor': B2LHor,
        'B1LVer': B1LVer,
        'B2LVer': B2LVer,
        'B1RHor': B1RHor,
        'B2RHor': B2RHor,
        'B1RVer': B1RVer,
        'B2RVer': B2RVer,
    }



# UDP joystick sender function
def UDPfunc():
    sendNum = 0
    global IsSending
    global WriteDelay
    while True:
        #print(IsSending)
        if IsSending:
            sendNum = sendNum+1
            # Read the joystick and button states
            data = joy.read()
            
            # Convert joystick data to bytes
            senddata = Joy2Bytes(data)
            
            # Convert data to JSON string for sending over UDP
            message = json.dumps(senddata)

            # Send the JSON message via UDP, and prints every 5th time
            sock.sendto(message.encode('utf-8'), (IP, UDP_PORT))
            if sendNum%5 == 0:
                #print(f"\rSent: {message}",end = '', flush=True)  # Debugging: print the sent data
                try:  
                    print("\rSent joystick positions: LeftY = {}, LeftX = {}, RightY = {}, RightX = {}".format(data['LeftJoystickY'], data["LeftJoystickX"], data["RightJoystickY"],data["RightJoystickX"]))
                    print(f"Sent bytes: LHor {senddata['B1LHor']} {senddata['B2LHor']}, LVer {senddata['B1LVer']} {senddata['B2LVer']}, RHor {senddata['B1RHor']} {senddata['B2RHor']}, RVer {senddata['B1RVer']} {senddata['B2RVer']}")

                except Exception as Excp:
                    print("Data is of type none, exception is {}".format(Excp))


            # Stops overflow
            if sendNum > 1000:
                sendNUm = 0

            # Delay between each send to avoid flooding the network
            time.sleep(0.1)  # Adjust delay as needed
            print(f"Sent bytes: LHor {senddata['B1LHor']} {senddata['B2LHor']}, LVer {senddata['B1LVer']} {senddata['B2LVer']}, RHor {senddata['B1RHor']} {senddata['B2RHor']}, RVer {senddata['B1RVer']} {senddata['B2RVer']}")
        else:
            time.sleep(3)
        time.sleep(WriteDelay)
        




# TCP function sender
def TCP_send_command(command):
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to TCP server at {SERVER_IP}:{SERVER_PORT}")

        # Send the command (as a string)
        client_socket.sendall(str(command).encode('utf-8'))
        print(f"Sent command: {command}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the connection
        client_socket.close()
        print("Connection closed")





        



# Command dictionary
commands = {
    'w': "turn_on_controller_pwr",
    'e': "turn_off_controller_pwr",
    't': "turn_on_controller",
    'y': "turn_off_controller",
    'o': "turn_on_drone",
    'p': "turn_off_drone",
    'n': "start_charging",
    'm': "stop_charging",
    'x': "start_controls",
    "c": "stop_controls",
}



# Start keyboard listener
def on_press(key):
    try:
        keyin = key.char
        global IsSending
        print('\n{0} pressed'.format(
            key))
        print(key.char)
        if key.char in commands:
            print("Sent command: {}".format(commands[key.char]))
            TCP_send_command(commands[key.char])
        else:
            print("Uknown key pressed: {0}".format(key))

        if key.char == 'x':
            IsSending = True
        
        if key.char == 'c':
            IsSending = False

        print("IsSending is " + str(IsSending))
    except Exception as Excp:
        print("No char associated with that key")

def on_release(key):
    nothing = 1
    


# Function to start the listener
def start_listener():
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()  # Blocks the thread it's in



# Run the listener in a separate thread
listener_thread = threading.Thread(target=start_listener, daemon=True)
listener_thread.start()


# Start UDP thread
udp_thread = threading.Thread(target=UDPfunc)

udp_thread.start()

udp_thread.join()

