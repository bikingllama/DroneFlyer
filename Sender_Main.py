import socket
import json
import time
from inputs import get_gamepad
import math
import threading
import inputimeout

# True if the program should be running
global IsRunning
IsRunning = False

# Define UDP settings
IP = "10.192.95.136"  # Replace with the receiver device's IP address
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
    while IsRunning:
        # Read the joystick and button states
        data = joy.read()

        # Convert data to JSON string for sending over UDP
        message = json.dumps(data)

        # Send the JSON message via UDP
        sock.sendto(message.encode('utf-8'), (IP, UDP_PORT))

        print(f"Sent: {message}")  # Debugging: print the sent data

        # Delay between each send to avoid flooding the network
        time.sleep(0.1)  # Adjust delay as needed





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




# TCP input registration
def TCPinput():
    while IsRunning:
        # Time to wait for each command
        # Presets input to be blank
        CmdIn = "Nothing"
        try:
            CmdIn = inputtimeout(prompt='Ready to send TCP command')
        except TimeoutOccured:
            CmdIn = "Nothing"
        if CmdIn != "Nothing":
            try:
                TCP_send_command(commands(CmdIn))
            except Exception as Excp:
                print("Exception! Wrong input; " + Excp)



        




# Command dictionary
commands = {
    "start_charging": 1,
    "stop_charging": 2,
    "turn_on_controller": 3,
    "turn_off_controller": 4,
    "perform_special_task": 9,
}




# Start both UDP and TCP senders in separate threads
udp_thread = threading.Thread(target=UDPfunc)
tcp_thread = threading.Thread(target=TCPinput)

udp_thread.start()
tcp_thread.start()

udp_thread.join()
tcp_thread.join()



