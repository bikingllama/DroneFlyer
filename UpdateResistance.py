
# import spidev
import numpy as np

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
    N = (np.floor((Value-75)*256/10000)).astype(int)

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

    '''
    Sends output
    try
        comm = spi.open(0,Stick)
        comm.bits_per_word = 16
        comm.max_speed_hz = 10*10^6
        comm.writebytes(Byte)
        spi.close

    '''
    print(N)
    print("{:016b}".format(Byte))
    print("\n\n\n\n")


UpdateResistance(1,1,0,1500)

UpdateResistance(0,1,1,12000)
