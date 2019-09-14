#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor, UltrasonicSensor, GyroSensor
from ev3dev2.led import Leds
from ev3dev2.sound import Sound
from timeit import default_timer as timer
import csv

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


# balance(k_p=1.2, k_i=16.0, k_d=0.0, cum_error=-0.25)
# Working around this, am I even close?
# balance(k_p=1.0, k_i=0.5, k_d=0.01, cum_error=0.0, max_theta=45)
# balance(k_p=0.5, k_i=1.0, k_d=0.01, cum_error=0.0, max_theta=45) - doesn't freak out very much
# Oscillates a little bit
# balance(k_p=0.8, k_i=0.0, k_d=0.01, cum_error=0.0, max_theta=45)
def balance(k_p=1.2, k_i=16.0, k_d=0.02, cum_error=-0.25, max_theta=45):
    reset_gyro()
    integrated_error = 0.0
    t = timer()
    theta, rate = gyro.angle_and_rate
    d_rate = 0.0
    recording = False
    with open('P{}_I{}_D{}.csv'.format(k_p, k_i, k_d), 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['t', 'angle', 'rate', 'd_rate', 'i_rate', 'P', 'I', 'D', 'pid', 'speedpct'])
        while abs(theta) <= max_theta:
            error = rate
            rate_error = d_rate
            integrated_error = cum_error
            P = k_p * error
            I = k_i * integrated_error
            D = k_d * rate_error
            pid = P + I + D
            speedpct = max(min(pid, 100.0), -100.0)
            if rate_error != 0:
                recording = True
            if recording:
                writer.writerow([t, theta, rate, rate_error, integrated_error, P, I, D, pid, speedpct])
            # print('theta=%s, rate=%s, error=%s, rate_error=%s, pid=%s, speedpct=%s' %
            #       (theta, rate, error, rate_error, pid, speedpct))
            print('theta=%s, rate=%s, error=%s, rate_error=%s, cum_error=%s, pid=%s, speedpct=%s' %
                  (theta, rate, error, rate_error, integrated_error, pid, speedpct))
            if speedpct != 0:
                speed = SpeedPercent(speedpct)
                tank_drive.on(speed, speed)
            else:
                tank_drive.off()
            t_old = t
            rate_old = rate
            t = timer()
            dt = t - t_old
            theta, rate = gyro.angle_and_rate
            d_rate = (rate - rate_old) / dt
            cum_error += rate * dt
        tank_drive.off()

# def balance_j():
#     reset_gyro()
#     max_theta = 30
#     t = timer()
#     mPos = 0
#     loop_count = 0
#     ready = False
#     theta, rate = gyro.angle_and_rate
#     cum_error = -0.25
#     m = [0, 0, 0, 0]
#     while abs(theta) <= max_theta:
#         t_old = t
#         t = timer()
#         dt = t - t_old
#         theta, rate = gyro.angle_and_rate
#         cum_error = cum_error + rate * dt
#         curr_speed = left_motor.speed + right_motor.speed - m[0]
#         m = ([curr_speed] + m)[:4]
#         print(m)
#         mSpd = sum(m) / 4.0 / dt
#         pwr = 0.08 * mSpd + 0.12 * m[0] + 0.8 * rate + 15 * cum_error
#         pwr = min(max(pwr, -100), 100)
#         if ready:
#             s = SpeedPercent(pwr)
#             tank_drive.on(s, s)
#         loop_count += 1
#         if loop_count == 10:
#             ready = True
#     tank_drive.off()

# def angle_balance(k_p=1.0, k_i=0.0, k_d=0.0, baseline=1.0):
#     reset_gyro()
#     max_theta = 30
#     # A basic drop test shows a max rate of about 493
#     max_rate = 500
#     integrated_error = 0.0
#     theta, rate = gyro.angle_and_rate
#     while abs(theta) <= max_theta:
#         error = constraint_to_unit((theta - baseline) / max_theta)
#         rate_error = constraint_to_unit(rate / max_rate)
#         pid = k_p * error + k_i * integrated_error + k_d * rate_error
#         speedpct = 100.0 * constraint_to_unit(pid)
#         print('theta=%s, rate=%s, error=%s, rate_error=%s, pid=%s, speedpct=%s' %
#               (theta, rate, error, rate_error, pid, speedpct))
#         if pid != 0:
#             speed = SpeedPercent(speedpct)
#             tank_drive.on(speed, speed)
#         else:
#             tank_drive.off()
#         theta, rate = gyro.angle_and_rate
#     tank_drive.off()

# balance(k_p=5.0, k_i=0.0, k_d=0.0)
# balance(k_p=4.0, k_i=0.0, k_d=0.0)
# balance(k_p=2.9, k_i=0.0, k_d=0.1, baseline=3.0)
