import json
from flask import Flask
from flask import request
from flask import make_response
from flask_restful import Api, Resource, reqparse
from random import randint
import time
import pprint
import datetime

app = Flask(__name__)

# This app is used to replicate the production agent behaviour

# Holds an archive of recently completed agent tests
test_archive = [
    {
        "Status": "Complete",
        "Result": "Passed",
        "Details": "",
        "Time": "12:05:01 13/11/2018"
    },
    {
        "Status": "Complete",
        "Result": "Failed",
        "Details": "Process shutdown, power failure",
        "Time": "11:05:01 13/11/2018"
    }
]


@app .route('/test')
def runTest():
    # In production this code will initiate the software/hardware work on the agent
    # This work will be initiated by this porgram but executes as a separate bash file
    # This work should be monitored and error responses generated if running for too long

    # Generate a generic response dict
    now = time.strftime("%d-%m-%Y %H:%M:%S")
    testResult = '{ "Status": "Complete", "Result": "Passed", "Details": "", "Time": "'
    testResult += (now + '" }')
    testResult = json.loads(testResult)
    # Add the dict to the archive
    test_archive.insert(0, testResult)
    pprint.pprint(test_archive[0])
    # Currently simulate work as a random timed wait
    x = randint(1, 9)
    for i in range(1, x):
        time.sleep(10)
        print("Working for %d0 seconds of %d0..." % (i, x))
    # Return HTTP response to the app
    resp = make_response('{ "response" : "' + str(testResult) + '" }')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.status_code = 200
    return resp


@app .route('/last')
def getLast():
    # Return the most recent addition to the cache
    resp = make_response('{ "response" : "' + str(test_archive[0]) + '" }')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.status_code = 200
    return resp


@app .route('/clean')
def cleanup():
    # Stop currently running scripts and try and reset application
    # Currently return a placeholder response
    now = time.strftime("%d-%m-%Y %H:%M:%S")
    cleanup_response = '{ "Status": "Complete", "Result": "Passed", "Details": "", "Time": "'
    cleanup_response += (now + '" }')
    cleanup_response = json.loads(cleanup_response)
    return (cleanup_response, 200)


if __name__ == '__main__':
    app.run(port='5001')
