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


def test_touch():
    # print("Press the touch sensor to change the LED color!")
    while touch.is_pressed:
        leds.set_color("LEFT", "RED")
        leds.set_color("RIGHT", "RED")

    leds.set_color("LEFT", "GREEN")
    leds.set_color("RIGHT", "GREEN")


def dump_gyro():
    max_rate = 0
    while not touch.is_pressed:
        angle, rate = gyro.angle_and_rate
        max_rate = max(max_rate, rate)
        print('%s, %s, %s' % (angle, rate, max_rate))


def constraint_to_unit(v):
    return max(min(v, 1.0), -1.0)


def reset_gyro():
    if gyro.mode == 'GYRO-RATE':
        gyro.mode = 'GYRO-ANG'
        gyro.mode = 'GYRO-RATE'
    else:
        mode = gyro.mode
        gyro.mode = 'GYRO-RATE'
        gyro.mode = mode


def balance(k_p=1.0, k_i=0.0, k_d=0.0, baseline=1.0):
    reset_gyro()
    max_theta = 30
    # A basic drop test shows a max rate of about 493
    max_rate = 500
    integrated_error = 0.0
    theta, rate = gyro.angle_and_rate
    while abs(theta) <= max_theta:
        error = constraint_to_unit((theta - baseline) / max_theta)
        rate_error = constraint_to_unit(rate / max_rate)
        pid = k_p * error + k_i * integrated_error + k_d * rate_error
        speedpct = 100.0 * constraint_to_unit(pid)
        print('theta=%s, rate=%s, error=%s, rate_error=%s, pid=%s, speedpct=%s' %
              (theta, rate, error, rate_error, pid, speedpct))
        if pid != 0:
            speed = SpeedPercent(speedpct)
            tank_drive.on(speed, speed)
        else:
            tank_drive.off()
        theta, rate = gyro.angle_and_rate
    tank_drive.off()

# balance(k_p=5.0, k_i=0.0, k_d=0.0)
# balance(k_p=4.0, k_i=0.0, k_d=0.0)
# balance(k_p=2.9, k_i=0.0, k_d=0.1, baseline=3.0)
