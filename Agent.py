import pprint


class Agent:

    def __init__(self, id):
        # Agents have an identifier and a list of jobs
        self.id = id
        self.jobs = []

    def getJobs(self):
        # list the scheduled jobs for this agent
        return self.jobs

    def addJob(self, job):
        # add a new job to list
        self.jobs.append(job)

    def removeJob(self, tag):
        # remove the specifically tagged job from this agent
        print()
