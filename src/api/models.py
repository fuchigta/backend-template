from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class TaskBase(BaseModel):
    title: str
    description: str = Field(min_length=1)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = Field(None, min_length=1)
    completed: bool | None = None


class Task(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    completed: bool = False
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime to ISO 8601 format with timezone."""
        return dt.isoformat() + "Z"


class ErrorResponse(BaseModel):
    message: str
