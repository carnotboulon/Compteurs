import tornado.ioloop
import tornado.web
import tornado.options
import tornado.template as tem
from dataManager import dataManager as dm
import os
import time, datetime

tornado.options.parse_command_line()

#Get Data from DB.
def dataExtractor(**kwargs):
    db = dm()
    if kwargs["when"] != "":
        if kwargs["when"] == "today":
            return db.exportToJSON(db.getTodayMeasures())
        else:
            date = kwargs["when"].split("-")
            return db.exportToJSON(db.getMeasuresFromDate(date[2],date[1],date[0]))

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        db = dm()
        mes = db.getLastMeasures(1)[0]
        loader = tem.Loader("/home/pi/Github/Compteurs/web")
        data = {}
        data["elecDailyAverage"]= 100.
        data["elecWeeklyAverage"]= 500.
        data["elecMonthlyAverage"]= 800.
        data["elecDaily"]= mes[3]
        data["elecWeekly"]= 450.
        data["elecMonthly"]= 1120.
        data["gazDailyAverage"]= 10.
        data["gazWeeklyAverage"]= 20.
        data["gazMonthlyAverage"]= 40.
        data["gazDaily"]= mes[2]
        data["gazWeekly"]= 25.
        data["gazMonthly"]= 35.
        self.write(loader.load("index-2.html").generate(data=data))

class TodayHandler(tornado.web.RequestHandler):
    def get(self):
        db = dm()
        data = {}
        data["time"]= []
        
        series = db.getTodayData()
        for t in series["time"]:
            s = "\"%s\"" % t
            data["time"].append(s)
        loader = tem.Loader("/home/pi/Github/Compteurs/web")

        currentIndexes = db.getLastMeasures(1)
        data["currentGasIndex"] = currentIndexes[0][2]
        data["currentElecIndex"] = currentIndexes[0][3]
        
        data["todayTime"]= str(series["time"])
        data["todayGas"]= str(series["gas"])
        data["todayElec"]= str(series["elec"])
        now = int(time.time())
        weekly = db.getWeeklyData(datetime.datetime.today().year, datetime.datetime.today().strftime("%W"))
        data["weeklyTime"]= weekly["time"]
        data["weeklyGas"]= weekly["gas"]
        data["weeklyElec"]= weekly["elec"]
        
        yearly = db.getYearlyData(datetime.datetime.today().year)
        data["yearlyGas"]= yearly["gas"]
        data["yearlyElec"]= yearly["elec"]
        self.write(loader.load("dayStats.html").generate(data=data))

# Gives data in JSON format.
# /data?when=today returns today measures.
# /data?when=dd-mm-yyyy returns data for the provided day.
class DataHandler(tornado.web.RequestHandler):
    def get(self):
        args = {}
        if self.get_arguments("when"):
            args["when"] = self.get_arguments("when")[0]
        if self.get_arguments("start"):
            args["start"] = self.get_arguments("start")[0]
            args["stop"] = self.get_arguments("stop")[0]
            if args["stop"] < args["start"]:
                args["stop"] = args["start"]
        data = dataExtractor(**args)    
        self.write(data)
    
print os.path.join(os.path.dirname(__file__))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/today", TodayHandler),
        (r"/data", DataHandler),
        (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": ""}),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {"path": "web/static"}),
        ],
        debug=True                           
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(80)
    
    tornado.ioloop.IOLoop.current().start()
