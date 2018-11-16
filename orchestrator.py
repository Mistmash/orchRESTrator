import requests
import schedule
import time
import threading
import json
import os
import pprint
from Agent import Agent
from Job import Job

config_path = os.path.dirname(os.path.realpath(__file__)) + "\config.json"
agents = []

every_command = dict(
    second=["every(", ").second"],
    minute=["every(", ").minute"],
    hour=["every(", ").hour"],
    day=["every(", ").day"],
    week=["every(", ").week"],
    monday=["every(", ").monday"],
    tuesday=["every(", ").tuesday"],
    wednesday=["every(", ").wednesday"],
    thursday=["every(", ").thursday"],
    friday=["every(", ").friday"],
    saturday=["every(", ").saturday"],
    sunday=["every(", ").sunday"]
)


def job(agent_ID):
    URL = 'http://127.0.0.1:5000/test'
    print("Making request to %s agent is %d" % (URL, agent_ID))
    r = requests.get(URL)
    print(r.status_code)
    print(r.text)
    print("Thread: %s" % threading.current_thread())


def run_threaded(job_func, agent_ID):
    job_thread = threading.Thread(target=job, args=([agent_ID]))
    job_thread.start()


def schedule_all_jobs(agents):
    for agent in agents:
        for job in agent.jobs:
            schedule_command = ("schedule." + every_command[job.every][0])
            if (job.interval != 0):
                schedule_command += (str(job.interval) +
                                     every_command[job.every][1] + "s")
            else:
                schedule_command += every_command[job.every][1]
            if(job.time != None):
                schedule_command += ".at(\"" + str(job.time) + "\")"
            schedule_command += (".do(run_threaded, job, " +
                                 str(agent.id) + ")" + ".tag('" + str(job.tag) + "')")
            print("Job Scheduled: " + schedule_command)
            eval(schedule_command)


# def schedule_job(job):
# if job.time == None:

# Pull config file and create Agent and Job objects
config = json.loads(open(config_path).read())
for agent in config['agents']:
    new_agent = Agent(agent['id'])
    agents.append(new_agent)
    for job in agent['jobs']:
        x, y = 0, None
        if ('interval' in job):
            x = job['interval']
        if ('time' in job):
            y = job['time']
        new_job = Job(job['tag'], job['every'], x, y)
        new_agent.addJob(new_job)


schedule_all_jobs(agents)

# schedule.every(5).seconds.do(run_threaded, job, 1).tag('1')
# schedule.every(10).seconds.do(run_threaded, job, 2).tag('2')


# while True:
#    schedule.run_pending()
#    time.sleep(1)
