import cv2
import time
import RPi.GPIO as GPIO
from PIL import Image
from gpiozero import AngularServo
import numpy as np
import tensorflow as tf

# ------------ CONFIGURACIÓN BOTÓN (PULL-DOWN) ------------
BUTTON_PIN = 27

# ------------ CONFIGURACIÓN MOTOR REDUCTOR ------------
MOTOR_PIN = 17  # Pin GPIO para el motor reductor

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Pull-down
GPIO.setup(MOTOR_PIN, GPIO.OUT)
GPIO.output(MOTOR_PIN, GPIO.LOW)  # Motor apagado al inicio

# ------------ CONFIG SERV0 ------------
servo = AngularServo(
    18,
    min_angle=0,
    max_angle=270,
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

def activar_motor_reductor(segundos=5):
    """Activa el motor reductor por el tiempo especificado"""
    print(f"Activando motor reductor por {segundos} segundos...")
    GPIO.output(MOTOR_PIN, GPIO.HIGH)
    time.sleep(segundos)
    GPIO.output(MOTOR_PIN, GPIO.LOW)
    print("Motor reductor detenido")

def resetear_servos():
    """Regresa los servos a posición cero"""
    print("Regresando servos a posición inicial...")
    mover_servo1(0)
    mover_servo2(0)

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
last_button_time = 0
DEBOUNCE_TIME = 1.5  # Tiempo mínimo entre capturas

while True:
    if GPIO.input(BUTTON_PIN) == 1:  # presionado
        
        current_time = time.time()
        if current_time - last_button_time < DEBOUNCE_TIME:
            continue  # Ignorar si fue presionado muy recientemente
        
        last_button_time = current_time
        print("Button Pushed")

        # ---- FLUSH REAL DEL BUFFER ----
        print("Limpiando buffer de cámara...")
        for _ in range(10):
            cap.grab()   # Avanza el frame sin decodificar

        # ---- AHORA SÍ TOMAMOS IMAGEN NUEVA ----
        ok, bgr = cap.read()
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

        img_resized = cv2.resize(rgb, (img_width, img_height))

        # Normalización
        if input_details[0]['dtype'] == np.float32:
            input_data = np.expand_dims(img_resized.astype(np.float32) / 255.0, axis=0)
        else:
            input_data = np.expand_dims(img_resized, axis=0)

        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        output_data = interpreter.get_tensor(output_details[0]['index'])
        predicted_class = np.argmax(output_data[0])
        confidence = output_data[0][predicted_class]
        predicted_name = CLASS_NAMES[predicted_class]

        print(f"Clase predicha: {predicted_name} (índice {predicted_class}), Confianza: {confidence:.2f}")
        print(f"Salidas completas: {output_data[0]}")

        # Paso 1: Movimiento de servos según clase
        print("\n--- Paso 1: Moviendo servos ---")
        if predicted_class in [0,1]:
            mover_servo1(0)
            mover_servo2(0)
        elif predicted_class in [2,3]:
            mover_servo1(200)
            mover_servo2(0)
        else:
            mover_servo1(0)
            mover_servo2(200)

        time.sleep(1)  # Esperar a que los servos se posicionen
        
        # Paso 2: Activar motor reductor por 5 segundos
        print("\n--- Paso 2: Activando motor reductor ---")
        activar_motor_reductor(5)
        
        # Paso 3: Resetear servos a cero
        print("\n--- Paso 3: Reseteando servos ---")
        resetear_servos()
        
        # Esperar a que el usuario suelte el botón
        while GPIO.input(BUTTON_PIN) == 1:
            time.sleep(0.1)
        
        print("\nListo para siguiente captura\n")
        print("="*50)
