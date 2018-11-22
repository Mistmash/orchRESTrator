class Job:
    def __init__(self, tag, every, interval=1, time=None):
        self.tag = tag
        #AgentID + int
        self.every = every
        # second/minute/hour/week/Mon/Tue/Wed/Thur/Fri/Sat/Sun
        self.interval = interval
        # number of seconds, minutes etc
        self.time = time
        # HH:mm

    def scheduleJob(self):
        # creates and executes the command to add this job to the schedule
        print()

    def unscheduleJob(self):
        # creates and executes the command to clear this job from the schedule
        print()

    def toString(self):
        return("{'tag': '%s', 'every': '%s', 'interval': '%s', 'time': '%s'}" % (self.tag, self.every, self.interval, self.time))
