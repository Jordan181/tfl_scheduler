from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.events import JobExecutionEvent, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from flask import Flask

from src.db import db, Task
from src.tfl import get_disruption_info


class TaskScheduler:
    def init_app(self, app: Flask) -> None:
        jobstores = {
            "default": SQLAlchemyJobStore(url=app.config["SQLALCHEMY_DATABASE_URI"])
        }
        self._app = app
        self._scheduler = BackgroundScheduler(jobstores=jobstores)
        self._scheduler.add_listener(self._on_job_event, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        self._scheduler.start()

    def get_tasks(self) -> list[Task]:
        return db.session.execute(db.select(Task)).scalars().all()

    def get_task(self, id: str) -> Task:
        return db.session.get(Task, id)

    def create_task(self, scheduler_time: datetime, lines: str) -> Task:
        job = self._scheduler.add_job(
            func=get_disruption_info,
            kwargs={
                "lines": lines,
            },
            trigger="date",
            run_date=scheduler_time,
        )

        task = Task(
            id = job.id,
            scheduled_time = scheduler_time,
            lines = lines,
        )

        db.session.add(task)
        db.session.commit()

        return task

    def update_task(self, task: Task, scheduler_time: datetime, lines: str) -> Task:
        if scheduler_time:
            task.scheduled_time = scheduler_time
        if lines:
            task.lines = lines
        
        db.session.commit()

    def delete_task(self, task: Task) -> None:
        db.session.delete(task)
        db.session.commit()

    def _on_job_event(self, event: JobExecutionEvent):
        with self._app.app_context():
            task = self.get_task(event.job_id)

            if task is None:
                return
            
            task.executed_time = datetime.now()
            task.is_complete = True
            
            if event.exception:
                task.is_success = False
                task.result = str(event.exception)
            else:
                task.is_success = True
                task.result = event.retval

            db.session.commit()

scheduler = TaskScheduler()
