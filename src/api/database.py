from datetime import UTC, datetime

from .models import Task, TaskCreate, TaskUpdate


class TaskDatabase:
    """In-memory task store.

    inv: all(task_id == task.id for task_id, task in self._tasks.items())
    inv: all(1 <= task_id < self._next_id for task_id in self._tasks)
    inv: list(self._tasks) == sorted(self._tasks)
    """

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def create_task(self, task_data: TaskCreate) -> Task:
        now = datetime.now(UTC)
        task = Task(
            id=self._next_id,
            title=task_data.title,
            description=task_data.description,
            completed=False,
            created_at=now,
            updated_at=now,
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get_task(self, task_id: int) -> Task | None:
        """
        post: (__return__ is None) == (task_id not in self._tasks)
        post: __return__ is None or __return__.id == task_id
        """
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[Task]:
        """
        post: [task.id for task in __return__] == sorted(self._tasks)
        """
        return list(self._tasks.values())

    def update_task(self, task_id: int, task_update: TaskUpdate) -> Task | None:
        """
        post[self]:
            (_ is None) == (task_id not in __old__.self._tasks)
            _ is None or _ == self.get_task(task_id)
            _ is None or _.created_at == __old__.self._tasks[task_id].created_at
            _ is None or _.updated_at.tzinfo is UTC
        """
        task = self._tasks.get(task_id)
        if task is None:
            return None

        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = datetime.now(UTC)
        return task

    def delete_task(self, task_id: int) -> bool:
        """
        post[self]: __return__ == (task_id in __old__.self._tasks)
        post: self.get_task(task_id) is None
        post: self._next_id == __old__.self._next_id
        post: len(self._tasks) == len(__old__.self._tasks) - __return__
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False


# Global database instance
db = TaskDatabase()
