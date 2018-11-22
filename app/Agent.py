import pprint


class Agent:

    def __init__(self, id):
        # Agents have an identifier and a list of jobs
        self.id = id
        self.jobs = []

    def get_jobs(self):
        # list the scheduled jobs for this agent
        return self.jobs

    def add_job(self, job):
        # add a new job to list
        self.jobs.append(job)

    def remove_job(self, remove_tag):
        # remove the specifically tagged job from this agent
        for job in self.jobs:
            if(job.tag == remove_tag):
                # unschedule job
                self.jobs.remove(job)
