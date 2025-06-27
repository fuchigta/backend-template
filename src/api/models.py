from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskBase(BaseModel):
    title: str
    description: str | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class Task(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    completed: bool = False
    created_at: datetime
    updated_at: datetime


class ErrorResponse(BaseModel):
    message: str
