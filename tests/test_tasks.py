from datetime import datetime, timedelta
from time import sleep
from unittest import TestCase
from unittest.mock import patch
from sqlalchemy import text
from werkzeug.http import http_date

from src import create_app
from src.db import db
from src.tasks import DATETIME_FORMAT

from tests.config import TestConfig

class ApiTestCase(TestCase):
    def setUp(self) -> None:
        self.app = create_app(TestConfig())
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        with self.app.app_context():
            db.session.execute(text("TRUNCATE task, apscheduler_jobs;"))
            db.session.commit()

        super().tearDown()

    def test_GET_tasks_returns_empty_list_given_no_tasks(self):
        response = self._get_tasks()
        
        tasks = response.json
        
        self.assertEqual(0, len(tasks))

    def test_POST_task_schedules_task_at_specified_time(self):
        time = datetime.now() + timedelta(days=1)
        lines = "bakerloo,victoria"

        response = self._post_tasks(time, lines)

        self.assertEqual(201, response.status_code)
        self.assertIsNotNone(response.text)

        task_id = response.text
        tasks = self._get_tasks().json
        expected = {
            "id": task_id,
            "scheduled_time": http_date(time),
            "lines": lines,
            "is_complete": False,
            "is_success": False,
            "executed_time": None,
            "result": None,
        }

        self.assertEqual(1, len(tasks))
        self.assertEqual(expected, tasks[0])

    def test_GET_tasks_can_return_multiple_tasks(self):
        time = datetime.now() + timedelta(days=1)

        self._post_tasks(time, "bakerloo,victoria")
        self._post_tasks(time, "central")

        tasks = self._get_tasks().json

        self.assertEqual(2, len(tasks))

    def test_GET_task_by_id(self):
        time = datetime.now() + timedelta(days=1)
        lines = "bakerloo,victoria"

        response = self._post_tasks(time, lines)
        task_id = response.text

        task = self._get_task(task_id)
    
        expected = {
            "id": task_id,
            "scheduled_time": http_date(time),
            "lines": lines,
            "is_complete": False,
            "is_success": False,
            "executed_time": None,
            "result": None,
        }

        self.assertEqual(expected, task.json)

    def test_GET_task_with_bad_id_gives_404(self):
        self._post_tasks(datetime.now() + timedelta(days=1), "bakerloo")
        response = self._get_task("not-a-real-id")
        self.assertEqual(404, response.status_code)

    def test_POST_tasks_with_no_time_schedules_task_immediately(self):
        with patch("src.tfl.get_disruption_info") as p:
            p.return_value = "Some disruption info"

            response = self._post_tasks(None, "bakerloo")
            task_id = response.text
            task = self._wait_for_task(task_id).json

        self.assertTrue(task["is_complete"])
        self.assertEqual("Some disruption info", task["result"])

    def test_PATCH_task_updates_task(self):
        response = self._post_tasks(datetime.now() + timedelta(days=1), "bakerloo")
        task_id = response.text

        new_time = datetime.now() + timedelta(days=2)
        new_lines = "victoria"
        self._patch_task(task_id, new_time, new_lines)

        task = self._get_task(task_id).json

        expected = {
            "id": task_id,
            "scheduled_time": http_date(new_time),
            "lines": new_lines,
            "is_complete": False,
            "is_success": False,
            "executed_time": None,
            "result": None,
        }

        self.assertEqual(expected, task)

    def test_PATCH_when_task_is_complete_gives_400_error(self):
        with patch("src.tfl.get_disruption_info") as p:
            p.return_value = "Some disruption info"

            response = self._post_tasks(None, "bakerloo")
            task_id = response.text
            self._wait_for_task(task_id)

        response = self._patch_task(task_id, datetime.now(), "victoria")
        self.assertEqual(400, response.status_code)

    def test_DELETE_can_delete_task(self):
        response = self._post_tasks(datetime.now() + timedelta(days=1), "bakerloo")
        task_id = response.text

        response = self._delete_task(task_id)

        self.assertEqual(200, response.status_code)

    def _get_tasks(self):
        return self.client.get("/tasks/")
    
    def _get_task(self, id: str):
        return self.client.get(f"/tasks/{id}")
    
    def _post_tasks(self, time: datetime, lines: str):
        return self.client.post("/tasks/", json={
            "scheduler_time": time.strftime(DATETIME_FORMAT) if time else None,
            "lines": lines
        })
    
    def _patch_task(self, id: str, time: datetime, lines: str):
        return self.client.patch(f"/tasks/{id}", json={
            "scheduler_time": time.strftime(DATETIME_FORMAT) if time else None,
            "lines": lines
        })
    
    def _delete_task(self, id: str):
        return self.client.delete(f"/tasks/{id}")
    
    def _wait_for_task(self, id: str, max_iters = 10):
        task = None
        iteration = 0
        while (
            iteration < max_iters and 
            (task is None or not task.json["is_complete"])
        ):
            sleep(1)
            task = self._get_task(id)
            iteration += 1

        if task is None:
            raise ValueError("Could not get task")
        
        return task




