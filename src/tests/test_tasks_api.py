from playwright.sync_api import APIRequestContext
import pytest


@pytest.fixture
def task(api: APIRequestContext):
    response = api.post("tasks", data={"title": "API test task"})
    assert response.ok, response.text()
    task = response.json()
    yield task
    api.delete(f"tasks/{task['id']}")


def test_create_task_returns_id(api: APIRequestContext) -> None:
    response = api.post("tasks", data={"title": "POST test task"})
    assert response.ok, response.text()
    task_id = response.json()["id"]
    assert task_id

    api.delete(f"tasks/{task_id}")


def test_get_task_by_id(api: APIRequestContext, task: dict) -> None:
    response = api.get(f"tasks/{task['id']}")
    assert response.ok
    assert response.json()["id"] == task["id"]


def test_delete_task_by_id(api: APIRequestContext) -> None:
    task_id = api.post("tasks", data={"title": "DELETE test task"}).json()["id"]

    response = api.delete(f"tasks/{task_id}")
    assert response.ok
    assert "message" in response.json()