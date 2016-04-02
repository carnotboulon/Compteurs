import sched, time, datetime

class regularExec():
    """Scheduler object that will be executed every hour every given time interval."""
    
    def __init__(self, functionToBeExecuted, timeout = 15):
        """__init__(self, functionToBeExecuted, timeout = 15)
        functionToBeExecuted is the function to be executed at every interval.
        timeout is the time interval in minutes at which the macro will be executed.
        """
        self.timeout = timeout      # Time at which it will be executed.
        self.dt = 10                # Interval in seconds to the next occurance.
        self.fct = functionToBeExecuted

        self.s = sched.scheduler(time.time, time.sleep)
        self.s.enter(self.timeout, 1, self.rerun, (self.s,))

    
    def setDeltaT(self):
        """calculateDeltaT(self)
        Calculates the interval in seconds to reach the next occurance.
        """
        nu = datetime.datetime.today()
        self.dt = (self.timeout - nu.minute%self.timeout)*60 - nu.second
        print "Current Time = %s:%s:%s >> delay = %s" % (nu.hour, nu.minute, nu.second, self.dt)

    
    def userFct(self):
        """ userFct(self)
        Executes user function. It's there to allow pre- and post-processing.
        """
        self.fct()

    
    def rerun(self, sc):
        """rerun(self, sc)
        Relaunch the scheduler with the new dt.
        """
        self.userFct()
        self.setDeltaT()
        sc.enter(self.dt, 1, self.rerun, (sc,))

    def run(self):
        """run(self)"""
        self.s.run()
