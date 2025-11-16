import cv2
import time
import RPi.GPIO as GPIO
from PIL import Image
from gpiozero import AngularServo
import numpy as np
import tensorflow as tf

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

# ------------ CONFIG SERVO 2 ------------
servo2 = AngularServo(
    23,
    min_angle=0,
    max_angle=270,
    min_pulse_width=0.0005,
    max_pulse_width=0.0025
)


# ------------ CONFIG TENSORFLOW LITE ------------
MODEL_PATH = "project_model.tflite"
interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print(f"Modelo cargado: {MODEL_PATH}")
print(f"Input shape: {input_details[0]['shape']}")
print(f"Output shape: {output_details[0]['shape']}")

# ------------ CLASES DEL MODELO ------------
CLASS_NAMES = ['Beetroot', 'Cauliflower', 'Orange', 'Pear', 'Pineapple', 'Watermelon']

# ------------ FUNCIONES PARA MOVER SERVOS ------------
def mover_servo1(angulo):
    """Mueve el servo 1 al ángulo especificado (0-180)"""
    if 0 <= angulo <= 270:
        servo.angle = angulo
        print(f"Servo 1 movido a {angulo}°")
    else:
        print(f"Ángulo fuera de rango para servo 1: {angulo}")

def mover_servo2(angulo):
    """Mueve el servo 2 al ángulo especificado (0-270)"""
    if 0 <= angulo <= 270:
        servo2.angle = angulo
        print(f"Servo 2 movido a {angulo}°")
    else:
        print(f"Ángulo fuera de rango para servo 2: {angulo}")

# ------------ CONFIG CÁMARA ------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERROR: No se puede abrir la cámara")
    print("Verifica que la cámara esté conectada y habilitada con 'sudo raspi-config'")
    exit(1)

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

print("Cámara inicializada correctamente")
print("Listo. Presiona el botón para mover servo + tomar foto + verificar RGB.")

mover_servo1(0)
mover_servo2(0)
# ------------ LOOP PRINCIPAL ------------
while True:
    if GPIO.input(BUTTON_PIN) == 1:  # presionado
        
        print("Button Pushed")
        
        ok,bgr = cap.read() 
        
        # Take picture
        if not ok:
            print("ERROR While trying to capture")
            continue
        
        # Convert to RGB
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        Image.fromarray(rgb).save("photo.png")
        print("Saved image photo.png")

        
        print("Starting Inference")
        
        # Preparar imagen para inferencia
        input_shape = input_details[0]['shape']
        img_height, img_width = input_shape[1], input_shape[2]
        
        # Redimensionar imagen
        img_resized = cv2.resize(rgb, (img_width, img_height))
        
        # Normalizar según el tipo de entrada del modelo
        if input_details[0]['dtype'] == np.float32:
            input_data = np.expand_dims(img_resized.astype(np.float32) / 255.0, axis=0)
        else:
            input_data = np.expand_dims(img_resized, axis=0)
        
        # Realizar inferencia
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        
        # Obtener resultados
        output_data = interpreter.get_tensor(output_details[0]['index'])
        predicted_class = np.argmax(output_data[0])
        confidence = output_data[0][predicted_class]
        predicted_name = CLASS_NAMES[predicted_class]
        
        print(f"Clase predicha: {predicted_name} (índice {predicted_class}), Confianza: {confidence:.2f}")
        print(f"Salidas completas: {output_data[0]}")
        
        # Ejemplo de uso de los servos basado en la predicción
        if predicted_class in [0,1]:
            mover_servo1(0)
            mover_servo2(0)
        elif predicted_class in [2,3]:
            mover_servo1(200)
            mover_servo2(0)
        else:
            mover_servo1(0)
            mover_servo2(200)
        
        time.sleep(0.5)  # Debounce
        