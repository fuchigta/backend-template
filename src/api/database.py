from datetime import datetime

from .models import Task, TaskCreate, TaskUpdate


class TaskDatabase:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def create_task(self, task_data: TaskCreate) -> Task:
        now = datetime.now()
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
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[Task]:
        return list(self._tasks.values())

    def update_task(self, task_id: int, task_update: TaskUpdate) -> Task | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None

        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = datetime.now()
        return task

    def delete_task(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False


# Global database instance
db = TaskDatabase()
