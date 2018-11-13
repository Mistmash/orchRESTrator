import requests
import schedule
import time
import threading


def job(agentID):
    URL = 'https://9cc3523f-3b5a-4c60-b89b-b6cf1a6d6bea.mock.pstmn.io/'
    r = requests.get(URL)
    print("Agent ID: %d" % agentID)
    print(r.status_code)
    print(r.text)
    print("Thread: %s" % threading.current_thread())
    # print(r.json)


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


scheduleObject6 = schedule.every(5).seconds.do(job, 1).tag('Agent1')

while True:
    schedule.run_pending()
    time.sleep(1)
