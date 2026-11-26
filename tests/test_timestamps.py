"""Timestamps are generated and serialized as UTC, whatever the server timezone.

Every test here runs with the process timezone set to JST (UTC+9), so a
timestamp taken from the local clock, or a naive value read as local time,
lands nine hours away from the expected UTC instant and fails the test even
on CI runners that use UTC.
"""

import time
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from src.api.database import TaskDatabase, db
from src.api.main import app
from src.api.models import Task, TaskCreate, TaskUpdate

JST = timezone(timedelta(hours=9))


@pytest.fixture(autouse=True)
def non_utc_local_timezone(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    # POSIX TZ string, so no tz database is needed: "JST-9" means UTC+9.
    monkeypatch.setenv("TZ", "JST-9")
    time.tzset()
    yield
    monkeypatch.undo()
    time.tzset()


@pytest.fixture
def client() -> TestClient:
    db._tasks.clear()
    db._next_id = 1
    return TestClient(app)


def test_local_timezone_is_not_utc_during_these_tests() -> None:
    assert datetime.now().astimezone().utcoffset() == timedelta(hours=9)


def test_create_task_stores_aware_utc_timestamps() -> None:
    before = datetime.now(UTC)
    task = TaskDatabase().create_task(TaskCreate(title="t", description="d"))
    after = datetime.now(UTC)

    assert task.created_at.utcoffset() == timedelta(0)
    assert task.updated_at.utcoffset() == timedelta(0)
    assert before <= task.created_at <= after
    assert task.updated_at == task.created_at


def test_update_task_stores_aware_utc_updated_at() -> None:
    database = TaskDatabase()
    task = database.create_task(TaskCreate(title="t", description="d"))

    before = datetime.now(UTC)
    updated = database.update_task(task.id, TaskUpdate(title="new"))
    after = datetime.now(UTC)

    assert updated is not None
    assert updated.updated_at.utcoffset() == timedelta(0)
    assert before <= updated.updated_at <= after


def test_api_created_timestamps_parse_back_to_the_current_utc_instant(
    client: TestClient,
) -> None:
    before = datetime.now(UTC)
    data = client.post("/tasks", json={"title": "t", "description": "d"}).json()
    after = datetime.now(UTC)

    for key in ("created_at", "updated_at"):
        assert data[key].endswith("Z")
        parsed = datetime.fromisoformat(data[key])
        assert parsed.utcoffset() == timedelta(0)
        assert before <= parsed <= after


def test_api_updated_at_parses_back_to_the_current_utc_instant(
    client: TestClient,
) -> None:
    task_id = client.post("/tasks", json={"title": "t", "description": "d"}).json()["id"]

    before = datetime.now(UTC)
    data = client.put(f"/tasks/{task_id}", json={"title": "new"}).json()
    after = datetime.now(UTC)

    assert data["updated_at"].endswith("Z")
    parsed = datetime.fromisoformat(data["updated_at"])
    assert before <= parsed <= after


def test_serialize_aware_utc_datetime_uses_z_not_offset() -> None:
    dt = datetime(2024, 1, 1, 0, 0, tzinfo=UTC)
    task = Task(
        id=1,
        title="t",
        description="d",
        completed=False,
        created_at=dt,
        updated_at=dt,
    )

    dumped = task.model_dump(mode="json")

    assert dumped["created_at"] == "2024-01-01T00:00:00Z"
    assert dumped["updated_at"] == "2024-01-01T00:00:00Z"


def test_serialize_aware_non_utc_datetime_converts_to_utc() -> None:
    dt = datetime(2024, 1, 1, 9, 0, tzinfo=JST)
    task = Task(
        id=1,
        title="t",
        description="d",
        completed=False,
        created_at=dt,
        updated_at=dt,
    )

    dumped = task.model_dump(mode="json")

    assert dumped["created_at"] == "2024-01-01T00:00:00Z"
    assert dumped["updated_at"] == "2024-01-01T00:00:00Z"


def test_serialize_naive_datetime_is_treated_as_utc() -> None:
    dt = datetime(2024, 1, 1, 9, 0)
    task = Task(
        id=1,
        title="t",
        description="d",
        completed=False,
        created_at=dt,
        updated_at=dt,
    )

    dumped = task.model_dump(mode="json")

    assert dumped["created_at"] == "2024-01-01T09:00:00Z"
    assert dumped["updated_at"] == "2024-01-01T09:00:00Z"


def test_serialize_keeps_microseconds() -> None:
    dt = datetime(2024, 1, 1, 9, 0, 0, 123456, tzinfo=JST)
    task = Task(
        id=1,
        title="t",
        description="d",
        completed=False,
        created_at=dt,
        updated_at=dt,
    )

    dumped = task.model_dump(mode="json")

    assert dumped["created_at"] == "2024-01-01T00:00:00.123456Z"
