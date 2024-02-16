from dataclasses import dataclass
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Boolean, DateTime

db = SQLAlchemy()

@dataclass
class Task(db.Model):
    id: str = Column(String, primary_key=True)
    scheduled_time: datetime = Column(DateTime, nullable=False)
    lines: str = Column(String, nullable=False)
    is_complete: bool = Column(Boolean, default=False)
    is_success: bool = Column(Boolean, default=False)
    executed_time: datetime = Column(DateTime, nullable=True)
    result: str = Column(String, nullable=True)
