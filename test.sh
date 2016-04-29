#!/bin/bash
sudo modprobe hardwarelib
sudo modprobe adc
sudo modprobe pwm
sudo modprobe gpio
sudo modprobe sw_interrupt

lsmod

sudo echo "3" > /sys/devices/virtual/misc/gpio/mode/gpio0
sudo echo "3" > /sys/devices/virtual/misc/gpio/mode/gpio1

cd /
cd ~/pcduino/powerMonitor
sudo python pwrmeter_test.py

cd /
