--- REST Orchestration Tool ---

--Introduction

ROTool is a python application which provides the capability to schedule REST API calls to multiple servers and log the responses of these HTTP requests.

The back end uses the Daniel Bader's schedule libaray found at https://schedule.readthedocs.io/en/stable/ to make threaded calls to functions at specific intervals or times. Interaction with the app is achieved through a front end web interface implemented using the Flask framework. Pages are rendered HTML files with functionality added via jQuery and JavaScript scripts. Agent configuration is stored in a local json file which is read on startup and written to whenever the program state changes.

--Classes

    -Agent
    Parameters:
        id
            The unique identifier of the Agent
        lastRun
            The time the Agent was last run, optional "" if not passed
        nextRun
            The time the Agent will next run, optional "" if not passed
        response
            The most recent response code recieved from the agent- optional "" if not passed

    Variables:
        jobs
            Agent initialized with an empty list of jobs to represent the schedule
        isRunning
            Boolean used to check if Agent is free for a request

    Functions:
        addJob
            Takes a job and adds it to Agent's list of jobs
        removeJob
            Takes a job and removes it from the Agent's list of jobs
        toString
            Describes the agent as a json, usually to store in the config

    -Job
    Parameters:
        tag
            Identifier for the job, combined with agent id makes a unique identifier
        every
            (second/minute/hour/week/Monday/Tuesday/Wednesday/Thursday/Friday/Saturday/Sunday)
        interval
            An integer that describes the schedule, optional "1" if not passed
        time
            An HH:mm 24 hour time variable that descirbes the schedule, optional "" if not passed

    Functions:
        toString
            Describes the agent as a json, usually to store in the config

    -Orchestrator
    Variables:
        every_command
            Dictionary equating 'every' data to code snippets for schedule-command construction
        agents
            The global list of currnet agents currently known to the application.
        app
            The main Flask object that is run to host the front end interface.
        lock
            A lock from the 'threading' library, used to prevent race conditions and corruption when writing to the config file.
        config
            Pulls the config from it's json file into a json data type to be used by the program.
    Functions:
        (taken directly from code comments)
        update_config
            Generate a new config file using the current global list of agents to build a json. Save json to the stored config path, return config json
        agent_request
            HTTP Get Request method takes type [test/last/clean] and server id makes a call to the specific server. Return string if server engaged or status code of request response
        run_threaded
            Function to make a threaded call to the agent_request function. Takes arguments for the above function
        schedule_job
            Function takes a job to create and an agent to target. Creates a command to schedule the job and evals it, returns the command as string
        delete_job_from_agent_and_schedule
            Function takes an agent and a job and removes the job passed returns boolean when completed
        create_job_for_agent_and_schedule
            Function takes an agent and a job and adds the job passed to the agent returns boolean
        edit_job_for_agent_and_schedule
            Function takes an agent and a job, replaces the same named job within the agent
        is_job_valid
            Function takes a job and returns 6 booleans descirbing it's validity
        validity_string
            Takes a validity boolean list, a job and a request type and returns an error string. String to be displayed to user on web front end as an alert
        run_backend
            Function runs the back end loop to run scheduled jobs
        MAIN
            Create Agent and Job objects from config file and hold in global list. Schedule all jobs for all agents in the global list. Create seperate thread for back end function and initiate. Run the front end app.

    -RESTserver
    The RESTsevrer file is a test harness which replicates the behaviour of the agent end points that the app will send requests to in production. The python file hosts a web interface using flask, similar to the

--HTML Files

    -list_agents
    Navbar:
    Includes the name of the application and an interactive site map, allowing navigation between pages. Also includes a refresh button on the pages that display live data and information regarding the current page. Features on every page of the web app and should be adpated into a template eventually

    Table:
    Columns
        Agent ID, displays the unique identifier of the agent
        Requests, contains buttons to initiate manual requests (Test & Cancel)
        Last Run, displays the time the agent was last sent a request
        Response Code, displays the response code of the last request made to the agent
        Status, displays the current state of the request (Running/Waiting)
        Next Run, displays the time the agent will next send a request
        Functions, contains buttons to edit the agent (Delete & Edit)
    Row 1
        The first row of the table is used for the creation of new agents, taking a text input from the "Agent ID" column and being initiated with the fa-plus icon button in the "Functions" column.
    Row >1
        The rest of the rows of the table are populated by the agents in the global agents list.

    -edit_agent
    Navbar:
    See above~

    Table:
    Columns
        Job Tag, displays the identifier for the job (unique within this agent)
        Every, describes the frequency of the request
        Interval, describes the frequency of the request
        Time, describes the time that a request is sent
        Functions, contains buttons to edit the agent (Delete & Edit)
    Row <n
        Most of the rows of the table are populated by the scheduled jobs in the current agents jobs list. They can be edited or deleted by using the buttons in the "Functions" column.
    Row n
        The last row of the table is used for the creation of new job scheduels, taking a text or select input from the "Job Tag", "Every", "Interval" and "Time" columns, and being initiated with the fa-plus icon button in the "Functions" column.
