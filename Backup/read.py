# -*- coding: utf-8 -*-
import minimalmodbus
from time import sleep
import os

os.system("sudo modprobe adc")
p=minimalmodbus.Instrument('/dev/ttyS1',1)
p.serial.baudrate=4800
p.serial.timeout=1
#p.debug=True
print "beginning..."
while (True):
	try:
		pwrInfo= p.read_registers(72,6)
		print pwrInfo
	except IOError:
		print 'failed to read from the instrument'
	except ValueError:
		print "instrument response is invalid"
	sleep(1.5)	
