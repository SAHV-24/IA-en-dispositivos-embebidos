import RPi.GPIO as GPIO
import time

SERVO_PIN = 18  # GPIO físico donde conectas el servo

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# PWM a 50Hz (frecuencia estándar para servo)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def set_angle(angle):
    """Mueve un servo entre 0 y 180 grados."""
    duty = 2 + (angle / 18)   # fórmula estándar
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.4)
    pwm.ChangeDutyCycle(0)    # para que no tiemble

print("Listo. Escribe un ángulo 0–180. 'q' para salir.")

while True:
    cmd = input("> ")

    if cmd == "q":
        break

    try:
        angle = int(cmd)
        if 0 <= angle <= 180:
            set_angle(angle)
            print(f"Servo movido a {angle}°")
        else:
            print("Ángulo inválido (0–180).")
    except ValueError:
        print("Escribe un número válido.")

pwm.stop()
GPIO.cleanup()
