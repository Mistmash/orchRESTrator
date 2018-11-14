import requests
import schedule
import time
import threading
import json
import os
import pprint
import Agent
import Job

config_path = os.path.dirname(os.path.realpath(__file__)) + "\config.json"


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


config = json.loads(open(config_path).read())
pprint.pprint(config)
for agent in config['agents']:
    pprint.pprint(agent)

schedule.every(5).seconds.do(run_threaded, job, 1).tag('1')
schedule.every(10).seconds.do(run_threaded, job, 2).tag('2')


# while True:
#    schedule.run_pending()
#    time.sleep(1)
