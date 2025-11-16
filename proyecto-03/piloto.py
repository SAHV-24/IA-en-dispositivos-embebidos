import cv2
import time
import RPi.GPIO as GPIO
from PIL import Image
from gpiozero import AngularServo
import numpy as np
from edge_impulse_linux.runner import ImpulseRunner

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

# Posiciones útiles para clasificador
POS_A = 0     # izquierda
POS_B = 90    # centro
POS_C = 180   # derecha

# ------------ CONFIG EDGE IMPULSE ------------
MODEL_PATH = "modelfile.eim"  # Cambia al nombre de tu modelo .eim

print(f"Cargando modelo Edge Impulse: {MODEL_PATH}")

with ImpulseRunner(MODEL_PATH) as runner:
    try:
        model_info = runner.init()
        print(f"Modelo cargado: {model_info['project']['name']}")
        print(f"Input shape: {model_info['model_parameters']['image_input_width']}x{model_info['model_parameters']['image_input_height']}")
        print(f"Labels: {model_info['model_parameters']['labels']}")
        
        IMG_WIDTH = model_info['model_parameters']['image_input_width']
        IMG_HEIGHT = model_info['model_parameters']['image_input_height']
        LABELS = model_info['model_parameters']['labels']
        
    except Exception as e:
        print(f"Error al cargar modelo: {e}")
        exit(1)

# ------------ FUNCIONES PARA MOVER SERVOS ------------
def mover_servo1(angulo):
    """Mueve el servo 1 al ángulo especificado (0-180)"""
    if 0 <= angulo <= 180:
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
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

print("Listo. Presiona el botón para mover servo + tomar foto + verificar RGB.")

# ------------ LOOP PRINCIPAL ------------
with ImpulseRunner(MODEL_PATH) as runner:
    try:
        model_info = runner.init()
        print(f"Modelo cargado: {model_info['project']['name']}")
        
        while True:
            if GPIO.input(BUTTON_PIN) == 1:  # presionado
                
                print("Button Pushed")
                
                ok, bgr = cap.read() 
                
                # Take picture
                if not ok:
                    print("ERROR While trying to capture")
                    continue
                
                # Convert to RGB
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                Image.fromarray(rgb).save("photo.png")
                print("Saved image photo.png")

                
                print("Starting Inference")
                
                # Redimensionar imagen al tamaño esperado por el modelo
                img_resized = cv2.resize(rgb, (IMG_WIDTH, IMG_HEIGHT))
                
                # Convertir a formato de características para Edge Impulse
                features = []
                for pixel in img_resized.flatten():
                    features.append(pixel)
                
                # Realizar inferencia
                res = runner.classify(features)
                
                if "result" in res:
                    print("Resultados de clasificación:")
                    for label, score in res["result"]["classification"].items():
                        print(f"  {label}: {score:.2f}")
                    
                    # Obtener la clase con mayor confianza
                    predictions = res["result"]["classification"]
                    predicted_label = max(predictions, key=predictions.get)
                    confidence = predictions[predicted_label]
                    
                    print(f"\nClase predicha: {predicted_label}, Confianza: {confidence:.2f}")
                    
                    # Obtener el índice de la clase predicha
                    predicted_class = LABELS.index(predicted_label)
                    
                    # Ejemplo de uso de los servos basado en la predicción
                    if predicted_class in [0, 1]:
                        mover_servo1(0)
                        mover_servo2(0)
                    elif predicted_class in [2, 3]:
                        mover_servo1(90)
                        mover_servo2(135)
                    else:
                        mover_servo1(180)
                        mover_servo2(270)
                
                time.sleep(0.5)  # Debounce
                
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario")
    finally:
        cap.release()
        GPIO.cleanup()
        