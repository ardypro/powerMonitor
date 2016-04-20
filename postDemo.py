 #-*- coding: utf-8 -*-

import requests
import json

api='http://api.heclouds.com/devices/1071322/datapoints?type=3'
api_key='YPjeEHaQKQA0aholzHpROJI4CCc='

#数据流名称
voltage='Voltage'
amp='Amp'
watt='WATT'
kwh='TotalKWh'
co2='CO2'
prate='P_Rate'

def sampling():
	return 1,2,3,4,5,6

def postData(v,a,w,k,c,p):
	payload={voltage:v, amp:a, watt:w, kwh:k, co2:c, prate:p}
	_data=json.dumps(payload)
	_headers={'api-key':api_key}
	r=requests.post(api, _data, headers=_headers)

	#print _data
	#print r.text
	if r.status_code != 200 :
		print r.text

if __name__=='__main__':
	#sampling()
	postData(1,2,3,4,5,6)
