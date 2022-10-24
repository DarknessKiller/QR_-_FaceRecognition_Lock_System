from gpiozero import Servo

from gpiozero.pins.pigpio import PiGPIOFactory

factory = PiGPIOFactory()

servo = Servo(15, min_pulse_width=0.45/1000, max_pulse_width=2.4/1000, pin_factory=factory)
servo.max()

while True:
    servoV = int(input("Enter 1 or 0 to change between lock and unlock"))
    if servoV == 1:
        servo.max()
    elif servoV == 0:
        servo.mid()
    else:
        break