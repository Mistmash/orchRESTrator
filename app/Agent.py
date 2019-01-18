import pprint


class Agent:

    def __init__(self, id, lastRun="", nextRun="", response=""):
        # Constructor
        self.id = id
        self.jobs = []
        self.lastRun = lastRun
        self.nextRun = nextRun
        self.isRunning = False
        self.response = response

    def add_job(self, job):
        # Add a new job to list
        self.jobs.append(job)

    def remove_job(self, remove_tag):
        # Remove the specifically tagged job from this agent return false if job does not exist
        for job in self.jobs:
            if(job.tag == remove_tag):
                # unschedule job
                self.jobs.remove(job)
                return True
        return False

    def toString(self):
        # Return a string describing the agent
        string = '{"id": "' + self.id + '", "lastRun": "' + \
            str(self.lastRun) + '", "nextRun": "' + \
            str(self.nextRun) + '", "response": "' + \
            str(self.response) + '", "jobs": ['
        for job in self.jobs:
            string += job.toString()
            string += ","
        if len(self.jobs) != 0:
            string = string[:-1]
        string += ']}'
        return string
