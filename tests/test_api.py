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
    task_data = {"title": "Minimal task", "description": "Minimal description"}
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minimal task"
    assert data["description"] == "Minimal description"


def test_create_task_invalid(client: TestClient) -> None:
    response = client.post("/tasks", json={})
    assert response.status_code == 400


def test_create_task_empty_description(client: TestClient) -> None:
    task_data = {"title": "Test task", "description": ""}
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 400


def test_create_task_missing_description(client: TestClient) -> None:
    task_data = {"title": "Test task"}
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 400


def test_get_task(client: TestClient) -> None:
    # Create a task first
    task_data = {"title": "Test task", "description": "Test description"}
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
    task_data = {"title": "Original task", "description": "Original description"}
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
    task_data = {"title": "Task to delete", "description": "Description to delete"}
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
    client.post("/tasks", json={"title": "Task 1", "description": "Description 1"})
    client.post("/tasks", json={"title": "Task 2", "description": "Description 2"})

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 1"
    assert data[1]["title"] == "Task 2"


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_check_method_not_allowed(client: TestClient) -> None:
    response = client.post("/health")
    assert response.status_code == 405
    assert response.headers["Allow"] == "GET"
    assert "message" in response.json()


def test_tasks_collection_method_not_allowed(client: TestClient) -> None:
    response = client.delete("/tasks")
    assert response.status_code == 405
    assert response.headers["Allow"] == "GET, POST"


def test_task_item_method_not_allowed(client: TestClient) -> None:
    response = client.post("/tasks/1")
    assert response.status_code == 405
    assert response.headers["Allow"] == "GET, PUT, DELETE"


def test_not_found_has_no_allow_header(client: TestClient) -> None:
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert "Allow" not in response.headers


def test_trailing_slash_is_not_redirected(client: TestClient) -> None:
    response = client.get("/tasks/", follow_redirects=False)
    assert response.status_code == 404


def test_create_task_single_char_description(client: TestClient) -> None:
    task_data = {"title": "Test task", "description": "a"}
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 201
    assert response.json()["description"] == "a"


def test_create_task_timestamps_have_utc_suffix(client: TestClient) -> None:
    task_data = {"title": "Test task", "description": "Test description"}
    data = client.post("/tasks", json=task_data).json()
    assert data["created_at"].endswith("Z")
    assert data["updated_at"].endswith("Z")


def test_update_task_keeps_fields_not_sent(client: TestClient) -> None:
    task_data = {"title": "Original task", "description": "Original description"}
    task_id = client.post("/tasks", json=task_data).json()["id"]

    response = client.put(f"/tasks/{task_id}", json={"title": "Updated task"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated task"
    assert data["description"] == "Original description"
    assert data["completed"] is False


def test_update_task_single_char_description(client: TestClient) -> None:
    task_data = {"title": "Test task", "description": "Test description"}
    task_id = client.post("/tasks", json=task_data).json()["id"]

    response = client.put(f"/tasks/{task_id}", json={"description": "a"})
    assert response.status_code == 200
    assert response.json()["description"] == "a"


def test_update_task_empty_description(client: TestClient) -> None:
    task_data = {"title": "Test task", "description": "Test description"}
    task_id = client.post("/tasks", json=task_data).json()["id"]

    response = client.put(f"/tasks/{task_id}", json={"description": ""})
    assert response.status_code == 400


def test_update_task_null_title(client: TestClient) -> None:
    task_data = {"title": "Test task", "description": "Test description"}
    task_id = client.post("/tasks", json=task_data).json()["id"]

    response = client.put(f"/tasks/{task_id}", json={"title": None})
    assert response.status_code == 400
