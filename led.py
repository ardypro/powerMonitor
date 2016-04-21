import gpio
import time

redpin='gpio7'
blackpin='gpio15'

gpio.pin_mode(blackpin, gpio.OUTPUT)
gpio.digital_write(blackpin,gpio.HIGH)

gpio.pin_mode(redpin, gpio.OUTPUT)
gpio.digital_write(redpin,gpio.LOW)
time.sleep(5)
gpio.digital_write(redpin, gpio.HIGH)
