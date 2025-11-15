import cv2
import time
import RPi.GPIO as GPIO
from PIL import Image
from gpiozero import AngularServo

# ------------ CONFIGURACIÓN BOTÓN (PULL-DOWN) ------------
BUTTON_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Pull-down

# ------------ CONFIG SERV0 ------------
servo = AngularServo(
    18,
    min_angle=0,
    max_angle=180,
    min_pulse_width=0.0005,
    max_pulse_width=0.0025
)

# Posiciones útiles para clasificador
POS_A = 0     # izquierda
POS_B = 90    # centro
POS_C = 180   # derecha

# ------------ CONFIG CÁMARA ------------
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

print("Listo. Presiona el botón para mover servo + tomar foto + verificar RGB.")

# ------------ LOOP PRINCIPAL ------------
while True:
    if GPIO.input(BUTTON_PIN) == 1:  # presionado
        print("\n\n--- Botón detectado ---")

        # 1. Mover a posición inicial
        print("Servo → Posición A (0°)")
        servo.angle = POS_A
        time.sleep(1)

        # 2. Limpiar buffer cámara
        for _ in range(6):
            cap.read()

        # 3. Capturar foto
        ok, bgr = cap.read()
        if not ok:
            print("Error capturando imagen.")
            continue

        # 4. Convertir a RGB
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        Image.fromarray(rgb).save("foto_rgb.png")
        print("Foto guardada como foto_rgb.png")

        # 5. Mostrar ejemplo de pixel
        print("Pixel RGB (0,0):", rgb[0][0])

        # 6. Mover servo a segunda posición
        print("Servo → Posición B (90°)")
        servo.angle = POS_B
        time.sleep(1)

        # 7. Mover servo a tercera posición
        print("Servo → Posición C (180°)")
        servo.angle = POS_C
        time.sleep(1)

        # Anti-rebote
        time.sleep(0.5)
