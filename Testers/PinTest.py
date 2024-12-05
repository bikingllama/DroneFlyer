
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(36, GPIO.OUT, initial=GPIO.LOW)

time.sleep(0.1)

GPIO.output(36, GPIO.LOW)


