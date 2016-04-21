# -*- coding: utf-8 -*-

'''由于PCDuino没有提供onewire库，配电箱温度、以及房间温度暂时不支持'''
'''power monitor with PCDuino V2'''


'''
    v1.0    newly created project
    v1.1    add postDataToLewei()
    v1.2    add reboot system after err counts reaches 5




'''

import minimalmodbus
#from socket import *
import time
#import select
import requests
import json
import os
import gpio

version_str =   '1.2'

errCounts   =   0     #err counts, if it reaches 5, then reboot the board
DEBUG_MODE  =   False     #debug mode

REDPin      =   "gpio14"
GREENPin    =   "gpio15"

def clearKwh(slave):
    pwrMeter=minimalmodbus.Instrument('/dev/ttyS1',slave)
    pwrMeter.serial.baudrate=4800
    pwrMeter.serial.timeout=10
    pwrMeter.write_registers(12,[0,0])



def turnOnRED():
    turnOffGREEN()
    gpio.digitalWrite(REDPin, gpio.LOW)


    
def turnOffRED():
    gpio.digitalWrite(REDPin, gpio.HIGH)

    

def turnOnGREEN():
    turnOffRED()
    gpio.digitalWrite(GREENPin, gpio.LOW)


    
def turnOffGREEN():
    gpio.digitalWrite(GREENPin, gpio.HIGH)

    

def samplingPower(slave,register):
    '采集电量'
    if (DEBUG_MODE):
        values= test()
        return values

    #define variable to host power info
    v=0.0
    a=0.0
    w=0.0
    kwh=0.0
    pf=0.0
    err=0 #错误代码
    try:
        powerMeter = minimalmodbus.Instrument('/dev/ttyS1',slave)
        powerMeter.serial.baudrate=4800
        powerMeter.serial.timeout=10

        
        if (DEBUG_MODE):
            print powerMeter

        try:	
            powerInfo = powerMeter.read_registers(register,6)

            #需要判断返回是否正常
            v=powerInfo[0] / 100.0
            a=round(powerInfo[1]/ 1000.0,2)
            w=powerInfo[2]/ 1.0
            hi=powerInfo[3]
            low=powerInfo[4]
            hi<<8
            kwh=round( (hi+low) /3200.0,4)    
            pf=powerInfo[5]/1000.0
            err=0
            turnOnGREEN()
            
        except IOError:
            print '电表通讯故障，或者电表离线'
            err=1
            turnOnRED()
            
        except ValueError:
            print '电表采集数据格式错误'
            err=2
            turnOnRED()
            
    except serial.SerialException,e:
        print e
        print '串口通信故障'
        err=3
        turnOnRED()
        
    else:
        print '其它不明故障'
        err=4
        turnOnRED()
        
    finally:
        return v,a,w,kwh,pf,err


def postdata(api,key,header,data):
    '''POST数据到指定IOT服务器'''
    
    try:
        r=requests.post(api,data,headers=header)
        errCounts=0     #reset err counts to 0

        turnOnGREEN()
        return r.status_code, r.text

    except requests.ConnectionError,e:
        print ('网络连接断开，无法发送数据')
        turnOnRED()
        errCounts=errCounts+1
        if (errCounts==5):
            os.system('sudo reboot')    #reboot the computer
        else:
            errCounts=errCounts%5




def postDataToLewei(v,a,w,kwh,pf,err):

    lw_api='http://www.lewei50.com/api/v1/gateway/updatesensors/02'
    lw_api_key='2c2a9948d4c049c18560ddbfb46930d8'
    _data='['
    _data=_data+'{"Name":"v1","Value":"'+ str(v) +'"},'
    _data=_data+'{"Name":"a1","Value":"'+ str(a) +'"},'
    _data=_data+'{"Name":"w1","Value":"'+ str(w) +'"},'
    _data=_data+'{"Name":"kw","Value":"'+ str(kwh) +'"},'
    _data=_data+'{"Name":"pf","Value":"'+ str(pf) +'"},'
    _data=_data+'{"Name":"e1","Value":"'+ str(err) +'"}'
    _data=_data+']'



    _headers={'userkey':lw_api_key}
    code,text=postdata(lw_api,lw_api_key,_headers,_data)

    print " "
    print "==============>>>>>>>>>>>>"
    print "posting data to ", lw_api
    print " "
    print  'Time:    \t', time.asctime( time.localtime(time.time()) )
    print  '电压:     \t', v
    print  '电流:     \t', a
    print  '有功功率:  \t', w
    print  '电能:     \t', kwh
    print  '功率因素： \t', pf
    print " " 
    print code
    print text
    print "=========================="
    print " " 

    if (code==200): #need to be modified later
        return True
    else:
        return False



def postDataToOneNet(v,a,w,kwh,pf,err):
    '''发送采集到的数据到onenet.10086.cn'''

    hm_api='http://api.heclouds.com/devices/1071322/datapoints?type=3'
    hm_api_key='YPjeEHaQKQA0aholzHpROJI4CCc='
    payload={'Voltage':v, 'Amp':a, 'WATT':w, 'TotalKWh':kwh, 'P_Rate':pf, 'err':err}
    _data=json.dumps(payload)
    _headers={'api-key':hm_api_key}


    code,text=postdata(hm_api,hm_api_key,_headers,_data)

    print " "
    print "==============>>>>>>>>>>>>"
    print "posting data to ", hm_api
    print " "
    print  'Time:    \t', time.asctime( time.localtime(time.time()) )
    print  '电压:     \t', v
    print  '电流:     \t', a
    print  '有功功率:  \t', w
    print  '电能:     \t', kwh
    print  '功率因素： \t', pf
    print " " 
    print code
    print text
    print "=========================="
    print " " 

    if (code==200):
        return True
    else:
        return False	




#test
def test():
    import random

    pf=random.random()
    vol=random.randrange(210,240)
    amp=random.randrange(1,60)

    w=vol*amp*pf
    kwh=0
    err=0

    return vol,amp,w,kwh,pf,err


#================main proc===========================
if __name__=='__main__':
    print '初始化设备...'	
    t0=time.time()
    
    gpio.pinMode(GREENPin, gpio.OUTPUT)
    gpio.pinMode(REDPin, gpio.OUTPUT)
    turnOnGREEN()
    time.sleep(15)  #设备初始化

    print '设备初始化完毕'
    
    while (True):
        #turnOffRED()   #省电
        turnOffGREEN()
        t1=time.time()

        values=samplingPower(1,72)
        postDataToOneNet(values[0],values[1],values[2],values[3],values[4],values[5])
        if ((t1-t0)>20):
             postDataToLewei(values[0],values[1],values[2],values[3],values[4],values[5])
             t0=time.time()
        time.sleep(2)

            
 
