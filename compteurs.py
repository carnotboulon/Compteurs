import sched, time, datetime, os
import urllib
import urllib2
import json
from dataManager import dataManager as dm

timeout = 15*60                                    #Seconds
db = dm()                                       #creating db connection.
arduinoIP = "192.168.1.48"                      # IP adress of Arduino.

os.environ["TZ"] = "Europe/Brussels"            # Set time zone.

def resetCompteurs():
    req = urllib2.Request("http://"+arduinoIP+"/reset")  #Building http request.
    res = urllib2.urlopen(req)
    data = res.read()
    print datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")+" > "+ data

def getCompteursValues():
    req = urllib2.Request("http://"+arduinoIP)  #Building http request.
    res = urllib2.urlopen(req)
    data = res.read()                           # Get data from request.
    compteurs = json.loads(data)                # decode json.
    return compteurs                               

def collect_data():
    data = ""
    attempt = 0
    while data == "" and attempt < 3:
        try:
            data = getCompteursValues()                 # Get Compteur values from Arduino.    
        except:
            print "Attempt "+str(attempt)+" failed. Trying again in 3 seconds."
            time.sleep(3)
            attempt += 1
            data = ""

    if data != "":
        t = int(time.time())
        gas = data["gas"]
        elec = data["elec"]
        db.saveMeasure(t, gas, elec)     # Save measures in DB.
        db.saveLocalTemperatureToDb()
    # if last measure of the day: save daily statistics and reset compteurs. 
    currentMeasureDay = datetime.datetime.fromtimestamp(int(time.time())).day
    nextMeasureDay = datetime.datetime.fromtimestamp(int(time.time())+timeout).day
    if nextMeasureDay != currentMeasureDay: 
        db.saveDailyStat(t, gas, elec)
        resetCompteurs()


s = sched.scheduler(time.time, time.sleep)
def schedule_data_acquisition(sc):
    collect_data()
    sc.enter(timeout,1, schedule_data_acquisition, (sc,))    # Re-do same action in timeout seconds.

print "Starting Acquisition :"+datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
collect_data()
s.enter(timeout, 1, schedule_data_acquisition, (s,))         
s.run()


