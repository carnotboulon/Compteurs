from regularExec import regularExec
import sched, time, datetime, os
import urllib
import urllib2
import json
from dataManager import dataManager as dm

timeout = 15                                    # Minutes between two measures.
db = dm()                                       # Creating db connection.
arduinoIP = "192.168.1.48"                      # IP adress of Arduino.

os.environ["TZ"] = "Europe/Brussels"            # Set time zone.

bufsize = 0
log = open("/home/pi/Desktop/compteurs.log", "w", bufsize)

def resetCompteurs():
    """ Reset compteurs to zero. Executed every day at midnight.
    """
    req = urllib2.Request("http://"+arduinoIP+"/reset")  #Building http request.
    res = urllib2.urlopen(req)
    data = res.read()
    log.write(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")+" > "+ data+"\n")
    
    
def getCompteursValues():
    """Connects to the compteurs to get their current values.
    Returns a dictionary with the compteur name and its value.
    """
    req = urllib2.Request("http://"+arduinoIP)  #Building http request.
    res = urllib2.urlopen(req)
    data = res.read()                           # Get data from request.
    compteurs = json.loads(data)                # decode json.
    return compteurs                               

def collect_data():
    """Executed every timeout. Connects to the compteurs, get their values and store them in the DB.
       Also restes the compteurs at midnight.
    """
    data = ""
    attempt = 0
    while data == "" and attempt < 3:
        try:
            data = getCompteursValues()                 # Get Compteur values from Arduino.    
        except:
            log.write("Attempt "+str(attempt)+" failed. Trying again in 3 seconds.\n")
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
    nextMeasureDay = datetime.datetime.fromtimestamp(int(time.time())+timeout*60).day
    if nextMeasureDay != currentMeasureDay: 
        db.saveDailyStat(t, gas, elec)
        resetCompteurs()

log.write("Starting Acquisition :"+datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")+"\n")

re = regularExec(collect_data, timeout)
re.run()
