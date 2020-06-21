# -*- coding: utf-8 -*-

import threading
import time
import random
import numpy as np
import RPi.GPIO as GPIO
import rawAD9850
import smbus
import pandas as pd


# 读取电压
voltage = 0

def AC_voltage():
    global voltage
    address = 0x48
    A0 = 0x40
    A1 = 0x41
    A2 = 0x42
    A3 = 0x43
    bus = smbus.SMBus(1)
    vol = 0
    for i in range(50):
        bus.write_byte(address,A0)
        value = bus.read_byte(address)
        value = value/255*5
        if i > 1 and vol < value:
            vol = value
            pass
        time.sleep(0.05)
        pass
#
#    voltage = (max - min)/2
    voltage = vol
    pass


# 调用继电器
def choose_inductance(inductance):

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    pin_3H = 36
    pin_1H = 38
    pin_1mH = 40

    GPIO.setup(pin_3H, GPIO.OUT)
    GPIO.setup(pin_1H, GPIO.OUT)
    GPIO.setup(pin_1mH, GPIO.OUT)

    if inductance == "3H":
        GPIO.output(pin_1mH, False)
        GPIO.output(pin_1H, False)
        GPIO.output(pin_3H, True)
    elif inductance == "1H":
        GPIO.output(pin_1mH, False)
        GPIO.output(pin_3H, False)
        GPIO.output(pin_1H, True)
    elif inductance == "1mH":
        GPIO.output(pin_3H, False)
        GPIO.output(pin_1H, False)
        GPIO.output(pin_1mH, True)
        pass
    pass


# 记录数据用的
def read_and_write_csv(record_data,inductance):
    data = pd.read_csv('data_' + inductance + '.csv', encoding='gb2312', sep='\n' and ',')
    data = np.array(data)
    data = data[:,1:3]

    i = 0
    for f in record_data[:,0]:
        j = 0
        for F in data[:,0]:
            if f == F:
                data[j,:] = (record_data[i,:] + data[j,:]) / 2
                break
            elif f < F:
                data = np.insert(data, j, values=record_data[i,:], axis= 0)
                break
                pass
            j = j + 1
            pass
        i = i + 1
        pass

    data = pd.DataFrame(data)
    data.to_csv('data_' + inductance + '.csv')
    pass


# 返回谐振频率
def return_resonant_csv(get_resonant_frequency):
    data = pd.read_csv('data_' + get_resonant_frequency + '.csv', encoding='gb2312', sep='\n' and ',')
    data = np.array(data)
    data = data[:, 1:3]
    return str(data[np.argmax(data[:,1]),0])


# 返回品质因子
def return_quality_factor_csv(get_quality_factor):
    data = pd.read_csv('data_' + get_quality_factor + '.csv', encoding='gb2312', sep='\n' and ',')
    data = np.array(data)
    data = data[:, 1:3]
    index = int(np.argmax(data[:, 1]))
    f_0 = data[index, 0]
    l = 0
    r = 0
    left_f = 0
    right_f = 0
    for i in np.arange(index, 0, -1):
        if data[i, 1] < data[index, 1]:
            left_f = (data[i, 0] + data[i + 1, 0]) / 2
            l = 1
            break
            pass
        pass

    for i in np.arange(index, np.size(data[:, 0]), 1):
        if data[i, 1] < data[index, 1]:
            right_f = (data[i, 0] + data[i - 1, 0]) / 2
            r = 1
            break
            pass
        pass

    if l == 0 or r == 0:
        return '数据不全'
    else:
        return str(f_0 / (right_f - left_f))


# 采集数据用的
def send_and_get(f):
    global voltage
    c1 = threading.Thread(target = rawAD9850.output, args =(f,))
    c2 = threading.Thread(target = AC_voltage)
    c1.start()
    time.sleep(5)
    c2.start()
    c1.join()
    c2.join()
    return voltage


