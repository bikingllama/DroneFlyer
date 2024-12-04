
import numpy as np









# Values for resistor linear interpolation
ResIntAB = {
    1: 7451,  #LHorA
    2: 421,   #LHorB
    3: 8530, #LHorAB
    4: 8306, #LVerA
    5: 242, #LVerB
    6: 8410, #RVerAB
    
    ## Guessed values
    7: 7451, # RHorA
    8: 421, #RHorB
    9: 8530, #RHorAB
    10: 8306, #RVerA
    11: 242, #RVerB
    12: 8410, #RVerAB
}


def ByteBuilder(Dir, JoyPos):
    
    # Dir: 1 = LHor, 2 = LVer, 3=RHor, 4=RVer
    # JoyPos is the corresponding position of the joystick between -1 and 1.

    # Finds voltage
    Voltage = interpolate_voltage(Dir, JoyPos)

    print(f"Interpolated voltage is {Voltage}")

    # Finds needed resistance; RWB/RAB*3.56V = V;    RWB = V/3.56V*RAB
    RAB = ResIntAB[3*(Dir-1)+3]
    Res = (Voltage/3.3)*RAB


    # Finds corresponding N-value:
    # R = A/256*x+B   (x=N)
    # N = (R-B)*256/A
    AVal = ResIntAB[(Dir-1)*3+1]
    BVal = ResIntAB[(Dir-1)*3+2]

    N = int(np.floor((Res-BVal)*256/AVal))


    # Checks if value for N is within range (0-255)
    if (N > 255 or N < 0):
        print("Error! Value for resistance is out of range at N = " + str(N))
        if N > 255:
            N = 255
        if N < 0:
            N = 0
    

    # Initializes double byte
    InitB = 0x8000

    # Defines that it needs to write
    CommandB = 0x00

    # Defines which wiper to write to
    if Dir in [1,3]:
        AxisB = 0b00000000
    else:
        AxisB = 0b00010000


    # Assembles byte
    Byte = InitB | CommandB | AxisB | N

    # Sets bit 16 and 9 to zero
    Byte = Byte & 0x7EFF
    
    # Splits byte into two eights
    Byte1 = Byte >> 8
    Byte2 = Byte & 0b11111111
    
    return Byte1, Byte2



def interpolate_voltage(Dir, pos):
    
    # Dir: 1 = LHor, 2 = LVer, 3=RHor, 4=RVer
    # pos: position of joystick between -1 and 1
    
    # Initialize interpolated voltage
    IntV = 0
    
    # Normalize position from -1 to 1 to 0 to 1
    pos = (pos + 1)/2
    
    # Interpolations for pos <=0.5 giving highest voltage: VTop + 2*(VCenter - Vtop) * pos
    # For pos >0.5 giving lowest voltage: VCenter + 2*(VBottom - VCenter) * (pos.0.5)
    # For horizontal, top=left, bottom = min

    # Horizontal position (0 = left, 1 = right)
    # Vertical position (0 = top, 1 = bottom)

    # Interpolates in two ranges to ensure center value

    # LHor
    if Dir == 1:
        if pos <= 0.5:
            IntV = 2.797 + 2*(1.774 - 2.797)*pos
        else:
            IntV = 1.774 + 2*(0.914 - 1.774)*(pos-0.5)
    
    # LVer
    if Dir  == 2:
        if pos <= 0.5:
            IntV = 1.764 + 2*(0.719 - 1.764)*pos
        else:
            IntV = 2.802 + 2*(1.764 - 2.802)*(pos-0.5)
    
    # RHor
    if Dir == 3:
        if pos <=0.5:
            IntV = 2.77 + 2*(1.775 - 2.77)*(pos)
        else:
            IntV = 1.775 + 2*(0.737 - 1.775)*(pos-0.5)

    # RVer
    if Dir == 4:
        if pos <=0.5:
            IntV = 2.692 + 2*(1.761 - 2.692)*pos
        else:
            IntV = 1.761 + 2*(0.934 - 1.761)*(pos-0.5)

    if IntV == 0:
        print(f"Error! Interpolation returned 0!. Inputs were Dir = {Dir} and pos = {pos}. Returning center-ish value instead.")
        IntV = 1.64
    
    return IntV


print(ByteBuilder(1,0.2))