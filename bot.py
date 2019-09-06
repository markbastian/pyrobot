#!/usr/bin/env python3
import ev3dev.ev3 as ev3
import math
import time
import random

# https://sites.google.com/site/ev3python/learn_ev3_python/using-motors

l_motor = ev3.LargeMotor('outB')
r_motor = ev3.LargeMotor('outC')
# m_motor = ev3.MediumMotor('outA')

# Sensors
# ts = ev3.TouchSensor('in1')
gyro = ev3.GyroSensor('in2')
us = ev3.UltrasonicSensor('in4')

MAX_POS_SPEED = 1050
MAX_NEG_SPEED = -MAX_POS_SPEED


def cap_speed(speed):
    return max(MAX_NEG_SPEED, min(MAX_POS_SPEED, speed))


def forward_by(deg):
    l_motor.run_to_rel_pos(position_sp=deg, speed_sp=200)
    r_motor.run_to_rel_pos(position_sp=deg, speed_sp=200)


def forward_dist(dist, tire_radius=0.028):
    forward_by(math.degrees(dist / tire_radius))


def forward(speed, correction=0):
    speed = -speed
    ls = speed+10*correction
    rs = speed-10*correction
    if ls > MAX_POS_SPEED:
        overflow = ls - MAX_POS_SPEED
        ls = MAX_POS_SPEED
        rs = rs - overflow
    elif ls > MAX_POS_SPEED:
        overflow = rs - MAX_POS_SPEED
        rs = MAX_POS_SPEED
        ls = ls - overflow
    elif rs < MAX_NEG_SPEED:
        overflow = rs - MAX_NEG_SPEED
        ls = ls - overflow
        rs = MAX_NEG_SPEED
    elif ls < MAX_NEG_SPEED:
        overflow = ls - MAX_NEG_SPEED
        rs = rs - overflow
        ls = MAX_NEG_SPEED
    l_motor.run_forever(speed_sp=ls)
    r_motor.run_forever(speed_sp=rs)


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def forward_to(goal, gain=5):
    goal_heading = gyro.value()
    v = us.value()
    c = 0
    while v != goal and c <= 10:
        forward_correction = goal_heading - gyro.value()
        err = v - goal
        error = cap_speed(gain * err)
        if error != 0:
            forward(error, correction=int(math.copysign(forward_correction, error)))
        else:
            stop()
        v = us.value()
        if abs(err) < 2:
            c = c + 1
    stop()


def ranging_sample():
    return gyro.value(), us.value()


def rotate(speed):
    l_motor.run_forever(speed_sp=speed)
    r_motor.run_forever(speed_sp=-speed)


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


def rotate_to(goal, k_p=5, k_i=2):
    t_old = time.time()
    integrated_error = 0
    while gyro.value() != goal:
        t_new = time.time()
        error = goal - gyro.value()
        integrated_error = integrated_error + error * (t_new - t_old)
        t_old = t_new
        rotate(cap_speed(k_p*error + k_i*integrated_error))
    stop()


def spin_sample():
    m = {}
    rotate_to(0)
    rotate(100)
    while gyro.value() <= 360:
        m[gyro.value()] = us.value()
    stop()
    return m


def orient_to_closest_sample():
    m = spin_sample()
    lo = min(m, key=m.get)
    rotate_to(lo, 1)
    reset_gyro()


def say(words):
    ev3.Sound.speak(words).wait()


def wander():
    # initial_range = us.value()
    # forward_to(initial_range - 7 * 25.4)
    x = 7 * 25.4
    d = []
    v = gyro.value()
    if us.value() > x:
        d.append(0)
    rotate_to(v + 90)
    if us.value() > x:
        d.append(90)
    rotate_to(v + 180)
    if us.value() > x:
        d.append(180)
    rotate_to(v + 270)
    if us.value() > x:
        d.append(270)
    rotate_to(v)
    rotate_to(random.choice(d))
    forward_to(us.value() - x)

