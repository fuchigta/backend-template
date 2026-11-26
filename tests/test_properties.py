"""Property-based tests for the task domain logic (TaskDatabase and models).

The HTTP layer is covered by tests/test_api.py and the schemathesis contract
tests; these tests target the in-memory database and the Pydantic models
directly. Every example builds a fresh TaskDatabase instead of the global
``db`` singleton so that no state leaks between examples.
"""

from datetime import UTC, datetime
from typing import Any

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, invariant, rule
from pydantic import ValidationError

from src.api.database import TaskDatabase
from src.api.models import Task, TaskCreate, TaskUpdate

# Same budget as the proptest suites in the Rust projects.
MAX_EXAMPLES = 64

UPDATABLE_FIELDS = ("title", "description", "completed")

# title has no length constraint (the empty string is valid);
# description requires at least one character.
titles = st.text()
descriptions = st.text(min_size=1)

task_creates = st.builds(TaskCreate, title=titles, description=descriptions)

update_fields = st.fixed_dictionaries(
    {},
    optional={
        "title": titles,
        "description": descriptions,
        "completed": st.booleans(),
    },
)
task_updates = update_fields.map(TaskUpdate.model_validate)


class TaskDatabaseMachine(RuleBasedStateMachine):
    """Runs random create/get/update/delete sequences against a simple model.

    The model is a dict of Task snapshots keyed by ID; dict insertion order
    mirrors creation order, so it also serves as the expected listing order.
    """

    ids = Bundle("ids")

    def __init__(self) -> None:
        super().__init__()
        self.db = TaskDatabase()
        self.model: dict[int, Task] = {}
        self.issued = 0

    @rule(target=ids, data=task_creates)
    def create(self, data: TaskCreate) -> int:
        task = self.db.create_task(data)
        self.issued += 1
        # IDs are sequential from 1 and never reused, even after deletes.
        assert task.id == self.issued
        assert (task.title, task.description) == (data.title, data.description)
        assert task.completed is False
        assert task.created_at == task.updated_at
        self.model[task.id] = task.model_copy()
        return task.id

    @rule(task_id=ids)
    def get(self, task_id: int) -> None:
        assert self.db.get_task(task_id) == self.model.get(task_id)

    @rule(task_id=ids, update=task_updates)
    def update(self, task_id: int, update: TaskUpdate) -> None:
        before = self.model.get(task_id)
        result = self.db.update_task(task_id, update)
        if before is None:
            assert result is None
            return
        assert result is not None
        sent = update.model_dump(exclude_unset=True)
        for field in UPDATABLE_FIELDS:
            # Sent fields take the new value; unsent fields stay unchanged.
            assert getattr(result, field) == sent.get(field, getattr(before, field))
        assert result.id == task_id
        assert result.created_at == before.created_at
        assert result.updated_at >= before.updated_at
        self.model[task_id] = result.model_copy()

    @rule(task_id=ids)
    def delete(self, task_id: int) -> None:
        assert self.db.delete_task(task_id) is (task_id in self.model)
        self.model.pop(task_id, None)
        assert self.db.get_task(task_id) is None

    @rule(task_id=st.integers(), update=task_updates)
    def operate_on_missing_id(self, task_id: int, update: TaskUpdate) -> None:
        assume(task_id not in self.model)
        assert self.db.get_task(task_id) is None
        assert self.db.update_task(task_id, update) is None
        assert self.db.delete_task(task_id) is False

    @invariant()
    def listing_matches_model_in_insertion_order(self) -> None:
        assert self.db.get_all_tasks() == list(self.model.values())

    @invariant()
    def updated_at_never_precedes_created_at(self) -> None:
        for task in self.db.get_all_tasks():
            assert task.created_at <= task.updated_at


TestTaskDatabaseStateful = TaskDatabaseMachine.TestCase
TestTaskDatabaseStateful.settings = settings(max_examples=MAX_EXAMPLES)


@settings(max_examples=MAX_EXAMPLES)
@given(
    title=titles,
    description=descriptions,
    created_at=st.datetimes(),
    updated_at=st.datetimes(),
)
def test_serialized_timestamps_are_iso8601_with_z_suffix(
    title: str, description: str, created_at: datetime, updated_at: datetime
) -> None:
    # TaskDatabase stores naive datetimes, so naive ones are generated here.
    task = Task(
        id=1,
        title=title,
        description=description,
        completed=False,
        created_at=created_at,
        updated_at=updated_at,
    )
    dumped = task.model_dump(mode="json")
    for key, original in (("created_at", created_at), ("updated_at", updated_at)):
        serialized = dumped[key]
        assert serialized.endswith("Z")
        assert datetime.fromisoformat(serialized) == original.replace(tzinfo=UTC)


@settings(max_examples=MAX_EXAMPLES)
@given(title=titles, description=descriptions)
def test_task_create_accepts_any_title_and_non_empty_description(
    title: str, description: str
) -> None:
    task = TaskCreate(title=title, description=description)
    assert (task.title, task.description) == (title, description)


@settings(max_examples=MAX_EXAMPLES)
@given(title=titles)
def test_task_create_rejects_empty_description(title: str) -> None:
    with pytest.raises(ValidationError):
        TaskCreate(title=title, description="")


@settings(max_examples=MAX_EXAMPLES)
@given(fields=update_fields)
def test_task_update_dumps_only_sent_fields(fields: dict[str, Any]) -> None:
    assert TaskUpdate(**fields).model_dump(exclude_unset=True) == fields


@settings(max_examples=MAX_EXAMPLES)
@given(fields=update_fields, null_field=st.sampled_from(UPDATABLE_FIELDS))
def test_task_update_rejects_explicit_null(
    fields: dict[str, Any], null_field: str
) -> None:
    with pytest.raises(ValidationError):
        TaskUpdate(**{**fields, null_field: None})


@settings(max_examples=MAX_EXAMPLES)
@given(fields=update_fields)
def test_task_update_rejects_empty_description(fields: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        TaskUpdate(**{**fields, "description": ""})
