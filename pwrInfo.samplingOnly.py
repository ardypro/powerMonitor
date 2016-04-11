# -*- coding: utf-8 -*-

import minimalmodbus
from socket import *
import time
import select

apiAddr= 'POST http://api.heclouds.com/devices/1071322/datapoints?type=3 HTTP/1.1\r\n'
device_id = '1071322'
device_key ='YPjeEHaQKQA0aholzHpROJI4CCc='

HOST = 'api.heclouds.com'
PORT = 80
BUFSIZE = 1024
ADDR = (HOST, PORT)



def postDatastreams(v,a,w,kwh,co2,prate):
	contents = " "
	contents = "{\"Voltage\" : "+ str(v) 
	contents += ", \"Amp\": " + str(a) 
	contents += ", \"WATT\" : " + str(w) 
	contents += ", \"TotalKWh\": " + str(kwh) 
	contents += ", \"CO2\": " + str(co2) 
	contents += ", \"P_Rate\": " + str(prate) + "}"

	return contents

powerMeter = minimalmodbus.Instrument('COM10',1)
powerMeter.serial.baudrate=4800
powerMeter.serial.timeout=50


i=1

while (True):


#while True:
	print "index: ", i
	powerInfo = powerMeter.read_registers(72,6)

	print  '电压:     ', powerInfo[0] / 100.0
	print  '电流:     ', round(powerInfo[1]/ 1000.0,2)
	print  '有功功率: ', powerInfo[2]/ 1.0
	print  '电能:     ', round( powerInfo[3] /3200.0,4)
	print  'CO2：     ', powerInfo[4]
	print  '功率因素：', powerInfo[5]/1000.0


	

	#print "DEBUGGING"
	#print jsonStr


	
	time.sleep(1)
	i=i+1
	print " "
