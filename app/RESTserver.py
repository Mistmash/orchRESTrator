from flask import Flask
from flask_restful import Api, Resource, reqparse
from random import *
import time
import pprint
import datetime

app = Flask(__name__)

# This app is used to replicate the agent behaviour
tests = [
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
# Do some work for x amount of time
def runTest():
    x = randint(1, 9)
    for i in range(1, x):
        time.sleep(10)
        print("Working for %d0 seconds of %d0..." % (i, x))
    # Generate a dict based on the test ran
    testResult = {
        "Status": "Complete",
        "Result": "Failed",
        "Details": "Process shutdown, power failure",
        "Time": "15:55:21 14/11/2018"
    }
    # Add the dict to the cache
    tests.insert(0, testResult)
    pprint.pprint(str(tests[0]))
    # Return HTTP GET response to the app
    return str(tests[0]), 200


@app .route('/last')
def getLast():
    # Return the most recent addition to the cache
    return tests[0], 200


@app .route('/clean')
def cleanup():
    # Stop currently running scripts and try and reset application
    # Return success or fail
    now = datetime.datetime.now()
    cleanup_response = {
        "Status": "Complete",
        "Result": "Passed",
        "Details": "",
        "Time": str(now)
    }
    return str(cleanup_response), 200
    # return "Failed", 500


if __name__ == '__main__':
    app.run(port='5001')
