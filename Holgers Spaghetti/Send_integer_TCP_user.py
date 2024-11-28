import socket

# Define server settings (IP and Port should match the TCP server)
SERVER_IP = "10.193.54.29"  # Replace with the actual server IP
SERVER_PORT = 5006  # Port number defined for TCP in the server

def send_command(command):
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


# Example usage: Send a numeric command
if __name__ == "__main__":
    # Example string input (replace with user input or other logic as needed)

    # Here you can edit the string variable "user_input" to perform one action at a time.
    # Run the script to send the command to the drone garage.

    # You can enter the strings:
    # "start charging" - starts charging the drone
    # "stop charging" - stops the drone from charging
    # "turn controller on" - turns on power for the controller
    # "turn controller off" - turns off power for the controller

    # If the message is not received the script will send the error:
    # [WinError 10061] No connection could be made because the target machine actively refused it
    #Connection closed
    # and if the entered string is unknown to the program it will send the error:
    # "no valid command to send"
    user_input = "end program"  # Replace with desired string


    # Determine the command to send based on the input string
    if user_input == "start charging":
        command_to_send = 1  # Example: 1 for start
    elif user_input == "stop charging":
        command_to_send = 2  # Example: 2 for stop
    elif user_input == "turn controller on":
        command_to_send = 3 #
    elif user_input == "turn controller off":
        command_to_send = 4 #
    elif user_input == "special task":
        command_to_send = 9  # Example: 9 for special task
    elif user_input == "end program":
        command_to_send = 99 # Stops program
    elif user_input == "nothing":
        command_to_send = 0  # Example: 0 for do nothing
    else:
        print(f"Unknown command string: {user_input}")
        command_to_send = None  # No command to send

    # Send the command if it's valid
    if command_to_send is not None:
        send_command(command_to_send)
    else:
        print("No valid command to send.")
