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

	
	
def clearKwh(slave):
    pwrMeter=minimalmodbus.Instrument('/dev/ttyS1',slave)
    pwrMeter.serial.baudrate=4800
    pwrMeter.serial.timeout=5
    pwrMeter.write_registers(12,[0,0])


    


if __name__=='__main__':
   clearKwh(1)
