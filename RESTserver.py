from flask import Flask
from flask_restful import Api, Resource, reqparse
import time
import pprint
import datetime

app = Flask(__name__)

# This app is used to replicate the agent behaviour

# Set a cache for the agent
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

# Called when GET request to /test url recieved


@app .route('/test')
# Do some work for x amount of time
def runTest():
    for x in range(1, 5):
        time.sleep(10)
        print("Working for %d0 seconds..." % x)
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

# Called when GET request to /last url recieved


@app .route('/last')
def getLast():
    # Return the most recent addition to the cache
    return tests[0], 200
    # return

# Called when GET request to /clean url recieved


@app .route('/clean')
def cleanup():
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
    app.run()
