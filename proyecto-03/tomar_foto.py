import cv2
import time
import RPi.GPIO as GPIO
from PIL import Image

# ------------ CONFIG GPIO ------------
BUTTON_PIN = 27  # <--- AHORA GPIO27

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ------------ CONFIG CÁMARA ------------
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

print("Sistema listo en GPIO27. Pulsa el botón para tomar foto.")

# ------------ LOOP ------------
while True:
    if GPIO.input(BUTTON_PIN) == 0:  # LOW = botón presionado
        print("Botón detectado → tomando foto...")

        # limpiar buffer viejo de la camara
        for _ in range(6):
            cap.read()

        ok, bgr = cap.read()
        if ok:
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            Image.fromarray(rgb).save("foto_rgb.png")
            print("Foto guardada: foto_rgb.png")
        else:
            print("Error leyendo la cámara")

        time.sleep(0.4)  # anti-rebote
