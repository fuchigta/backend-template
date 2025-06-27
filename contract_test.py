#!/usr/bin/env python3
"""
Simple contract test to verify API matches OpenAPI spec.
This is a basic implementation since dredd has configuration issues.
"""

import subprocess
import sys
import time

import requests


def start_server():
    """Start the FastAPI server."""
    return subprocess.Popen(
        ["uv", "run", "python", "main.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_for_server(max_wait=10):
    """Wait for server to be ready."""
    for _ in range(max_wait * 2):  # Check every 0.5 seconds
        try:
            response = requests.get("http://localhost:8000/tasks", timeout=1)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.5)
    return False


def test_contract():
    """Test API contract against OpenAPI spec."""
    base_url = "http://localhost:8000"

    # Test 1: GET /tasks (should return empty array initially)
    print("✓ Testing GET /tasks...")
    response = requests.get(f"{base_url}/tasks")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.json() == [], f"Expected empty array, got {response.json()}"

    # Test 2: POST /tasks (create task)
    print("✓ Testing POST /tasks...")
    task_data = {"title": "Test task", "description": "Test description"}
    response = requests.post(f"{base_url}/tasks", json=task_data)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    task = response.json()
    assert "id" in task, "Response should contain 'id'"
    assert task["title"] == "Test task", f"Expected 'Test task', got {task['title']}"
    assert task["completed"] is False, f"Expected False, got {task['completed']}"
    assert "created_at" in task, "Response should contain 'created_at'"
    assert "updated_at" in task, "Response should contain 'updated_at'"
    task_id = task["id"]

    # Test 3: GET /tasks/{id} (get specific task)
    print("✓ Testing GET /tasks/{id}...")
    response = requests.get(f"{base_url}/tasks/{task_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    retrieved_task = response.json()
    assert retrieved_task["id"] == task_id, (
        f"Expected {task_id}, got {retrieved_task['id']}"
    )

    # Test 4: PUT /tasks/{id} (update task)
    print("✓ Testing PUT /tasks/{id}...")
    update_data = {"title": "Updated task", "completed": True}
    response = requests.put(f"{base_url}/tasks/{task_id}", json=update_data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    updated_task = response.json()
    assert updated_task["title"] == "Updated task", (
        f"Expected 'Updated task', got {updated_task['title']}"
    )
    assert updated_task["completed"] is True, (
        f"Expected True, got {updated_task['completed']}"
    )

    # Test 5: GET /tasks (should show the updated task)
    print("✓ Testing GET /tasks with data...")
    response = requests.get(f"{base_url}/tasks")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    tasks = response.json()
    assert len(tasks) == 1, f"Expected 1 task, got {len(tasks)}"
    assert tasks[0]["title"] == "Updated task", (
        f"Expected 'Updated task', got {tasks[0]['title']}"
    )

    # Test 6: DELETE /tasks/{id} (delete task)
    print("✓ Testing DELETE /tasks/{id}...")
    response = requests.delete(f"{base_url}/tasks/{task_id}")
    assert response.status_code == 204, f"Expected 204, got {response.status_code}"

    # Test 7: GET /tasks/{id} after deletion (should return 404)
    print("✓ Testing GET /tasks/{id} after deletion...")
    response = requests.get(f"{base_url}/tasks/{task_id}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    error_response = response.json()
    assert "message" in error_response, "Error response should contain 'message'"

    # Test 8: Error cases
    print("✓ Testing error cases...")

    # Invalid POST request
    response = requests.post(f"{base_url}/tasks", json={})
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    # Non-existent task
    response = requests.get(f"{base_url}/tasks/999")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    # Update non-existent task
    response = requests.put(f"{base_url}/tasks/999", json={"title": "Updated"})
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    # Delete non-existent task
    response = requests.delete(f"{base_url}/tasks/999")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    print("✅ All contract tests passed!")


def main():
    """Main function to run contract tests."""
    print("🚀 Starting API contract tests...")

    # Start server
    print("📡 Starting server...")
    server = start_server()

    try:
        # Wait for server to be ready
        if not wait_for_server():
            print("❌ Server failed to start within timeout")
            return 1

        print("✅ Server is ready")

        # Run contract tests
        test_contract()

        return 0

    except AssertionError as e:
        print(f"❌ Contract test failed: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

    finally:
        # Stop server
        print("🛑 Stopping server...")
        server.terminate()
        server.wait()


if __name__ == "__main__":
    sys.exit(main())
