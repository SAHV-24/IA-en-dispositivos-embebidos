import cv2
import time
import RPi.GPIO as GPIO
from PIL import Image
from gpiozero import AngularServo
import numpy as np
from edge_impulse_linux.tflite_runtime import Interpreter

# ------------ CONFIGURACIÓN BOTÓN (PULL-DOWN) ------------
BUTTON_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# ------------ CONFIG SERVOS ------------
servo = AngularServo(
    18,
    min_angle=0, max_angle=180,
    min_pulse_width=0.0005,
    max_pulse_width=0.0025
)

servo2 = AngularServo(
    23,
    min_angle=0, max_angle=270,
    min_pulse_width=0.0005,
    max_pulse_width=0.0025
)

# Posiciones útiles
POS_A = 0
POS_B = 90
POS_C = 180

# ------------ CONFIG TFLITE (EDGE IMPULSE .tflite) ------------
MODEL_PATH = "model.tflite"  # tu archivo convertido a .tflite

interpreter = Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

IMG_HEIGHT = input_details[0]['shape'][1]
IMG_WIDTH = input_details[0]['shape'][2]

print("Modelo cargado correctamente.")
print(f"Input shape: {IMG_WIDTH}x{IMG_HEIGHT}")

# ------------ FUNCIONES SERVO ------------
def mover_servo1(angulo):
    if 0 <= angulo <= 180:
        servo.angle = angulo
        print(f"Servo 1 → {angulo}°")

def mover_servo2(angulo):
    if 0 <= angulo <= 270:
        servo2.angle = angulo
        print(f"Servo 2 → {angulo}°")

# ------------ CONFIG CÁMARA ------------
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

print("Listo. Presiona el botón para tomar foto + inferencia + mover servos.")

# ------------ LOOP PRINCIPAL ------------
while True:
    if GPIO.input(BUTTON_PIN) == 1:

        print("\nBotón presionado → capturando foto...")

        # Tomar foto
        ok, bgr = cap.read()
        if not ok:
            print("ERROR capturando imagen")
            continue

        # Convertir RGB + guardar
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        Image.fromarray(rgb).save("photo.png")
        print("Imagen guardada: photo.png")

        # ------------ PREPARAR IMAGEN PARA TFLITE ------------
        img_resized = cv2.resize(rgb, (IMG_WIDTH, IMG_HEIGHT))

        if input_details[0]['dtype'] == np.float32:
            input_data = np.expand_dims(img_resized.astype(np.float32) / 255.0, axis=0)
        else:
            input_data = np.expand_dims(img_resized.astype(np.uint8), axis=0)

        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        output_data = interpreter.get_tensor(output_details[0]['index'])[0]

        predicted_class = int(np.argmax(output_data))
        confidence = float(output_data[predicted_class])

        print(f"Clase predicha: {predicted_class}  | Confianza: {confidence:.2f}")
        print("Vectores de salida:", output_data)

        # ------------ CONTROL DE SERVOS SEGÚN LA CLASE ------------
        if predicted_class in [0, 1]:
            mover_servo1(0)
            mover_servo2(0)

        elif predicted_class in [2, 3]:
            mover_servo1(90)
            mover_servo2(135)

        else:
            mover_servo1(180)
            mover_servo2(270)

        time.sleep(0.4)
