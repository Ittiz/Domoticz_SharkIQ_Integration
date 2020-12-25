import DomoticzEvents as DE
import os
import urllib.parse
import datetime
import json
import re
import html

vrov = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=command&param=getuservariables" &').read()
def getvar(name):
	stop1 = vrov.find('"' + name + '"')
	if stop1 > -1:
		stop1 = vrov.find('"Value" : "',stop1)+11
		stop2 = vrov.find('",',stop1)
		var = vrov[stop1:stop2]
		#DE.Log("Python: " + var)
		return var
	else:
		return None

def getvarID(name):
	vro = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=command&param=getuservariables" &').read()
	stop1 = vro.find('"' + name + '"')
	if stop1 > -1:
		stop1 = vro.find('"idx" : "',stop1)+9
		stop2 = vro.find('"',stop1)
		var = vro[stop1:stop2]
		#DE.Log("Python: " + var)
		return int(var)
	else:
		return None

das = os.popen('curl -m 1 --silent  -k "http://127.0.0.1/json.htm?type=devices&filter=all&used=true" &').read()
def getDevID(name):
	stop0 = das.find('"' + name + '"')
	if stop0 > -1:
		stop0 = das.find('"idx" : "',stop0)
		stop1 = das.find('"',stop0+10)
		return int(das[stop0+9:stop1])
	else:
		return None

def getDevVal(name):
	da = os.popen('curl -m 1 --silent  -k "http://127.0.0.1/json.htm?type=devices&filter=all&used=true" &').read()
	stop0 = da.find('"' + name + '"')
	if stop0 > -1:
		stop0 = da.rfind('"Data" : "',0,stop0)
		stop1 = da.find('"',stop0+11)
		stop1 = da.rfind(' ',stop0,stop1)
		return da[stop0+10:stop1]
	else:
		return None

def createvar(name,vtype,value):
	name = urllib.parse.quote(str(name))
	value = urllib.parse.quote(str(value))
	vro = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=command&param=adduservariable&vname=' + str(name) + '&vtype=' + str(vtype) + '&vvalue=' + str(value) + '" &').read()
	DE.Log("Python: " + vro)
	return

def updatevar(name,vtype,value):
	ID = getvarID(name)
	name = urllib.parse.quote(str(name))
	value = urllib.parse.quote(str(value))
	vro = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=command&param=updateuservariable&idx=' + str(ID) + '&vname=' + str(name) + '&vtype=' + str(vtype) + '&vvalue=' + str(value) + '" &').read()
	DE.Log("Python: " + vro)
	return

def updateDevice(name,nvalue,svalue):
	ID = getDevID(name)
	name = urllib.parse.quote(str(name))
	nvalue = urllib.parse.quote(str(nvalue))
	svalue = urllib.parse.quote(str(svalue))
	vro = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?param=udevice&type=command&idx=' + str(ID) + '&nvalue=' + str(nvalue) + '&svalue=' + str(svalue) + '" &').read()
	DE.Log("Python: " + vro)
	return

def getHWID(name):
	da = os.popen('curl -m 1 --silent  -k "http://127.0.0.1/json.htm?type=hardware" &').read()
	stop0 = da.find('"' + name + '"')
	#DE.Log("Python: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" + stop0)
	if stop0 > -1:
		stop0 = da.find('"idx" : "',stop0)
		stop1 = da.find('"',stop0+10)
		return int(da[stop0+9:stop1])
	else:
		return None

def getVacVal(array):
	newdict = {}
	for x in array:
		newdict[x['property']['name']] = x
	#DE.Log(newdict['GET_Charging_Status']['property']['name'])
	return newdict

#date_time = datetime.datetime.strptime(tstamp, '%I:%M %p - %d %b %Y').strftime("%s")
#end test setup

stop0 = 0
stop1 = 0
token = ""
email = ""
psswrd = ""
dev = {}
params = {}
VcNm = ""
VcHWID = 0
def updateDomoDevs(params):
	#print(params)
	#DE.Log("Python: " + DE.Devices[VcNm + " Error"].s_value)
	errortable = ["No Error", VcNm + "'s side wheel got stuck while trying to clean.", VcNm + "'s side brush got stuck while trying to clean.", VcNm + "'s suction motor stopped working while trying to clean.", VcNm + "'s brushroll got stuck while trying to clean.", VcNm + "'s side wheel got stuck while trying to clean.", VcNm + "'s bumper got stuck while trying to clean.", VcNm + " stopped cleaning because its cliff sensors are blocked.", VcNm + " has reached very low battery, your robot will likely power off shortly.", VcNm + " cannot run because its dust cup is missing.", VcNm + " stopped cleaning because it is on an uneven surface.", "Something has interrupted " + VcNm + "'s cleaning.", "The wrong power adapter is being used to charge " + VcNm + "'s", VcNm + "'s power switch is off.", VcNm + " is stuck on a magnetic boundary strip.", "Unknown Error: 15", VcNm + "'s top bumper got stuck while trying to clean.", "Unknown Error: 17", "There was an error with " + VcNm + "'s drive wheel."]
	if (int(DE.Devices[VcNm + " Charge"].n_value) == 0 or int(DE.Devices[VcNm + " Charge"].n_value) == 1) and int(params['GET_Charging_Status']['property']['value']) == 0:
		updateDevice(VcNm + " Charge",2,"Discharging")
	elif int(DE.Devices[VcNm + " Charge"].n_value) != 0 and int(DE.Devices[VcNm + " Charge"].n_value) != 1 and int(params['GET_Charging_Status']['property']['value']) == 1:
		if params['GET_Battery_Capacity']['property']['value'] < 100:
			updateDevice(VcNm + " Charge",0,"Charging")
		elif params['GET_Battery_Capacity']['property']['value'] == 100:
			updateDevice(VcNm + " Charge",1,"Charged")
	if int(DE.Devices[VcNm + " Battery"].s_value) != params['GET_Battery_Capacity']['property']['value']:
		updateDevice(VcNm + " Battery",0,params['GET_Battery_Capacity']['property']['value'])
		if int(DE.Devices[VcNm + " Charge"].n_value) != 0 and int(DE.Devices[VcNm + " Charge"].n_value) != 1:
			if params['GET_Battery_Capacity']['property']['value'] > 15 and int(DE.Devices[VcNm + " Charge"].n_value) != 2:
				updateDevice(VcNm + " Charge",2,"Discharging")
			elif params['GET_Battery_Capacity']['property']['value'] < 16 and params['GET_Battery_Capacity']['property']['value'] > 0 and int(DE.Devices[VcNm + " Charge"].n_value) != 3:
				updateDevice(VcNm + " Charge",3,"Low")
			elif params['GET_Battery_Capacity']['property']['value'] == 0 and int(DE.Devices[VcNm + " Charge"].n_value) != 4:
				updateDevice(VcNm + " Charge",4,"Dead")
		elif int(DE.Devices[VcNm + " Charge"].n_value) == 0 or int(DE.Devices[VcNm + " Charge"].n_value) == 1:
			if params['GET_Battery_Capacity']['property']['value'] < 100 and int(DE.Devices[VcNm + " Charge"].n_value) != 0:
				updateDevice(VcNm + " Charge",0,"Charging")
			elif params['GET_Battery_Capacity']['property']['value'] == 100 and int(DE.Devices[VcNm + " Charge"].n_value) != 1:
				updateDevice(VcNm + " Charge",1,"Charged")
	if DE.Devices[VcNm + " Error"].s_value != errortable[params['GET_Error_Code']['property']['value']]:
		updateDevice(VcNm + " Error","0",errortable[params['GET_Error_Code']['property']['value']])
	test = ""
	if int(params['GET_Charging_Status']['property']['value']) == 0:
		test = "Returning to Dock"
	elif int(params['GET_Charging_Status']['property']['value']) == 1:
		test = "Docked"
	#print("Shark:", params['GET_Operating_Mode'])
	if (DE.Devices[VcNm + " Mode"].n_value != params['GET_Operating_Mode']['property']['value']) or (str(DE.Devices[VcNm + " Mode"].s_value) != test and params['GET_Operating_Mode']['property']['value'] == 3):
		#DE.Log("Python: " + str(DE.Devices[VcNm + " Mode"].n_value) + ", " + str(params[23]['property']['value']))
		if params['GET_Operating_Mode']['property']['value'] == 0:
			msg = "Paused"
		elif params['GET_Operating_Mode']['property']['value'] == 1:
			msg = "Unknown"
		elif params['GET_Operating_Mode']['property']['value'] == 2:
			msg = "Cleaning"
		elif params['GET_Operating_Mode']['property']['value'] == 3:
			if int(params['GET_Charging_Status']['property']['value']) == 0:
				msg = "Returning to Dock"
			elif int(params['GET_Charging_Status']['property']['value']) == 1:
				msg = "Docked"
		updateDevice(VcNm + " Mode",params['GET_Operating_Mode']['property']['value'],msg)
	if DE.Devices[VcNm + " Power"].n_value != params['GET_Power_Mode']['property']['value']:
		if params['GET_Power_Mode']['property']['value'] == 0:
			msg = "Normal"
		elif params['GET_Power_Mode']['property']['value'] == 1:
			msg = "Eco"
		elif params['GET_Power_Mode']['property']['value'] == 2:
			msg = "High"
		updateDevice(VcNm + " Power",params['GET_Power_Mode']['property']['value'],msg)

TAG_RE = re.compile(r'<[^>]+>')
URL_RE = re.compile('http[^\s]*')
WS_RE = re.compile('\s+')

rID = ""
vacurl = "https://ads-field.aylanetworks.com/apiv1/devices"
vacparameters = ".json?env=field_production"

header = " -H 'authorization: auth_token " + token + "'"
header = header + " -H 'authority: ads-field.aylanetworks.com' -H 'accept: application/json, text/plain, */*' -H 'cache-control: max-age=0' -H 'origin: https://dashboard.aylanetworks.com' -H 'sec-fetch-site: same-site' -H 'sec-fetch-mode: cors' -H 'referer: https://dashboard.aylanetworks.com/' -H 'accept-encoding: gzip, deflate, br' -H 'accept-language: en-US,en;q=0.9' --compressed"
header = header + " -j -L -b non-existing"

def startup(dev):
	VcNm = str(dev[0]['device']['product_name'])
	createvar("VacName",2,VcNm)
	if (getHWID("VacName") == None):
		resp = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=command&param=addhardware&htype=15&name=' + urllib.parse.quote(VcNm) + '&enabled=true&datatimeout=0" &').read()
		stop0 = da.find('"idx" : "',0)
		stop1 = da.find('"',stop0+10)
		VcHWID = int(da[stop0+9:stop1])
	else:
		VcHWID = int(getHWID("VacName"))
	if (getDevID(VcNm + " Clean") == None):
		resp = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=createdevice&idx=' + str(VcHWID) + '&sensorname=' + urllib.parse.quote(VcNm) + '%20Clean&sensormappedtype=0xF449" &').read()
		stop0 = da.find('"idx" : "',0)
		stop1 = da.find('"',stop0+10)
		rID = int(da[stop0+9:stop1])
		resp = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?addjvalue=0&addjvalue2=0&customimage=0&description=&idx=' + rID + '&name=' + urllib.parse.quote(VcNm) + '%20Clean&options=&protected=false&strparam1=&strparam2=&switchtype=9&type=setused&used=true &').read()
	elif (getDevID(VcNm + " Dock") == None):
		resp = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=createdevice&idx=' + str(VcHWID) + '&sensorname=' + urllib.parse.quote(VcNm) + '%20Dock&sensormappedtype=0xF449" &').read()
		stop0 = da.find('"idx" : "',0)
		stop1 = da.find('"',stop0+10)
		rID = int(da[stop0+9:stop1])
		resp = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?addjvalue=0&addjvalue2=0&customimage=0&description=&idx=' + rID + '&name=' + urllib.parse.quote(VcNm) + '%20Dock&options=&protected=false&strparam1=&strparam2=&switchtype=9&type=setused&used=true &').read()
	elif (getDevID(VcNm + " Pause") == None):
		resp = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=createdevice&idx=' + str(VcHWID) + '&sensorname=' + urllib.parse.quote(VcNm) + '%20Pause&sensormappedtype=0xF449" &').read()
		stop0 = da.find('"idx" : "',0)
		stop1 = da.find('"',stop0+10)
		rID = int(da[stop0+9:stop1])
		resp = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?addjvalue=0&addjvalue2=0&customimage=0&description=&idx=' + rID + '&name=' + urllib.parse.quote(VcNm) + '%20Pause&options=&protected=false&strparam1=&strparam2=&switchtype=9&type=setused&used=true &').read()
	elif (getDevID(VcNm + " Power Mode") == None):
		resp = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=createdevice&idx=' + str(VcHWID) + '&sensorname=' + urllib.parse.quote(VcNm) + '%20Power%20Mode&sensormappedtype=0xF449" &').read()
		stop0 = da.find('"idx" : "',0)
		stop1 = da.find('"',stop0+10)
		rID = int(da[stop0+9:stop1])
		resp = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?addjvalue=0&addjvalue2=0&customimage=0&description=&idx=' + rID + '&name=' + urllib.parse.quote(VcNm) + '%20Power&options=TGV2ZWxOYW1lczpPZmZ8RWNvfE5vcm1hbHxNYXg7TGV2ZWxBY3Rpb25zOnx8fDtTZWxlY3RvclN0eWxlOjA7TGV2ZWxPZmZIaWRkZW46dHJ1ZQ%3D%3D&protected=false&strparam1=&strparam2=&switchtype=18&type=setused&used=true" &').read()
	elif (getDevID(VcNm + " Charge") == None):
		resp = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=createdevice&idx=' + str(VcHWID) + '&sensorname=' + urllib.parse.quote(VcNm) + '%20Charge&sensormappedtype=0xF316" &').read()
	elif (getDevID(VcNm + " Mode") == None):
		resp = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=createdevice&idx=' + str(VcHWID) + '&sensorname=' + urllib.parse.quote(VcNm) + '%20Mode&sensormappedtype=0xF316" &').read()
	elif (getDevID(VcNm + " Power") == None):
		resp = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=createdevice&idx=' + str(VcHWID) + '&sensorname=' + urllib.parse.quote(VcNm) + '%20Power&sensormappedtype=0xF316" &').read()
	elif (getDevID(VcNm + " Battery") == None):
		resp = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=createdevice&idx=' + str(VcHWID) + '&sensorname=' + urllib.parse.quote(VcNm) + '%20Battery&sensormappedtype=0xF306" &').read()
	elif (getDevID(VcNm + " Error") == None):
		resp = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=createdevice&idx=' + str(VcHWID) + '&sensorname=' + urllib.parse.quote(VcNm) + '%20Error&sensormappedtype=0xF313" &').read()
	createvar("VacName",2,VcNm)

if (getvar("AylaToken") == None):
	createvar("AylaToken",2,"")
else:
	token = getvar("AylaToken")
if (getvar("AylaMail") == None):
	createvar("AylaMail",2,"")
else:
	email = urllib.parse.quote(getvar("AylaMail"))
if (getvar("AylaPass") == None):
	createvar("AylaPass",2,"")
else:
	psswrd = urllib.parse.quote(getvar("AylaPass"))

vacurl = "https://ads-field.aylanetworks.com/apiv1/devices"
vacparameters = ".json?env=field_production"

header = " -H 'authorization: auth_token " + token + "'"
header = header + " -H 'authority: ads-field.aylanetworks.com' -H 'accept: application/json, text/plain, */*' -H 'cache-control: max-age=0' -H 'origin: https://dashboard.aylanetworks.com' -H 'sec-fetch-site: same-site' -H 'sec-fetch-mode: cors' -H 'referer: https://dashboard.aylanetworks.com/' -H 'accept-encoding: gzip, deflate, br' -H 'accept-language: en-US,en;q=0.9' --compressed"
header = header + " -j -L -b non-existing"

if (getvar("VacName") == None):
	try:
		dev = json.loads(os.popen("curl '" + vacurl + vacparameters + "' -m 5 --silent -k " + header).read())
		startup(dev)
	except:
		vacurl = "https://dashboard.aylanetworks.com"
		resp = ""#{}
		vacparameters = '/sessions/create'#&min_position=' + nextpos
		header = " --data 'email=" + email + "&password=" + psswrd + "'"
		header = header + " -i -j -L -b non-existing"
		header = header + " --compressed"
		try:
			resp = os.popen('curl ' + header + ' -m 5 -k ' + vacurl + vacparameters).read()
			stop0 = resp.find('/#/login/')
			stop1 = resp.find('server:',stop0)
			#stop1 = resp.find('server:',stop0)
			token = resp[stop0+9:stop1-1]
			#DE.Log("Python: " +stop0 + ", " + stop1 + token)
			updatevar("AylaToken",2,token)
			vacurl = "https://ads-field.aylanetworks.com/apiv1/devices"
			vacparameters = ".json?env=field_production"
			header = " -H 'authorization: auth_token " + token + "'"
			header = header + " -H 'authority: ads-field.aylanetworks.com' -H 'accept: application/json, text/plain, */*' -H 'cache-control: max-age=0' -H 'origin: https://dashboard.aylanetworks.com' -H 'sec-fetch-site: same-site' -H 'sec-fetch-mode: cors' -H 'referer: https://dashboard.aylanetworks.com/' -H 'accept-encoding: gzip, deflate, br' -H 'accept-language: en-US,en;q=0.9' --compressed"
			header = header + " -j -L -b non-existing"
			try:
				dev = json.loads(os.popen("curl '" + vacurl + vacparameters + "' -m 5 --silent -k " + header).read())
				startup(dev)
			except:
				DE.Log("Python: " + "Can't connect to: " + vacurl + vacparameters)
		except:
			DE.Log("Python: " + "Can't connect to: " + vacurl + vacparameters)
else:
	VcNm = getvar("VacName")

try:
	dev = json.loads(os.popen("curl '" + vacurl + vacparameters + "' -m 5 --silent -k " + header).read())
	DE.Log("Python: " + VcNm + " " + str(dev[0]['device']['connection_status']))
	if dev[0]['device']['connection_status'] == "Online":
		#DE.Log("Python: " + VcNm + " " + str(dev[0]['device']['key']))
		#DE.Log("Python: " + dev)
		vacparameters = "/" + str(dev[0]['device']['key']) + "/properties.json?env=field_production"
		#DE.Log("Python: " + vacurl + vacparameters)
		try:
			params = getVacVal(json.loads(os.popen("curl '" + vacurl + vacparameters + "' -m 5 --silent -k " + header).read()))
			#DE.Log("Python: " + os.popen("curl '" + vacurl + vacparameters + "' -m 5 --silent -k " + header).read())
			#getVacVal(params)
			updateDomoDevs(params)
		except:
			DE.Log("Python: " + "Can't connect to: " + vacurl + vacparameters)
	else:
		DE.Log("Python: " + "Vacuum not connected!")
except:
	vacurl = "https://dashboard.aylanetworks.com"
	resp = ""#{}
	vacparameters = '/sessions/create'#&min_position=' + nextpos
	header = " --data 'email=" + email + "&password=" + psswrd + "'"
	header = header + " -i -j -L -b non-existing"
	header = header + " --compressed"
	try:
		resp = os.popen('curl ' + header + ' -m 5 -k ' + vacurl + vacparameters).read()
		stop0 = resp.find('/#/login/')
		stop1 = resp.find('server:',stop0)
		token = resp[stop0+9:stop1-1]
		updatevar("AylaToken",2,token)
		#DE.Log("Python: " + token)
		vacurl = "https://ads-field.aylanetworks.com/apiv1/devices"
		vacparameters = ".json?env=field_production"
		header = " -H 'authorization: auth_token " + token + "'"
		header = header + " -H 'authority: ads-field.aylanetworks.com' -H 'accept: application/json, text/plain, */*' -H 'cache-control: max-age=0' -H 'origin: https://dashboard.aylanetworks.com' -H 'sec-fetch-site: same-site' -H 'sec-fetch-mode: cors' -H 'referer: https://dashboard.aylanetworks.com/' -H 'accept-encoding: gzip, deflate, br' -H 'accept-language: en-US,en;q=0.9' --compressed"
		header = header + " -j -L -b non-existing"
		try:
			dev = json.loads(os.popen("curl '" + vacurl + vacparameters + "' -m 5 --silent -k " + header).read())
			DE.Log("Python: " + VcNm + " " + str(dev[0]['device']['connection_status']))
			if dev[0]['device']['connection_status'] == "Online":
				#DE.Log("Python: " + VcNm + " " + str(dev[0]['device']['key']))
				#DE.Log("Python: " + dev)
				vacparameters = "/" + str(dev[0]['device']['key']) + "/properties.json?env=field_production"
				#DE.Log("Python: " + vacurl + vacparameters)
				try:
					params = getVacVal(json.loads(os.popen("curl '" + vacurl + vacparameters + "' -m 5 --silent -k " + header).read()))
					#DE.Log("Python: " + DE.Devices[VcNm + " Battery"].s_value)
					#getVacVal(params)
					updateDomoDevs(params)
				except:
					DE.Log("Python: " + "Can't connect to: " + vacurl + vacparameters)
			else:
				DE.Log("Python: " + "Vacuum not connected!")
		except:
			DE.Log("Python: " + "Can't connect to: " + vacurl + vacparameters)
	except:
		DE.Log("Python: " + "Can't connect to: " + vacurl + vacparameters)
