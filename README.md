# Overview

Flask web app for shceduling calls to the TFL disruptions endpoint and storing the result in a database, using apscheduler for shceduling and SQLAlchemy with PostgreSQL backend.

## API:

`/tasks/`
    - GET retreives all tasks (past and future)
        returns: JSON serialized tasks
    - POST creates a new task
        JSON data:
            - lines: string
            - scheduler_time: string (optional, if ommitted will use now)
        returns: task ID as string

`/tasks/<id>`
    - GET retreives specific task (will give 404 if not found)
        returns: JSON serialized task
    - PATCH updates a specific task
        JSON data:
            - lines: string
            - scheduler_time: string (optional, if ommitted will use now)
        returns: JSON serialized task with updated values
    - DELETE deletes a specific task
        returns: empty 200 status 


# Running the server

`docker-compose up`


# Running the tests

While server is running, `docker-compose exec web python -m unittest`


# Limitations

-   Does not support multiple users with various permissions and does not authenticate the user.
-   Input is not fully validated - if invalid lines are specified the user will not know until the task is executed.
-   Nothing to prevent multiple, identical tasks being scheduled at the same time.
-   Only includes end-to-end integration tests for the API, ideally would include finer grain unit tests as well.
-   Only one specific task supported - could be useful to allow a `task_type` to be specified in the POST request to change the task action.
