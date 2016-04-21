import minimalmodbus
import time

p=minimalmodbus.Instrument('com10',1)
p.serial.baudrate=4800
p.serial.timeout=50

#pwrInfo= p.write_registers(12,[0,0])  

#print pwrInfo
time.sleep(1)

pwrInfo=p.read_registers(72,6)
h=pwrInfo[3]
l=pwrInfo[4]

h<<8
total=h+l
print total/3200.0

print pwrInfo
