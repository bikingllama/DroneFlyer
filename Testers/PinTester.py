import RPi.GPIO as GPIO
import time

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

pin =34 



GPIO.setup(pin,GPIO.OUT)
try:
	print(f"activating pin {pin}...")
	GPIO.output(pin,GPIO.HIGH)
	time.sleep(5)
	print(f"deactivating pin {pin}...")
finally:
	GPIO.cleanup()
