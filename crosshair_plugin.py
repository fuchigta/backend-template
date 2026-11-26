"""CrossHair plugin: teach CrossHair how to build symbolic task models.

CrossHair builds symbolic instances of a class by calling ``__init__`` with
symbolic arguments. Pydantic validates in pydantic-core (Rust), which cannot
accept symbolic values, so every attempt fails with ``ValidationError``. The
analysis then ends as UNKNOWN on every path, and ``crosshair check`` still
exits 0 ("no counterexample found") without having checked anything. The
factories below use ``model_construct`` instead, which skips validation and
stores the symbolic values directly.

Only the field values are symbolic. Pydantic's own validation rules (such as
``min_length=1``) are not analysed by CrossHair; tests cover them.

CrossHair runs this file with ``exec()`` inside one of its own functions, so
module-level names are not visible from the functions defined here. That is
why each factory imports what it needs itself.

Load with: ``crosshair check <target> --extra_plugin crosshair_plugin.py``
(the option takes several files, so put the target before it).
"""

from typing import Any

from crosshair import SymbolicFactory, register_type

from src.api.database import TaskDatabase
from src.api.models import Task, TaskUpdate


def _symbolic_task(factory: SymbolicFactory) -> Task:
    from datetime import datetime

    from src.api.models import Task

    return Task.model_construct(
        id=factory(int),
        title=factory(str),
        description=factory(str),
        completed=factory(bool),
        created_at=factory(datetime),
        updated_at=factory(datetime),
    )


def _symbolic_task_update(factory: SymbolicFactory) -> TaskUpdate:
    # Each field is either sent (with any value) or omitted; model_fields_set
    # records which ones were sent, as pydantic does for parsed requests.
    from src.api.models import TaskUpdate

    sent: dict[str, Any] = {}
    if factory(bool):
        sent["title"] = factory(str)
    if factory(bool):
        sent["description"] = factory(str)
    if factory(bool):
        sent["completed"] = factory(bool)
    return TaskUpdate.model_construct(**sent)


def _symbolic_task_database(factory: SymbolicFactory) -> TaskDatabase:
    # Any stored tasks and any next ID; the class invariants in TaskDatabase's
    # docstring restrict these to the states that create/delete can reach.
    from src.api.database import TaskDatabase
    from src.api.models import Task

    database = TaskDatabase()
    database._tasks = factory(dict[int, Task])
    database._next_id = factory(int)
    return database


register_type(Task, _symbolic_task)
register_type(TaskUpdate, _symbolic_task_update)
register_type(TaskDatabase, _symbolic_task_database)
