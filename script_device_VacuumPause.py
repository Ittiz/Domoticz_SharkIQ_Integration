import DomoticzEvents as DE
import os
import urllib.parse
import datetime
import json
import re
import html


def getvar(name):
	vro = os.popen('curl -m 1 --silent -k "http://127.0.0.1/json.htm?type=command&param=getuservariables" &').read()
	stop1 = vro.find('"' + name + '"')
	if stop1 > -1:
		stop1 = vro.find('"Value" : "',stop1)+11
		stop2 = vro.find('",',stop1)
		var = vro[stop1:stop2]
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

def getDevID(name):
	da = os.popen('curl -m 1 --silent  -k "http://127.0.0.1/json.htm?type=devices&filter=all&used=true" &').read()
	stop0 = da.find('"' + name + '"')
	if stop0 > -1:
		stop0 = da.find('"idx" : "',stop0)
		stop1 = da.find('"',stop0+10)
		return int(da[stop0+9:stop1])
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

#date_time = datetime.datetime.strptime(tstamp, '%I:%M %p - %d %b %Y').strftime("%s")
#end test setup

def getVacVal(array):
	newdict = {}
	for x in array:
		newdict[x['property']['name']] = x
	#DE.Log(newdict['GET_Charging_Status']['property']['name'])
	return newdict

stop0 = 0
stop1 = 0
token = ""
dev = {}
params = {}
VcNm = getvar("VacName") + " Pause"



TAG_RE = re.compile(r'<[^>]+>')
URL_RE = re.compile('http[^\s]*')
WS_RE = re.compile('\s+')
if DE.changed_device_name == VcNm:
	if (getvar("AylaToken") == None):
		createvar("AylaToken",2,"")
	else:
		token = getvar("AylaToken")
	vacurl = "https://ads-field.aylanetworks.com/apiv1/devices"
	vacparameters = ".json?env=field_production"


	header = " -H 'authorization: auth_token " + token + "'"
	header = header + " -H 'authority: ads-field.aylanetworks.com' -H 'accept: application/json, text/plain, */*' -H 'cache-control: max-age=0' -H 'origin: https://dashboard.aylanetworks.com' -H 'sec-fetch-site: same-site' -H 'sec-fetch-mode: cors' -H 'referer: https://dashboard.aylanetworks.com/' -H 'accept-encoding: gzip, deflate, br' -H 'accept-language: en-US,en;q=0.9' --compressed"
	header = header + " -j -L -b non-existing"

	try:
		dev = json.loads(os.popen("curl '" + vacurl + vacparameters + "' -m 5 --silent -k " + header).read())
		
		DE.Log("Python: " + VcNm + " " + str(dev[0]['device']['connection_status']))
		if dev[0]['device']['connection_status'] == "Online":
			DE.Log("Python: " + VcNm + " " + str(dev[0]['device']['key']))
			#DE.Log("Python: " + dev)
			vacparameters = "/" + str(dev[0]['device']['key']) + "/properties.json?env=field_production"
			#DE.Log("Python: " + vacurl + vacparameters)
			try:
				params = getVacVal(json.loads(os.popen("curl '" + vacurl + vacparameters + "' -m 5 --silent -k " + header).read()))
				#DE.Log("Python: " + DE.Devices[VcNm + " Battery"].s_value)
				vacurl = "https://ads-field.aylanetworks.com/apiv1/properties"
				vacparameters = "/" + str(params['SET_Operating_Mode']['property']['key']) + "/datapoints.json?env=field_production"
				header = "-H 'authorization: auth_token " + token + "'"
				header = header + "  -H 'accept: application/json, text/plain, */*' -H 'content-type: application/json;charset=UTF-8' -H 'accept-encoding: gzip, deflate, br'"
				packet = '{"id":' + str(params['SET_Operating_Mode']['property']['key']) + ',"datapoint":{"value":"0"}}'
				header = header + " -j -L --data-binary '" + packet + "' --compressed"
				#try:
				result = os.popen("curl '" + vacurl + vacparameters + "' -m 5 --silent -k " + header).read()
				DE.Log(result)
				#except:
				#	DE.Log("Python: " + "Can't connect to: " + vacurl + vacparameters)
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
			stop1 = resp.find('Server',stop0)
			token = resp[stop0+9:stop1-1]
			updatevar("AylaToken",2,token)
			DE.Log("Python: " + token)
			vacurl = "https://ads-field.aylanetworks.com/apiv1/devices"
			vacparameters = ".json?env=field_production"
			header = " -H 'authorization: auth_token " + token + "'"
			header = header + " -H 'authority: ads-field.aylanetworks.com' -H 'accept: application/json, text/plain, */*' -H 'cache-control: max-age=0' -H 'origin: https://dashboard.aylanetworks.com' -H 'sec-fetch-site: same-site' -H 'sec-fetch-mode: cors' -H 'referer: https://dashboard.aylanetworks.com/' -H 'accept-encoding: gzip, deflate, br' -H 'accept-language: en-US,en;q=0.9' --compressed"
			header = header + " -j -L -b non-existing"
			try:
				dev = json.loads(os.popen("curl '" + vacurl + vacparameters + "' -m 5 --silent -k " + header).read())
				
				DE.Log("Python: " + VcNm + " " + str(dev[0]['device']['connection_status']))
				if dev[0]['device']['connection_status'] == "Online":
					DE.Log("Python: " + VcNm + " " + str(dev[0]['device']['key']))
					#DE.Log("Python: " + dev)
					vacparameters = "/" + str(dev[0]['device']['key']) + "/properties.json?env=field_production"
					#DE.Log("Python: " + vacurl + vacparameters)
					try:
						params = getVacVal(json.loads(os.popen("curl '" + vacurl + vacparameters + "' -m 5 --silent -k " + header).read()))
						#DE.Log("Python: " + DE.Devices[VcNm + " Battery"].s_value)
						vacurl = "https://ads-field.aylanetworks.com/apiv1/properties"
						vacparameters = "/" + str(params['SET_Operating_Mode']['property']['key']) + "/datapoints.json?env=field_production"
						header = "-H 'authorization: auth_token " + token + "'"
						header = header + "  -H 'accept: application/json, text/plain, */*' -H 'content-type: application/json;charset=UTF-8' -H 'accept-encoding: gzip, deflate, br'"
						packet = '{"id":' + str(params['SET_Operating_Mode']['property']['key']) + ',"datapoint":{"value":"0"}}'
						header = header + " -j -L --data-binary '" + packet + "' --compressed"
						#try:
						result = os.popen("curl '" + vacurl + vacparameters + "' -m 5 --silent -k " + header).read()
						DE.Log(result)
						#except:
						#	DE.Log("Python: " + "Can't connect to: " + vacurl + vacparameters)
					except:
						DE.Log("Python: " + "Can't connect to: " + vacurl + vacparameters)
				else:
					DE.Log("Python: " + "Vacuum not connected!")
			except:
				DE.Log("Python: " + "Can't connect to: " + vacurl + vacparameters)
		except:
			DE.Log("Python: " + "Can't connect to: " + vacurl + vacparameters)



