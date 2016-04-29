# -*- coding: utf-8 -*-

'''由于PCDuino没有提供onewire库，配电箱温度、以及房间温度暂时不支持'''
'''power monitor with PCDuino V2'''


'''
    v1.0    newly created project
    v1.1    add postDataToLewei()
    v1.2    add reboot system after err counts reaches 5
    v1.3    add log function



'''

import minimalmodbus
#from socket import *
import time
#import select
import requests
import json
import os
import gpio
import logging
import logging.config

version_str =   '1.3'

errCounts   =   0     #err counts, if it reaches 5, then reboot the board
DEBUG_MODE  =   True     #debug mode

REDPin      =   "gpio7"
BLUEPin     =   "gpio8"
GREENPin    =   "gpio9"

#判断POST操作成功的标识
hmTrueFlag = '{"errno":0,"error":"succ"}'
lwTrueFlag='{"Successful":true,"Message":"Successful. "}'

mdErrcounts	=	0	#modbus communication error
nwErrcounts	=	0	#network communication error

def delaySeconds(s):
    time.sleep(s)

def reboot():
	os.system('sudo reboot')
	
	
def clearKwh(slave):
    pwrMeter=minimalmodbus.Instrument('/dev/ttyS1',slave)
    pwrMeter.serial.baudrate=4800
    pwrMeter.serial.timeout=5
    pwrMeter.write_registers(12,[0,0])



def doNetworkErr():
    doModbusNormal()
    gpio.digitalWrite(REDPin, gpio.LOW)


    
def doNetworkNormal():
    gpio.digitalWrite(REDPin, gpio.HIGH)

    

def doModbusErr():
    doNetworkNormal()
    gpio.digitalWrite(BLUEPin, gpio.LOW)


    
def doModbusNormal():
    gpio.digitalWrite(BLUEPin, gpio.HIGH)

    

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

    global mdErrcounts

    try:
        powerMeter = minimalmodbus.Instrument('/dev/ttyS1',slave)
        powerMeter.serial.baudrate=4800
        powerMeter.serial.timeout=5

        
        #if (DEBUG_MODE):
        #    print powerMeter

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

        except IOError:
            if (DEBUG_MODE):
                print '电表通讯故障，或者电表离线'
                logging.exception('电表通讯故障。')
            err=1
            
        except ValueError:
            if (DEBUG_MODE):
                print '电表采集数据格式错误'
                logging.exception('电表数据格式错误。')
            err=2
            
    except serial.SerialException,e:
        if (DEBUG_MODE):
            print e
            print '串口通信故障'
            logging.exception('串口通信故障。')
        err=3

        
    #timeout exception:
    
    #else:
    #    print '其它不明故障'
    #    err=4

        
    finally:
		if (err==0):
			doModbusNormal()
			mdErrcounts	=	0
			
		else:
			doModbusErr()
			mdErrcounts	=	mdErrcounts + 1
			if ((mdErrcounts>5 ) and (mdErrcounts<10)):
				delaySeconds(10)
			if (mdErrcounts>=10):
				reboot()
			
    return v,a,w,kwh,pf,err


def postdata(api,key,header,data):
    '''POST数据到指定IOT服务器'''
    
    global 	errCounts
    global      nwErrcounts

    respCode	=	0
    respText	=	' '
    errCode		=	0
    try:
		r=requests.post(api,data,headers=header,timeout=15)
		nwErrcounts	=	0
		
		respCode	=	r.status_code
		respText	=	r.text
		errCode		=	0

                doNormalPost()
                #return r.status_code, r.text

    except requests.ConnectionError,e:
        if (DEBUG_MODE):
            print ('网络连接断开，无法发送数据')
            logging.exception('网络连接断开！')
        errCode=1
		
    except requests.exceptions.ReadTimeout,e:
    	if (DEBUG_MODE):
    		print 'time out'
    		logging.exception('read timed out')
    	errCode		=	2
    	
    finally:
		if (errCode==0):
			nwErrcounts	=	0
			doNetworkNormal()
		else:
			doNetworkErr()
			nwErrcounts =	nwErrcounts + 1
			if (nwErrcounts >=5):
				if (nwErrcounts>=10):
					reboot()				
				delaySeconds(5)

					
		return respCode, respText
    		


def postDataToLewei(v,a,w,kwh,pf,err):
    if (v<=0.001):		#modbus communication error
    	doModbusErr()
    	return False
    	
    	
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
    if (DEBUG_MODE):
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

    if (DEBUG_MODE):
        logging.info('电流: '+ str(a))

    if (text == lwTrueFlag): 
        if (DEBUG_MODE):
            logging.info('成功发送到乐为服务器。')
        return True
    else:
        if (DEBUG_MODE):
            logging.exception('发送到乐为服务器失败。')
        return  False



def postDataToOneNet(v,a,w,kwh,pf,err):
    '''发送采集到的数据到onenet.10086.cn'''
    if (v<=0.001):		#采集到的电压为0，由于模块是有被采样电路供电，所以采集到0V电压是错误的
    	doModbusErr()
    	return False
    	
    hm_api='http://api.heclouds.com/devices/1071322/datapoints?type=3'
    hm_api_key='YPjeEHaQKQA0aholzHpROJI4CCc='
    payload={'Voltage':v, 'Amp':a, 'WATT':w, 'TotalKWh':kwh, 'P_Rate':pf, 'err':err}
    _data=json.dumps(payload)
    _headers={'api-key':hm_api_key}


    code,text=postdata(hm_api,hm_api_key,_headers,_data)
	
    if (DEBUG_MODE):
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

    if (DEBUG_MODE):
        logging.info('电流: '+str(a))

    if (text == hmTrueFlag):
        if (DEBUG_MODE):
            logging.info('成功发送数据到中国移动物联网服务器')
        return True
    else:
        if (DEBUG_MODE):
            logging.exception('发送数据到中国移动物联网失败')
        return False	




#test
def test():
    import random

    pf=random.random()
    vol=random.randrange(220,235)
    amp=random.randrange(1,15)

    w=vol*amp*pf
    kwh=0
    err=random.randrange(0,2)

    return vol,amp,w,kwh,pf,err


def doNormalPost(t=0.5):
    gpio.digitalWrite(GREENPin,gpio.LOW)
    time.sleep(t)
    gpio.digitalWrite(GREENPin,gpio.HIGH)

#================main proc===========================
def main():
    print '初始化设备...' 
    t0=time.time()
    

    logging.basicConfig(level=logging.WARNING,
					format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
					datefmt='%a, %d %b %Y %H:%M:%S',
					filename='/var/log/pwrinfo.log',
					filemode='w')
		
    logging.debug('调试模式')
    logging.info('初始化设备...')
    logging.warning('测试logging')
    logging.info('创建log文档')

    gpio.pinMode(BLUEPin, gpio.OUTPUT)
    gpio.pinMode(REDPin, gpio.OUTPUT)
    gpio.pinMode(GREENPin,gpio.OUTPUT)
     
    doModbusErr()
    doNetworkErr() 
    doNormalPost(0.1)
    #doModbusErr()
    #time.sleep(0.1)
    #doNetworkErr()
    #time.sleep(0.1)
    doModbusNormal()
    doNetworkNormal()
    time.sleep(10)  #设备初始化

    print '设备初始化完毕'
    
    while (True):
        doNetworkNormal()   #省电
        doModbusNormal()
        t1=time.time()

        values=samplingPower(1,72)
        postDataToOneNet(values[0],values[1],values[2],values[3],values[4],values[5])
        if ((t1-t0)>20):
             postDataToLewei(values[0],values[1],values[2],values[3],values[4],values[5])
             t0=time.time()
        time.sleep(0.5)

            
 

if __name__=='__main__':
    main()
