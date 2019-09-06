#!/usr/bin/env python3

# https://github.com/ev3dev/ev3dev-lang-python
# https://github.com/ev3dev/ev3dev-lang-python-demo#balanc3r

from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor, GyroSensor, UltrasonicSensor
from ev3dev2.led import Leds
from ev3dev2.sound import Sound

import math
import time

# Motors
l_motor = LargeMotor(OUTPUT_D)
r_motor = LargeMotor(OUTPUT_A)

# Sensors
color = ColorSensor(INPUT_1)
gyro = GyroSensor(INPUT_2)
ts = TouchSensor(INPUT_3)
us = UltrasonicSensor(INPUT_4)

# Sound
sound = Sound()

# sound.speak('Welcome to the E V 3 dev project!')


def forward(speed):
    l_motor.run_forever(speed_sp=speed)
    r_motor.run_forever(speed_sp=speed)


def stop():
    l_motor.stop(stop_action="hold")
    r_motor.stop(stop_action="hold")


def reset_gyro():
    if gyro.mode == gyro.MODE_GYRO_CAL:
        gyro.mode = gyro.MODE_GYRO_G_A
        gyro.mode = gyro.MODE_GYRO_CAL
    else:
        mode = gyro.mode
        gyro.mode = gyro.MODE_GYRO_CAL
        gyro.mode = mode


# tires are 56mm diameter
def balance(target_angle=0, k_p=20, k_i=0, k_d=0):
    integrated_error = 0
    t_old = time.time()
    reset_gyro()
    angle = gyro.angle
    while abs(angle) < 60:
        t_new = time.time()
        dt = t_new - t_old
        t_old = t_new
        angle, rate = gyro.rate_and_angle
        error = angle - target_angle
        integrated_error = integrated_error + error * dt
        pid = k_p * error + k_i * integrated_error + k_d * rate
        print(t_new, angle, integrated_error, rate, pid)
        forward(min(max(pid, -1050), 1050))
    stop()


def balance_rate(target_rate=0, k_p=20, k_i=0, k_d=0):
    integrated_error = 0
    t_old = time.time()
    reset_gyro()
    angle, rate = gyro.rate_and_angle
    while abs(rate) < 3000:
        t_new = time.time()
        dt = t_new - t_old
        t_old = t_new
        angle, rate = gyro.rate_and_angle
        error = rate - target_rate
        integrated_error = integrated_error + error * dt
        pid = k_p * error + k_i * integrated_error + k_d * rate
        print(t_new, angle, integrated_error, rate, pid)
        forward(min(max(pid, -1050), 1050))
    stop()
