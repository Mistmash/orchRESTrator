import requests
import schedule
import time
from datetime import datetime
import threading
import json
import os
import pprint
import sys
import re
from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
# Project Classes
from Agent import Agent
from Job import Job

# Initialize the front end
app = Flask(__name__)
app.config["FLASK3_FILEPATH_HEADERS"] = {
    r".css$": {
        "Content-Type": "text/css",
    }
}

# Get the path to the agent config file and pull it
config_path = os.path.dirname(os.path.realpath(__file__)) + "\config.json"
config = json.loads(open(config_path).read())

# Initialize globals
global agents
agents = []
lock = threading.Lock()

# Dictionary equating 'every' data to code snippets for schedule-command construction
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

# Generate a new config file using the current global list of agents to build a json
# Save json to the stored config path, return config json
def update_config():  
    newconf = '{ "agents": ['
    for agent in agents:
        newconf += agent.toString()
        newconf += ","
    newconf = newconf[:-1]
    newconf += ']}'
    newconf = json.loads(newconf)
    # A lock is used to prevent data corruption from race condition
    with lock:
        with open(config_path, 'w') as fp:
            json.dump(newconf, fp)
        return newconf

# HTTP Get Request method takes type [test/last/clean] and server id makes a call to the specific server
# Return string if server engaged or status code of request response
def agent_request(subdomain, agent_ID):  
    # *** Current test harness hosted on 127.0.0.1:5001 replace in live***
    URL = "http://127.0.0.1:5001/"
    URL += subdomain
    # *** ***
    for agent in agents:
        if agent_ID == agent.id:
            if agent.isRunning:
                resp = "Running " + subdomain + " to " + \
                    agent_ID + " cancelled, already running."
                print(resp)
                return resp
            else:
                agent.isRunning = True
                r = requests.get(URL)
                print(r.text)
                agent.isRunning = False
                agent.response = r.status_code
                update_config()
                return r.status_code

# Function to make a threaded call to the agent_request function
# Takes arguments for the above function
def run_threaded(agent_request_func, subdomain, agent_ID):
    request_thread = threading.Thread(
        target=agent_request, args=([subdomain, agent_ID]))
    # Log the call to the console
    for agent in agents:
        if agent.id == agent_ID:
            now = time.strftime("%d-%m-%Y %H:%M:%S")
            agent.lastRun = (now)
            print("Running " + subdomain + " to " + agent_ID + " at " + now)
    request_thread.start()

# Function takes a job to create and an agent to target
# Creates a command to schedule the job and evals it, returns the command as string
def schedule_job(job, agent):
    schedule_command = ("schedule." + every_command[job.every][0])
    if ((job.interval != "0") and (job.interval != "1") and (job.interval != "")):
        schedule_command += (str(job.interval) +
                             every_command[job.every][1] + "s")
    else:
        schedule_command += every_command[job.every][1]
    if(job.time != None and job.time != "None" and job.time != ""):
        schedule_command += ".at('" + str(job.time) + "')"
    schedule_command += (".do(run_threaded, agent_request, 'test', '" +
                         str(agent.id) + "')" + ".tag('" + str(agent.id) + str(job.tag) + "')")
    # Log the command used to schedule the job
    print("Job Scheduled: " + schedule_command)
    eval(schedule_command)
    return schedule_command

# Function takes an agent and a job and removes the job passed returns boolean when completed
def delete_job_from_agent_and_schedule(agent, job):
    # *** Handle error if agent or job does not exist ***
    # *** Try clear, catch return false ***
    schedule.clear(agent.id + job.tag)
    agent.remove_job(job.tag)
    update_config()
    return True

# Function takes an agent and a job and adds the job passed to the agent returns boolean
def create_job_for_agent_and_schedule(agent, job):
    # *** Handle error if agent or job does not exist ***
    # *** Try clear, catch return false ***
    agent.add_job(job)
    schedule_job(job, agent)
    update_config()
    return True

# Function takes an agent and a job, replaces the same named job within the agent
def edit_job_for_agent_and_schedule(agent, job):
    # First delete the job with same ID as the passed job
    delete_job_from_agent_and_schedule(agent, job)
    # Then create the new job object for the agent
    create_job_for_agent_and_schedule(agent, job)
    update_config()
    return True

# Function takes a job and returns 6 booleans descirbing it's validity
def is_job_valid(job):
    valid = [None, None, None, None, None, None]
    # 0: is the job tag an alphanumeric, min 1 and max 14 characters
    tag_pattern = re.compile('^\w{1,14}$')
    if(re.match(tag_pattern, job.tag)):
        valid[0] = True
    else:
        valid[0] = False
    # 1: does the 'every' value present in the every snippet dictionary
    if(job.every in every_command):
        valid[1] = True
    else:
        valid[1] = False
    # 2: is the 'interval' value an integer between 0 and 59 (empty string passes)
    try:
        if((int(job.interval) < 60) and (int(job.interval) >= 0)):
            valid[2] = True
        else:
            valid[2] = False
    except:
        if(job.interval == ""):
            valid[2] = True
        else:
            valid[2] = False
    # 3: is the 'time' value in standard 24 hour HH:mm format
    time_pattern = re.compile('^(2[0-3]|[01][0-9]):([0-5][0-9])$')
    if(bool(re.match(time_pattern, job.time)) or (job.time == "None") or (job.time == "")):
        valid[3] = True
    else:
        valid[3] = False
    # 4: if 'every' is hourly or more frequent and has a 'time' value then false
    if((job.every == "second" or job.every == "minute" or job.every == "hour")
       and (job.time != None and job.time != "" and job.time != "None")):
        valid[4] = False
    else:
        valid[4] = True
    # 5: if 'every' is a specific day of the week and interval is > 1 then false
    if((job.every == "monday" or job.every == "tuesday" or job.every == "wednesday" or
            job.every == "thursday" or job.every == "friday" or job.every == "saturday" or
            job.every == "sunday") and (job.interval != "0" and job.interval != "1" and job.interval != "")):
        valid[5] = False
    else:
        valid[5] = True
    return valid

# Takes a validity boolean list, a job and a request type and returns an error string
# String to be displayed to user on web front end as an alert
def validity_string(valid, new_job, agent, request_type):
    alert_string = ""
    if request_type == "create":
        for job in agent.jobs:
            if (job == new_job.tag):
                alert_string += "New tag already exists within this agent$$"
    if not valid[0]:
        alert_string += "Tag must be an alphanumeric of length 1-14$$"
    if not valid[1]:
        alert_string += "Every must be a choice from the dropdown menu$$"
    if not valid[2]:
        alert_string += "Interval must be an integer between 0 and 59$$"
    if not valid[3]:
        alert_string += "Time must be in the 24-hour format HH:mm$$"
    if not valid[4]:
        alert_string += "Second/Minute/Hour schedules cannot use a specific time$$"
    if not valid[5]:
        alert_string += "Weekday specific schedules cannot have an interval larger than 1"
    return alert_string

# Function runs the back end loop to run scheduled jobs
def run_backend():
    while (True):
        schedule.run_pending()
        time.sleep(0.1)

# Index page - currently unused
@app.route("/", methods=["GET"])
def index():
    return render_template("root.html", name="sam")

# Agents page
# GET - displays a list of all currently known agents
# PUT - adds a new agent to the global list
# POST - initiates a manual request to an agent
# DELETE - deletes an agent from a global list 
@app.route("/agents/", methods=["GET", "PUT", "POST", "DELETE"])
def list_agents():
    if request.method == "POST":
        resp = ""
        #print(request.json["id"])
        #print(request.json["requestType"])
        for agent in agents:
            if agent.id == request.json["id"]:
                if (request.json["requestType"] == "1"):
                    # requestType 1 coresponds to a manual TEST request
                    print("Manual TEST request to agent: " + agent.id)
                    run_threaded(agent_request, "test", request.json["id"])
                    resp = "test"
                elif (request.json["requestType"] == "2"):
                    # requestType 2 crresponds to a manual CLEAN request
                    print("Manual CLEAN request to agent: " + agent.id)
                    run_threaded(agent_request, "clean", request.json["id"])
                    resp = "clean"
                resp = make_response('{ "response" : "' + resp + '" }')
                resp.headers['Access-Control-Allow-Origin'] = '*'
                resp.status_code = 200
                return resp
        # 404
        resp = make_response()
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.status_code = 404
        return resp

    if request.method == "PUT":
        new_agent = Agent(request.json["id"], "", "")
        resp = ""
        unique = True
        # If the new agent ID already exists add error response
        for agent in agents:
            if(new_agent.id == agent.id):
                unique = False
                resp += "End point must have a unique ID$$"
        if unique:
            # If the ID is not alphanumeric of size 3-14 add error response
            tag_pattern = re.compile('^\w{3,14}$')
            if(not re.match(tag_pattern, new_agent.id)):
                resp += "ID must be an alphanumeric of length 3-14"
        if(resp == ""):
            resp = make_response('{ "response" : "' + resp + '" }')
            resp.headers['Access-Control-Allow-Origin'] = '*'
            agents.append(new_agent)
            update_config()
            resp.status_code = 200
        else:
            resp = make_response('{ "response" : "' + resp + '" }')
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.status_code = 400
        return resp

    elif request.method == "DELETE":
        for i in range(len(agents)):
            if agents[i].id == request.json["id"]:
                try:
                    resp = str(agents.pop(i))
                    update_config()
                except:
                    resp = "False"
                if resp != "False":
                    resp = make_response(
                        '{ "response" : "' + resp + '" }')
                    resp.headers['Access-Control-Allow-Origin'] = '*'
                    resp.status_code = 200
                else:
                    # If pop fails on global list return error response
                    resp = "The selected agent could not be deleted."
                    resp = make_response(
                        '{ "response" : "' + resp + '" }')
                    resp.headers['Access-Control-Allow-Origin'] = '*'
                    resp.status_code = 400
                return resp
        # 404
        resp = make_response()
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.status_code = 404
        return resp
    elif request.method == "GET":
        return render_template("list_agents.html", agents=agents, jobs=schedule.jobs)

# Specific Agents page
# GET - displays the jobs scheduled for the subdomain specified agent
# PUT - adds a new job to the specifc agent
# POST - edits an existing job for the specific agent
# DELETE - deletes an existing job for the current agent
@app.route("/agents/<string:agent_id>/", methods=["GET", "POST", "PUT", "DELETE"])
def edit_agent(agent_id):
    if request.method == "POST":
        for agent in agents:
            if (agent.id == agent_id):
                new_job = Job(request.json["tag"], request.json["every"],
                              request.json["interval"], request.json["time"])
                request_validity = is_job_valid(new_job)
                resp = make_response('{ "response" : "' + validity_string(
                    request_validity, new_job, agent, "edit") + '" }')
                resp.headers['Access-Control-Allow-Origin'] = '*'
                if(request_validity == [True, True, True, True, True, True]):
                    edit_job_for_agent_and_schedule(agent, new_job)
                    resp.status_code = 200
                else:
                    resp.status_code = 400
                return resp
        # 404
        resp = make_response()
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.status_code = 404
        return resp
    elif request.method == "PUT":
        for agent in agents:
            if (agent.id == agent_id):
                new_job = Job(request.json["tag"], request.json["every"],
                              request.json["interval"], request.json["time"])
                request_validity = is_job_valid(new_job)
                resp = make_response('{ "response" : "' + validity_string(
                    request_validity, new_job, agent, "edit") + '" }')
                resp.headers['Access-Control-Allow-Origin'] = '*'
                # print(request_validity)
                if(request_validity == [True, True, True, True, True, True]):
                    create_job_for_agent_and_schedule(agent, new_job)
                    resp.status_code = 200
                else:
                    resp.status_code = 400
                return resp
        # 404
        resp = make_response()
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.status_code = 404
        return resp
    elif request.method == "DELETE":
        for agent in agents:
            if agent.id == agent_id:
                new_job = Job(request.json["tag"], request.json["every"],
                              request.json["interval"], request.json["time"])
                resp = make_response(
                    '{ "response" : "' + str(delete_job_from_agent_and_schedule(agent, new_job)) + '" }')
                resp.headers['Access-Control-Allow-Origin'] = '*'
                resp.status_code = 200
                return resp
        # 404
        resp = make_response()
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.status_code = 404
        return resp
    elif request.method == "GET":
        for agent in agents:
            if (agent.id == agent_id):
                return render_template("edit_agent.html", agent=agent)
        return render_template("edit_agent.html", agent=None)
    else:
        # 405
        print()

# Main function, program runs from here
if __name__ == "__main__":
    # Create Agent and Job objects from config file and hold in global list
    for agent in config["agents"]:
        new_agent = Agent(agent["id"], agent["lastRun"],
                        agent["nextRun"], agent["response"])
        agents.append(new_agent)
        for job in agent["jobs"]:
            x, y = 1, "None"
            if ("interval" in job):
                x = job["interval"]
            if ("time" in job):
                y = job["time"]
            new_job = Job(job["tag"], job["every"], x, y)
            new_agent.add_job(new_job)

    # Schedule all jobs for all agents in the global list
    for agent in agents:
        for job in agent.jobs:
            schedule_job(job, agent)

    # Create seperate thread for back end function and initiate
    backend_thread = threading.Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()

    # Run the front end app
    app.run()