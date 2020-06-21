# -*- coding: utf-8 -*-
import aliyunsdkiotclient.AliyunIotMqttClient as iot
import json
import threading
import time
import numpy as np
import sum
import pandas as pd


options = {
    'productKey':'######',
    'deviceName':'#####',
    'deviceSecret':'###',
    'port':1883,
    'host':'iot-as-mqtt.cn-shanghai.aliyuncs.com'
}

# initialling
send_frequency = [0,0,0]
voltage = 0
inductance = "3H"
record_inductance = "3H"
get_resonant_frequency = '0'
get_quality_factor = '0'
host = options['productKey'] + '.' + options['host']


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #topic = '/' + productKey + '/' + deviceName + '/update'
    #{"method":"thing.service.property.set","id":"169885527","params":{"LED":1},"version":"1.0.0"}
    print(msg.payload)
    setjson = json.loads(msg.payload)
    global send_frequency
    global inductance
    global get_resonant_frequency
    global get_quality_factor
    for c in setjson['params'].keys():
        if c == 'send_frequency':
            send_frequency = setjson['params']['send_frequency']
        elif c == 'inductance':
            inductance = setjson['params']['inductance']
        elif c == 'get_resonant_frequency':
            get_resonant_frequency = setjson['params']['get_resonant_frequency']
        elif c == 'get_quality_factor':
            get_quality_factor = setjson['params']['get_quality_factor']
            pass
        pass
    print(send_frequency)
    print(inductance)

#     GPIO.output(led_pin,(GPIO.HIGH if led==1 else GPIO.LOW ))

    
def on_connect(client, userdata, flags_dict, rc):
    print("Connected with result code " + str(rc))
    
def on_disconnect(client, userdata, flags_dict, rc):
    print("Disconnected.")

def worker(client):
    global send_frequency
    global inductance
    global record_inductance
    global get_resonant_frequency
    global get_quality_factor

    topic = '/sys/'+options['productKey']+'/'+options['deviceName']+'/thing/event/property/post'
    while True:
        if inductance != record_inductance:
            sum.choose_inductance(inductance)
            record_inductance = inductance
            time.sleep(3)  # 确认继电器搞定了
            pass

        if get_resonant_frequency != '0':
            get_resonant_frequency = sum.return_resonant_csv(get_resonant_frequency)
            payload_json = {
                #            'id': int(time.time()),
                'params': {
                    'get_resonant_frequency': get_resonant_frequency + "Hz",
                },
                #            'method': "thing.event.property.post"
            }

            print('send data to iot server: ' + str(payload_json))
            client.publish(topic, payload=str(payload_json))
            get_resonant_frequency = '0'
            pass

        if get_quality_factor != '0':
            get_quality_factor = sum.return_quality_factor_csv(get_quality_factor)
            payload_json = {
                #            'id': int(time.time()),
                'params': {
                    'get_quality_factor': get_quality_factor,
                },
                #            'method': "thing.event.property.post"
            }

            print('send data to iot server: ' + str(payload_json))
            client.publish(topic, payload=str(payload_json))
            get_quality_factor = '0'
            pass


        if send_frequency != [0,0,0]:
            record_data = np.zeros((int((send_frequency[2] - send_frequency[0]) / send_frequency[1] + 1),2),dtype= np.float)
            i = 0
            for f in np.arange(send_frequency[0],send_frequency[2]+1, send_frequency[1]):
                f = int(f)
                voltage = sum.send_and_get(f)
                record_data[i, :] = [f, voltage]
                payload_json = {
                    #            'id': int(time.time()),
                    'params': {
                        'inductance':inductance,
                        'get_frequency_' + inductance: str(f)+'Hz',
                        'get_voltage_' + inductance: voltage,
                        'get_frequency': str(f)+'Hz',
                        'get_voltage': voltage,
                    },
                    #            'method': "thing.event.property.post"
                }

                print('send data to iot server: ' + str(payload_json))
                client.publish(topic, payload=str(payload_json))
                i = i + 1 # record index

                pass
            send_frequency = [0,0,0]
            sum.read_and_write_csv(record_data,inductance)
            print("数据成功写入")
            pass
        time.sleep(3)   # 休息一下
        pass
    pass



        


if __name__ == '__main__':
    client = iot.getAliyunIotMqttClient(options['productKey'], options['deviceName'], options['deviceSecret'], secure_mode=3)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    sum.choose_inductance(inductance) # 默认使用3H
    client.connect(host=host, port=options['port'], keepalive=60)
    t1 = threading.Thread(target = worker, args =(client,))
    t2 = threading.Thread(target = client.loop_forever)
    t1.start()
    t2.start()
