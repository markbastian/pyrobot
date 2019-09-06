#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor, UltrasonicSensor, GyroSensor
from ev3dev2.led import Leds
from ev3dev2.sound import Sound

# Universal
sound = Sound()
leds = Leds()

# This is the standard balancebot config
# Outputs
left_motor = LargeMotor(OUTPUT_A)
right_motor = LargeMotor(OUTPUT_D)
tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)
medium_motor = MediumMotor(OUTPUT_C)

# Inputs
color = ColorSensor(INPUT_1)
gyro = GyroSensor(INPUT_2)
touch = TouchSensor(INPUT_3)
us = UltrasonicSensor(INPUT_4)


def speak(words):
    sound.speak(words)


print("Press the touch sensor to change the LED color!")


def test_touch():
    while touch.is_pressed:
        leds.set_color("LEFT", "RED")
        leds.set_color("RIGHT", "RED")

    leds.set_color("LEFT", "GREEN")
    leds.set_color("RIGHT", "GREEN")


def dump_gyro():
    while not touch.is_pressed:
        print(gyro.angle)


def balance():
    while not touch.is_pressed:
        a = gyro.angle / 90.0
        if a != 0:
            speed = SpeedPercent(100.0 * a)
            tank_drive.on(speed, speed)
        else:
            tank_drive.off()

    tank_drive.off()
