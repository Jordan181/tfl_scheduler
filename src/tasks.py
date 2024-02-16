from datetime import datetime
from typing import Any
from flask import Blueprint, Request, Response, request, abort, jsonify

from src.scheduler import scheduler


tasksBlueprint = Blueprint("tasks", __name__, url_prefix="/tasks")

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

@tasksBlueprint.route("/", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        tasks = scheduler.get_tasks()
        return jsonify(tasks)
    
    elif request.method == "POST":
        data = _extract_task_data(request)
        task = scheduler.create_task(**data)
        return Response(status=201, response=task.id)

@tasksBlueprint.route("/<string:id>", methods=["GET", "PATCH", "DELETE"])
def handle_task(id: str):
    task = scheduler.get_task(id)
    if task is None:
        abort(404, f"Task with id '{id}' not found.")

    if request.method == "GET":
        return jsonify(task)

    elif request.method == "PATCH":
        data = _extract_task_data(request)

        if task.is_complete:
            abort(400, "Task is already complete.")

        task = scheduler.update_task(task, **data)
        return jsonify(task)
    
    elif request.method == "DELETE":
        scheduler.delete_task(task)
        return Response(status=200)

def _extract_task_data(request: Request) -> dict[str, Any]:
    data = request.get_json()
    time = data.get("scheduler_time")
    lines = data.get("lines")
    return {
        "scheduler_time": datetime.strptime(time, DATETIME_FORMAT) if time else datetime.now(),
        "lines": lines,
    }
