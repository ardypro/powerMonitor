import minimalmodbus

p=minimalmodbus.Instrument('com10',1)
p.serial.baudrate=4800
p.serial.timeout=50

pwrInfo= p.read_registers(72,6)
print pwrInfo
