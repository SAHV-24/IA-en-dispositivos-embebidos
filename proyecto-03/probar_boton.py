import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)  # usar numeración BCM
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # pull-down

print("Probando botón en GPIO 27 (PULL-DOWN).")
print("Suelta = 0 | Presiona = 1")

try:
    while True:
        print(GPIO.input(27))
        time.sleep(0.2)
except KeyboardInterrupt:
    GPIO.cleanup()
