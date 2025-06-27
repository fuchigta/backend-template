import pytest
from fastapi.testclient import TestClient

from src.api.database import db
from src.api.main import app


@pytest.fixture
def client() -> TestClient:
    # Reset database before each test
    db._tasks.clear()
    db._next_id = 1
    return TestClient(app)


def test_get_tasks_empty(client: TestClient) -> None:
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task(client: TestClient) -> None:
    task_data = {"title": "Test task", "description": "Test description"}
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["description"] == "Test description"
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_minimal(client: TestClient) -> None:
    task_data = {"title": "Minimal task"}
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minimal task"
    assert data["description"] is None


def test_create_task_invalid(client: TestClient) -> None:
    response = client.post("/tasks", json={})
    assert response.status_code == 400


def test_get_task(client: TestClient) -> None:
    # Create a task first
    task_data = {"title": "Test task"}
    create_response = client.post("/tasks", json=task_data)
    task_id = create_response.json()["id"]

    # Get the task
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test task"


def test_get_task_not_found(client: TestClient) -> None:
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert "message" in response.json()


def test_update_task(client: TestClient) -> None:
    # Create a task first
    task_data = {"title": "Original task"}
    create_response = client.post("/tasks", json=task_data)
    task_id = create_response.json()["id"]

    # Update the task
    update_data = {"title": "Updated task", "completed": True}
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated task"
    assert data["completed"] is True


def test_update_task_not_found(client: TestClient) -> None:
    update_data = {"title": "Updated task"}
    response = client.put("/tasks/999", json=update_data)
    assert response.status_code == 404


def test_delete_task(client: TestClient) -> None:
    # Create a task first
    task_data = {"title": "Task to delete"}
    create_response = client.post("/tasks", json=task_data)
    task_id = create_response.json()["id"]

    # Delete the task
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_task_not_found(client: TestClient) -> None:
    response = client.delete("/tasks/999")
    assert response.status_code == 404


def test_get_all_tasks_with_data(client: TestClient) -> None:
    # Create multiple tasks
    client.post("/tasks", json={"title": "Task 1"})
    client.post("/tasks", json={"title": "Task 2"})

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 1"
    assert data[1]["title"] == "Task 2"
