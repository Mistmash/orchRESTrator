class Job:
    def __init__(self, tag, increment, magnitude, time=None):
        self.tag = tag
        #AgentID + int
        self.increment = increment
        # second/minute/hour/week/Mon/Tue/Wed/Thur/Fri/Sat/Sun
        self.magnitude = magnitude
        # number of seconds, minutes etc
        self.time = time
        # HH:mm

    def scheduleJob(self):
        # creates and executes the command to add this job to the schedule
        print()

    def unscheduleJob(self):
        # creates and executes the command to clear this job from the schedule
        print()
