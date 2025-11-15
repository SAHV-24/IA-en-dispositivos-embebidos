import cv2
import time
import RPi.GPIO as GPIO
from PIL import Image

# ------------ CONFIG GPIO ------------
BUTTON_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ------------ CONFIG CÁMARA ------------
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

print("Listo. Presiona el botón físico para tomar foto.")

# ------------ LOOP ------------
while True:
    # Botón presionado → GPIO17 pasa a LOW
    if GPIO.input(BUTTON_PIN) == 0:
        print("Botón detectado → tomando foto...")

        # Limpia frames viejos (logitech deja frames en buffer)
        for _ in range(6):
            cap.read()

        ret, bgr = cap.read()
        if ret:
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            Image.fromarray(rgb).save("foto_rgb.png")
            print("Foto guardada como foto_rgb.png")
        else:
            print("Error leyendo la cámara")

        time.sleep(0.4)  # Anti-rebote

