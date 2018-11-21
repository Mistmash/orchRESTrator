import requests
import schedule
import time
import threading
import json
import os
import pprint
import sys
from flask import Flask
from flask import render_template
# Project Classes
from Agent import Agent
from Job import Job

app = Flask(__name__)

# Get the path to the agent config file
config_path = os.path.dirname(os.path.realpath(__file__)) + "\config.json"
agents = []

# Dictionary equating 'every' to code snippets for schedule-command construction
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


def agent_request(type, agent_ID):
    # HTTP Get Request method takes type [test/last/clean] and amkes a call to the server
    URL = "http://127.0.0.1:5001/"
    if(type == "test"):
        URL += "test"
        print("Making request to %s agent is %s" % (URL, agent_ID))
        print("Thread: %s" % threading.current_thread())
        r = requests.get(URL)
        print(r.text)
    elif(type == "last"):
        URL += "last"
        print("Making request to %s agent is %s" % (URL, agent_ID))
        print("Thread: %s" % threading.current_thread())
        r = requests.get(URL)
        print(r.text)
    elif(type == "clean"):
        URL += "clean"
        print("Making request to %s agent is %s" % (URL, agent_ID))
        print("Thread: %s" % threading.current_thread())
        r = requests.get(URL)
        print(r.text)
    else:
        # Handle error
        print("error")


def run_threaded(agent_request_func, type, agent_ID):
    # Threaded call to the agent_request method
    request_thread = threading.Thread(
        target=agent_request, args=([type, agent_ID]))
    request_thread.start()


def schedule_job(job, agent_id):
    # Create a schedule command for the Job passed
    schedule_command = ("schedule." + every_command[job.every][0])
    if (job.interval != 0):
        schedule_command += (str(job.interval) +
                             every_command[job.every][1] + "s")
    else:
        schedule_command += every_command[job.every][1]
    if(job.time != None):
        schedule_command += ".at('" + str(job.time) + "')"
    schedule_command += (".do(run_threaded, agent_request, 'test', '" +
                         str(agent_id) + "')" + ".tag('" + str(agent_id) + str(job.tag) + "')")
    print("Job Scheduled: " + schedule_command)
    eval(schedule_command)


def remove_scheduled_job(agent, job_tag):
    # Remove a job from the schedule using the agent id and job tag to specify
    schedule.clear(agent.id + job_tag)
    agent.remove_job(job_tag)


def load_agents_from_config(config_path):
    # Pull config file, create Agent and Job objects
    config = json.loads(open(config_path).read())
    for agent in config["agents"]:
        # Create an agent object for each in theconfig
        new_agent = Agent(agent["id"])
        agents.append(new_agent)
        for job in agent["jobs"]:
            # For each Job in each Agent in the config, create a Job object
            x, y = 0, None
            if ("interval" in job):
                x = job["interval"]
            if ("time" in job):
                y = job["time"]
            new_job = Job(job["tag"], job["every"], x, y)
            # pprint.pprint(new_job.toString())
            new_agent.add_job(new_job)


""" class Backend_Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # A flag to notify the thread that it should finish up and exit
        self.kill_received = False

    def run(self):
        while not self.kill_received:
            # Run all pending jobs on a 1 second tick
            schedule.run_pending()
            time.sleep(1) """


def run_backend():
    # Main loop
    while (True):
        # Run all pending jobs on a 1 second tick
        schedule.run_pending()
        time.sleep(1)


@app.route("/", methods=["GET"])
# Index where root of the app is ran and started
def index():
    return render_template("root.html", name="sam")


@app.route("/agents/", methods=["GET"])
def list_agents():
    # List all agents here
    agents_list = ""
    for agent in agents:
        agents_list += (agent.id + " ")
    return render_template("list_agents.html", agents=agents)


@app.route("/agents/delete")
def delete_agent():
    #
    return


@app.route("/agents/create")
def create_agent():

    return


@app.route("/agents/<string:agent_id>/")
def show_agent(agent_id):
    for agent in agents:
        if (agent.id == agent_id):
            return render_template("show_agent.html", agent=agent)
    return render_template("show_agent.html", agent=None)


# @app.route("/agents/<string:agent_id>/<integer:job>/")
# def delete_agenshow_jobt(agent_id):
#    return


# Startup load config and schedule all jobs from it
load_agents_from_config(config_path)
for agent in agents:
    for job in agent.jobs:
        schedule_job(job, agent.id)

if __name__ == "__main__":
    backend_thread = threading.Thread(target=run_backend)  # Backend_Worker()
    backend_thread.daemon = True
    backend_thread.start()
    # try:
    app.run()
    # except KeyboardInterrupt:
    #backend_thread.kill_recieved = True
