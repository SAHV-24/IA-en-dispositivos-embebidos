import cv2
from PIL import Image

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Listo. Escribe 'f' para tomar foto, 'q' para salir.")

while True:
    cmd = input("> ").strip().lower()

    if cmd == "f":
        print("Tomando foto...")

        # limpiar buffer
        for _ in range(5):
            cap.read()

        ok, bgr = cap.read()
        if not ok:
            print("Error capturando.")
            continue

        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        Image.fromarray(rgb).save("foto_rgb.png")

        print("Foto guardada: foto_rgb.png")

    elif cmd == "q":
        print("Saliendo...")
        break

cap.release()

