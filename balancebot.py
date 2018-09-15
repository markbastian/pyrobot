#!/usr/bin/env python3
import ev3dev.ev3 as ev3
import math
import time

l_motor = ev3.LargeMotor('outD')
r_motor = ev3.LargeMotor('outA')

# Sensors
color = ev3.ColorSensor('in1')
gyro = ev3.GyroSensor('in2')
ts = ev3.TouchSensor('in3')
us = ev3.UltrasonicSensor('in4')


def forward(speed):
    l_motor.run_forever(speed_sp=speed)
    r_motor.run_forever(speed_sp=speed)


def stop():
    l_motor.stop(stop_action="hold")
    r_motor.stop(stop_action="hold")


def reset_gyro():
    if gyro.mode == 'GYRO-RATE':
        gyro.mode = 'GYRO-ANG'
        gyro.mode = 'GYRO-RATE'
    else:
        mode = gyro.mode
        gyro.mode = 'GYRO-RATE'
        gyro.mode = mode


# tires are 56mm diameter
def balance(target_angle=0, k_p=20, k_i=0, k_d=0):
    integrated_error = 0
    t_old = time.time()
    reset_gyro()
    angle = gyro.angle
    while abs(angle) < 30:
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
