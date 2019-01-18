class Job:
    def __init__(self, tag, every, interval="1", time="None"):
        # Constructor
        self.tag = tag
        self.every = every
        if(interval == "0" or interval == ""):
            self.interval = "1"
        else:
            self.interval = interval
        if(time == ""):
            self.time = "None"
        else:
            self.time = time

    def toString(self):
        # Retunr a string describing the job
        return('{"tag": "%s", "every": "%s", "interval": "%s", "time": "%s"}'
               % (self.tag, self.every, self.interval, self.time))
