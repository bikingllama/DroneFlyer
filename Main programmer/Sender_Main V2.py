import socket
import json
import time
from inputs import get_gamepad
import math
import threading
import inputimeout
from pynput.keyboard import Key, Listener # For registering keyboard inputs

# True if the program should be sending joystick position information
global IsSending
IsSending = False

# Define UDP settings
IP = "10.193.50.157"  # Replace with the receiver device's IP address
UDP_PORT = 5005

# Define server settings (IP and Port should match the TCP server)
SERVER_IP = IP  # Replace with the actual server IP
SERVER_PORT = 5006  # Port number defined for TCP in the server

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)




class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self, Rs):
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
        self.Rs = Rs  # Series resistance

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def read(self):
        # Apply the resistance conversion
        left_resistance = self._convert_to_potentiometer_resistance(self.LeftJoystickX, self.LeftJoystickY)
        right_resistance = self._convert_to_potentiometer_resistance(self.RightJoystickX, self.RightJoystickY)

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
            'LeftJoystickResistance': left_resistance,
            'RightJoystickResistance': right_resistance
        }

    def _convert_to_potentiometer_resistance(self, x, y):
        # DJI controller potentiometer boundaries
        AD1_top = 0.64       # Top position voltage for AD1
        AD1_bottom = 2.28    # Bottom position voltage for AD1
        AD1_center = 1.6     # Center voltage for AD1

        AD0_left = 2.653     # Left position voltage for AD0
        AD0_right = 0.88     # Right position voltage for AD0
        AD0_center = 1.85    # Center voltage for AD0

        # Normalize joystick input from -1..1 to 0..1
        x_pos = (x + 1) / 2  # Horizontal position (0 = left, 1 = right)
        y_pos = (y + 1) / 2  # Vertical position (0 = top, 1 = bottom)

        # Interpolate for AD1 (vertical direction)
        if y_pos < 0.5:
            # Interpolate between top and center for y_pos in [0, 0.5]
            AD1_interpolated = AD1_top + 2 * (AD1_center - AD1_top) * y_pos
        else:
            # Interpolate between center and bottom for y_pos in (0.5, 1]
            AD1_interpolated = AD1_center + 2 * (AD1_bottom - AD1_center) * (y_pos - 0.5)

        # Interpolate for AD0 (horizontal direction)
        if x_pos < 0.5:
            # Interpolate between left and center for x_pos in [0, 0.5]
            AD0_interpolated = AD0_left + 2 * (AD0_center - AD0_left) * x_pos
        else:
            # Interpolate between center and right for x_pos in (0.5, 1]
            AD0_interpolated = AD0_center + 2 * (AD0_right - AD0_center) * (x_pos - 0.5)

        # Convert interpolated voltages to resistances
        RwR0 = (AD0_interpolated / 3.3) * self.Rs  # Resistance for AD0
        RwR1 = (AD1_interpolated / 3.3) * self.Rs  # Resistance for AD1

        return {'RwR0': RwR0, 'RwR1': RwR1}

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
joy = XboxController(10000.0)






# UDP joystick sender function
def UDPfunc():
    sendNum = 0
    while True:
        if IsSending:
            sendNum = sendNum+1
            # Read the joystick and button states
            data = joy.read()

            # Convert data to JSON string for sending over UDP
            message = json.dumps(data)

            # Send the JSON message via UDP, and prints every 5th time
            sock.sendto(message.encode('utf-8'), (IP, UDP_PORT))
            if sendNum%5 == 0:
                print(f"\rSent: {message}",end = '', flush=True)  # Debugging: print the sent data
            
            # Stops overflow
            if sendNum >1000:
                sendNUm = 0

            # Delay between each send to avoid flooding the network
            time.sleep(0.1)  # Adjust delay as needed
        else:
            time.sleep(0.1)




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
        print('{0} pressed'.format(
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

