import requests
import schedule
import time
import threading
import json
import os
import pprint
import sys
import re
from flask import Flask
from flask import render_template
from flask import request
# Project Classes
from Agent import Agent
from Job import Job

app = Flask(__name__)
app.config["FLASK3_FILEPATH_HEADERS"] = {
    r".css$": {
        "Content-Type": "text/css",
    }
}

# Get the path to the agent config file
config_path = os.path.dirname(os.path.realpath(__file__)) + "\config.json"
# Pull config file
config = json.loads(open(config_path).read())
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


def agent_request(subdomain, agent_ID):
    # HTTP Get Request method takes type [test/last/clean] and amkes a call to the server
    URL = "http://127.0.0.1:5001/"
    URL += subdomain
    print("Making %s request to %s agent is %s" % (subdomain, URL, agent_ID))
    print("Thread: %s" % threading.current_thread())
    r = requests.get(URL)
    print(r.text)


def run_threaded(agent_request_func, subdomain, agent_ID):
    # Threaded call to the agent_request method
    request_thread = threading.Thread(
        target=agent_request, args=([subdomain, agent_ID]))
    request_thread.start()


def schedule_job(job, agent_id):
    # Create a schedule command for the Job passed
    schedule_command = ("schedule." + every_command[job.every][0])
    if ((job.interval != 0) | (job.interval != 1)):
        schedule_command += (str(job.interval) +
                             every_command[job.every][1] + "s")
    else:
        schedule_command += every_command[job.every][1]
    if(job.time != "None"):
        schedule_command += ".at('" + str(job.time) + "')"
    schedule_command += (".do(run_threaded, agent_request, 'test', '" +
                         str(agent_id) + "')" + ".tag('" + str(agent_id) + str(job.tag) + "')")
    print("Job Scheduled: " + schedule_command)
    eval(schedule_command)


def delete_job_from_agent_and_schedule(agent, job):
    # Handle error if agent or job does not exist
    #
    # Remove a job from the schedule
    schedule.clear(agent.id + job.tag)
    # Remove the job from the agent's list of jobs
    agent.remove_job(job.tag)
    return True


def create_job_for_agent_and_schedule(agent, job):
    # Handle error where agent does not exist
    #
    # Add the job from the agent's list of jobs
    agent.add_job(job)
    # Schedule the job with the scheduler
    schedule_job(job, agent.id)
    return True


def edit_job_for_agent_and_schedule(agent, job):
    # Handle error if agent or job does not exist
    #
    delete_job_from_agent_and_schedule(agent, job)
    # Handle error if agent does not have this job
    #
    pprint.pprint(agent.toString())
    create_job_for_agent_and_schedule(agent, job)
    pprint.pprint(agent.toString())
    return True


def write_to_config():
    newconf = '{ "agents": ['
    for agent in agents:
        newconf += agent.toString()
        newconf += ","
    newconf = newconf[:-1]
    newconf += ']}'
    newconf = json.loads(newconf)
    with open(config_path, 'w') as fp:
        json.dump(newconf, fp)
    return True
    # pprint.pprint(config)


def is_job_valid(job):
    valid = [None, None, None, None, None]
    tag_pattern = re.compile("^\w{1,14}$")
    if(re.match(tag_pattern, job.tag)):
        valid[0] = True
    else:
        valid[0] = False
    if(job.every in every_command):
        valid[1] = True
    else:
        valid[1] = False
    try:
        if((int(job.interval) < 60) and (int(job.interval) >= 0)):
            valid[2] = True
        else:
            valid[2] = False
    except:
        valid[2] = False
    time_pattern = re.compile("^(2[0-3]|[01][0-9]):([0-5][0-9])$")
    if(bool(re.match(time_pattern, job.time)) or (job.time == "None")):
        valid[3] = True
    else:
        valid[3] = False
    if((job.every == "second" or job.every == "minute" or job.every == "hour") and (job.time != "None")):
        valid[4] = False
    else:
        valid[4] = True
    return valid


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


@app.route("/agents/<string:agent_id>/", methods=["GET", "POST", "PUT", "DELETE"])
def edit_agent(agent_id):
    if request.method == "POST":
        # POST request edits an existing Job, by deleting and creating a new one.
        new_job = Job(request.json["tag"], request.json["every"],
                      request.json["interval"], request.json["time"])
        print(is_job_valid(new_job))
        # Handle errors if the input is not valid
        if(is_job_valid(new_job) == [True, True, True, True, True]):
            for agent in agents:
                if (agent.id == agent_id):
                    edit_job_for_agent_and_schedule(agent, new_job)
                    break
        pprint.pprint(agent.toString())
        return render_template("edit_agent.html", agent=agent)
    for agent in agents:
        if (agent.id == agent_id):
            return render_template("edit_agent.html", agent=agent)
    return render_template("edit_agent.html", agent=None)


# Create Agent and Job objects
for agent in config["agents"]:
    # Create an agent object for each in the config
    new_agent = Agent(agent["id"])
    agents.append(new_agent)
    for job in agent["jobs"]:
        # For each Job in each Agent in the config, create a Job object
        x, y = 1, "None"
        if ("interval" in job):
            x = job["interval"]
        if ("time" in job):
            y = job["time"]
        new_job = Job(job["tag"], job["every"], x, y)
        # pprint.pprint(new_job.toString())
        new_agent.add_job(new_job)


for agent in agents:
    for job in agent.jobs:
        schedule_job(job, agent.id)

if __name__ == "__main__":
    backend_thread = threading.Thread(target=run_backend)  # Backend_Worker()
    backend_thread.daemon = True
    # backend_thread.start()
    write_to_config()
    # try:
    app.run()
    # except KeyboardInterrupt:
    # backend_thread.kill_recieved = True
