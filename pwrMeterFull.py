# -*- coding: utf-8 -*-

'''由于PCDuino没有提供onewire库，配电箱温度、以及房间温度暂时不支持'''
'''power monitor with PCDuino V2'''


import minimalmodbus
from socket import *
import time
import select
import requests
import json

version_str='1.0'

api='http://api.heclouds.com/devices/1071322/datapoints?type=3'
api_key='YPjeEHaQKQA0aholzHpROJI4CCc='
values=[0,0,0,0,0,0,0,0] #对应电压、电流、有功功率、总电量、功率因素、配电箱内部温度、房间温度、房间湿度

#数据流名称
voltage	=	'Voltage'
amp		=	'Amp'
watt		=	'WATT'
kwh		=	'TotalKWh'

prate		=	'P_Rate'
ds18b20_id='a' #id


def sampleTempInside(id): #ds18b20 id
    '采集配电箱内部温度'
    t=2
    return t
    
def sampleDHT22():
    '采集房间温度、湿度'
    t=20
    h=98
    return t,h


def samplingPower(slave,register):
    '采集电量、配电箱内部温度以及房间的温度、湿度值'
    powerMeter = minimalmodbus.Instrument('/dev/ttyS1',slave)
    powerMeter.serial.baudrate=4800
    powerMeter.serial.timeout=50

    print powerMeter

    powerInfo = powerMeter.read_registers(register,6)

    #需要判断返回是否正常
    values[0]=powerInfo[0] / 100.0
    values[1]=round(powerInfo[1]/ 1000.0,2)
    values[2]=powerInfo[2]/ 1.0
    hi=powerInfo[3]
    low=powerInfo[4]
    hi<<8
    	
    values[3]=round( (hi+low) /3200.0,4)    

    values[4]=powerInfo[5]/1000.0
    
    print  '电压:     \t', values[0]
    print  '电流:     \t', values[1]
    print  '有功功率:  \t', values[2]
    print  '电能:     \t', values[3]
    print  '功率因素： \t', values[4]
    print " "    


def postData(v):
    '发送采集到的数据到指定服务商'
    payload={voltage:v[0], amp:v[1], watt:[2], kwh:v[3], prate:v[4]}
    _data=json.dumps(payload)
    _headers={'api-key':api_key}
    r=requests.post(api, _data, headers=_headers)

    #print _data
    #print r.text
    if r.status_code != 200 :
        print r.text


if __name__=='__main__':
    while (True):
        samplingPower(1,72)
        time.sleep(1)
        #postData()
