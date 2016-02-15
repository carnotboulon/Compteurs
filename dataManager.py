import os, sqlite3, time, datetime

# To create a table.
# db.cur.execute("CREATE TABLE Statistics (Id INTEGER PRIMARY KEY ASC, date INT, day INT, week INT, month INT, year INT, gas INT, elec INT)")

os.environ["TZ"] = "Europe/Brussels" 

class dataManager():

    DEBUG = True
    VERBOSITY = 1
    MONTHS = {"1":"jan","2":"feb","3":"mar","4":"apr","5":"may","6":"jun","7":"jul","8":"aug","9":"sep","10":"oct","11":"nov","12":"dec"}
    DAYS  ={"0":"Sun","1":"Mon","2":"Tue","3":"Wed","4":"Thu","5":"Fri","6":"Sat"}
    
    def __init__(self, dirPath = "/home/pi/Github/Compteurs", db = "CompteursData.db", table = "Measures"):
        self.path = dirPath
        self.db = db
        self.table = table
        self.con = ""
        os.chdir(self.path)
        
    def connectDB(self):
        self.con = sqlite3.connect(self.db)
        self.cur = self.con.cursor()
        if dataManager.DEBUG and dataManager.VERBOSITY > 1:
            print "Connected to DB."

    def closeDB(self):
        self.con.close()
        if dataManager.DEBUG and dataManager.VERBOSITY > 1:
            print "Connection closed."
        
    def getAllMeasures(self):
        self.connectDB()
        self.cur.execute("SELECT * FROM "+self.table)
        rows = self.cur.fetchall()
        self.closeDB()
        return rows

    def getLastMeasures(self, dataNumber=10):
        self.connectDB()
        self.cur.execute("SELECT * FROM "+self.table+" ORDER BY Id DESC LIMIT "+str(dataNumber))    
        rows = self.cur.fetchall()
        self.closeDB()
        return rows
        
    def deleteAllMeasures(self):
        self.executeSQLCommand("DELETE FROM "+self.table)
        if dataManager.DEBUG and dataManager.VERBOSITY > 0:
            print "Databased cleared."

    def executeSQLCommand(self, command):
        self.connectDB()
        self.cur.execute(command)
        self.con.commit()
        self.closeDB()

    def saveMeasure(self,timestamp, gas, elec):
        self.executeSQLCommand("INSERT INTO Measures VALUES(NULL,"+str(timestamp)+","+str(gas)+","+str(elec)+")")
        if dataManager.DEBUG and dataManager.VERBOSITY > 0:
            print "Saved measure >> "+str(timestamp)+" > "+str(gas)+" > "+str(elec)

    def saveDailyStat(self, epoch, gas, elec):
        date = time.strftime("%d",time.localtime(epoch))
        day = time.strftime("%w",time.localtime(epoch))
        week = time.strftime("%W",time.localtime(epoch))
        month = time.strftime("%m",time.localtime(epoch))
        year = time.strftime("%Y",time.localtime(epoch))
        com = "INSERT INTO Statistics VALUES(NULL,%s, %s, %s, %s, %s, %s, %s)" % (date, day, week, month, year, gas, elec)
        self.executeSQLCommand(com)
        if dataManager.DEBUG and dataManager.VERBOSITY > 0:
            print "Saved Stats >> date: %s - day: %s - week: %s - month: %s - year: %s - gas: %s - elec: %s" % (date, day, week, month, year, gas, elec)

    def getStats(self):
        com = "SELECT * FROM Statistics"
        return self.getDataFromDB(com)
    
    #Get today series.
    def getTodayData(self, timeFormat = "%H:%M"):
        rows = self.getTodayMeasures()
        todayData = {"time": [], "gas": [], "elec": []}
        previousGas = 0
        previousElec = 0
        for r in rows:
            todayData["time"].append(time.strftime(timeFormat,time.localtime(r[1])))
            todayData["gas"].append(r[2] - previousGas)
            todayData["elec"].append(r[3] - previousElec)
            previousGas = r[2]
            previousElec = r[3]
        return todayData

    def getWeeklyData(self, year, weekNum):
        data = {}
        com = "SELECT day,gas,elec FROM Statistics ORDER BY Id DESC LIMIT 7"
        rawData = self.getDataFromDB(com)
        data["time"] = [dataManager.DAYS[str(d[0])] for d in reversed(rawData)] # First element of the list is a tuple.
        data["gas"] = [d[1] for d in reversed(rawData)] # First element of the list is a tuple.
        data["elec"] = [d[2] for d in reversed(rawData)] # First element of the list is a tuple.
        return data

    def getYearlyData(self, year):
        data = {}
        com = "SELECT * FROM Statistics WHERE year = %s" % (year)
        rawData = self.getDataFromDB(com)
        elecData = {"jan":0,"feb":0,"mar":0,"apr":0,"may":0,"jun":0,"jul":0,"aug":0,"sep":0,"oct":0,"nov":0,"dec":0}
        gasData = {"jan":0,"feb":0,"mar":0,"apr":0,"may":0,"jun":0,"jul":0,"aug":0,"sep":0,"oct":0,"nov":0,"dec":0}
        for day in rawData:
            gasData[dataManager.MONTHS[str(day[4])]] += day[6]
            elecData[dataManager.MONTHS[str(day[4])]] += day[7]
             
        data["gas"] = [gasData["jan"], gasData["feb"], gasData["mar"], gasData["apr"], gasData["may"], gasData["jun"], gasData["jul"], gasData["aug"], gasData["sep"], gasData["oct"], gasData["nov"], gasData["dec"]] # First element of the list is a tuple.
        data["elec"] = [elecData["jan"], elecData["feb"], elecData["mar"], elecData["apr"], elecData["may"], elecData["jun"], elecData["jul"], elecData["aug"], elecData["sep"], elecData["oct"], elecData["nov"], elecData["dec"]]
        return data

    def getLastWeeks(self, numberOfWeeks):
        currentWeek = datetime.datetime.today().isocalendar()[1]
        currentYear = datetime.date.today().year
        # to be continued...

    def getLastMonths(self, numberOfMonths):
        currentMonth = datetime.date.today().month
        currentYear = datetime.date.today().year
        # to be continued...

    def getDataFromDB(self, com):
        self.connectDB()
        self.cur.execute(com)
        rows = self.cur.fetchall()
        self.closeDB()
        return rows
    
    def getMeasuresFromToDate(self, yearStart, monthStart, dayStart, hourStart, minutesStart, yearStop, monthStop, dayStop, hourStop, minutesStop):
        startTime = str(dayStart)+"/"+str(monthStart)+"/"+str(yearStart)+" "+str(hourStart)+":"+str(minutesStart)+":00"
        stopTime = str(dayStop)+"/"+str(monthStop)+"/"+str(yearStop)+" "+str(hourStop)+":"+str(minutesStop)+":00"
        startTimeStamp = int(time.mktime(time.strptime(startTime,"%d/%m/%Y %H:%M:%S")))
        stopTimeStamp = int(time.mktime(time.strptime(stopTime,"%d/%m/%Y %H:%M:%S")))
        self.connectDB()
        com = "SELECT * FROM "+self.table+" WHERE time BETWEEN "+str(startTimeStamp)+" AND "+str(stopTimeStamp)
        self.cur.execute(com)
        rows = self.cur.fetchall()
        self.closeDB()
        return rows

    def getMeasuresFromDate(self, year, month, day):
        return self.getMeasuresFromToDate(year,month, day, "00", "00", year, month, day, 23, "00")

    def getTodayMeasures(self):
        return self.getMeasuresFromDate(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)

    def epochToString(self, epoch, form="%d/%m/%Y %H:%M"):
        return time.strftime(form,time.localtime(epoch))

    def gazCountToCubicMeter(self, gasCount):
        return gasCount/1000.

    def elecCountToKwh(self, elecCount):
        return elecCount/600.
        
    def exportToCSV(self, fileName, dataList, raw = True, separator = ","):
        f = open(fileName, "w")
        f.write("id,time, gaz, elec\n")
        for r in dataList:
            if raw:
                line = "%d%s%s%s%d%s%d\n" % (r[0], separator, self.epochToString(r[1]), separator, r[2], separator, r[3])
            else:
                line = "%d%s%s%s%f%s%f\n" % (r[0], self.epochToString(r[1]), self.gazCountToCubicMeter(r[2]), self.elecCountToKwh(r[3]))
            f.write(line)
        f.close()
    
    def exportToJSON(self, dataList, raw=True):
        json = "?(\n["
        for r in dataList[:-1]:
            if raw:
                json += "[%d, %d, %d]\n," % (r[1], r[2], r[3])
            else:
                json += "[%s, %f, %f]\n," % (self.epochToString(r[1]), self.gazCountToCubicMeter(r[2]), self.elecCountToKwh(r[3]))
                
        if raw:
            json += "[%d, %d, %d]\n" % (dataList[-1][1], dataList[-1][2], dataList[-1][3])
        else:
            json += "[%s, %f, %f]\n" % (self.epochToString(dataList[-1][1]), self.gazCountToCubicMeter(dataList[-1][2]), self.elecCountToKwh(dataList[-1][3]))
        json += "]);"
        return json


        
