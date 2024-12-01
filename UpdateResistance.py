
import spidev
import numpy as np
import RPi.GPIO as GPIO
import time

# Define stick CS's
CSL = 31
CSR = 29

# Set CS as output and initilazise
GPIO.setmode(GPIO.BOARD)
GPIO.setup(CSL, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(CSR, GPIO.OUT, initial=GPIO.HIGH)

# Setup SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 10**6


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
    #N = int(np.floor((Value-75)*256/10000))
    N=0

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
    #try:
    print("First byte is {:08b} & second byte is {:08b}".format(Byte1, Byte2))
    GPIO.output(31, GPIO.LOW)
    Response = spi.xfer2([Byte1, Byte2])    # Send 2-byte SPI command
    GPIO.output(31, GPIO.HIGH)
    time.sleep(0.01)
    #except Exception as Excp:
    #print("Exception when sending:\n")
    #print(Excp)
    print("Outputpin is {}".format(CurrOutPin))
        
    # Prints response
    if Response != 0b1:
        print("Recieved response:\n")
        print(Response)

    # Sets both to be high to be sure
    GPIO.output(CSL, GPIO.HIGH)
    GPIO.output(CSR, GPIO.HIGH)
    
    
    print(N)
    print("{:016b}".format(Byte))
    print("\n\n\n\n")






UpdateResistance(0,0,0,5000)

#UpdateResistance(1,1,0,1500)

#UpdateResistance(0,1,1,12000)

# Updatetester
