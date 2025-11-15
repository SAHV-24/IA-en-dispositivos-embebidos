from gpiozero import AngularServo
from time import sleep

servo =AngularServo(18, min_angle=0, max_angle=270, min_pulse_width=0.0005, max_pulse_width=0.0025)

angulo = 0


while (True):
    
    servo.angle = 0
    sleep(3)
    
    servo.angle =  90
    sleep(3)

    servo.angle = 180
    sleep(3)

    servo.angle = 270
    sleep(3)
    
