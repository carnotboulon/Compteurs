import urllib2
import json
import time



saveLocalTemperatureToDb():
    #f = urllib2.urlopen("http://api.wunderground.com/api/e93d8e80b8d925a2/geolookup/conditions/q/ebbr.json")
    f = urllib2.urlopen("http://api.wunderground.com/api/e93d8e80b8d925a2/geolookup/conditions/q/pws:IKRAAINE5.json")
    jsonstring = f.read()
    parsed_json = json.loads(jsonstring)
    temp_f = parsed_json["current_observation"]["temp_c"]
    epoch = parsed_json["current_observation"]["local_epoch"]
    timeString = time.strftime("%d/%m/%Y %H:%M:%S",time.localtime(float(epoch)))
    f.close()
    
