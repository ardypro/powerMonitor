import serial
from time import sleep

ser=serial.Serial('/dev/ttyS1',4800)
print ser
i=0
while (True):
	ser.write(str(i))
	i=i+1
	print i
	sleep(5)	
