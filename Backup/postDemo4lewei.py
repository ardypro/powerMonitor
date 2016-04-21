 #-*- coding: utf-8 -*-

import requests
import json



#数据流名称
voltage='v1'
amp='a1'
watt='w1'
kwh='kw'
co2='c1'
prate='pf'

def sampling():
	foo=4

def postDataToLewei(v,a,w,k,p):
	lwapi='http://www.lewei50.com/api/v1/gateway/updatesensors/02'
	lwapi_key='2c2a9948d4c049c18560ddbfb46930d8'
	#payload={voltage:v, amp:a, watt:w, kwh:k, co2:c, prate:p}
	#payload={}
	_data='['
	_data=_data+'{"Name":"v1","Value":"'+ str(v) +'"},'
	_data=_data+'{"Name":"a1","Value":"'+ str(a) +'"},'
	_data=_data+'{"Name":"w1","Value":"'+ str(w) +'"},'
	_data=_data+'{"Name":"kw","Value":"'+ str(k) +'"},'
	_data=_data+'{"Name":"pf","Value":"'+ str(p) +'"}'
	_data=_data+']'


	#_data=json.dumps(payload)
	_headers={'userkey':lwapi_key}
	r=requests.post(lwapi, _data, headers=_headers)

	print _data
	print r.text

	if r.status_code != 200 :
		print r.text

if __name__=='__main__':
	sampling()
	postDataToLewei(1,1,1,1,1)
