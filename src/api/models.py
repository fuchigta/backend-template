from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    field_serializer,
    field_validator,
)


class TaskBase(BaseModel):
    title: str
    description: str = Field(min_length=1)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = Field(None, min_length=1)
    completed: StrictBool | None = None

    @field_validator("title", "description", "completed")
    @classmethod  # pragma: no mutate (pydantic adds classmethod itself)
    def reject_null(cls, value: object) -> object:
        """Reject explicit null values; omitted fields are fine."""
        if value is None:
            raise ValueError("null is not allowed")
        return value


class Task(TaskBase):
    model_config = ConfigDict(from_attributes=True)  # pragma: no mutate (never read)

    id: int
    completed: bool = False  # pragma: no mutate (always passed explicitly)
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime to ISO 8601 format with timezone."""
        return dt.isoformat() + "Z"


class ErrorResponse(BaseModel):
    message: str
