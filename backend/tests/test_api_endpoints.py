import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "ai_engines" in data

def test_load_demo_project():
    response = client.post("/api/projects/demo/load")
    assert response.status_code == 200
    project = response.json()
    assert project["name"] == "Project Aurora"
    assert project["scene_count"] >= 8
    project_id = project["id"]

    # Verify scenes
    res_scenes = client.get(f"/api/projects/{project_id}/scenes")
    assert res_scenes.status_code == 200
    scenes = res_scenes.json()
    assert len(scenes) >= 8

    # Verify characters
    res_chars = client.get(f"/api/projects/{project_id}/characters")
    assert res_chars.status_code == 200
    assert len(res_chars.json()) > 0

    # Verify schedule
    res_sched = client.get(f"/api/projects/{project_id}/schedule")
    assert res_sched.status_code == 200
    sched = res_sched.json()
    assert sched["total_days"] > 0

    # Verify stripboard
    res_strip = client.get(f"/api/projects/{project_id}/stripboard")
    assert res_strip.status_code == 200
    assert "strips" in res_strip.json()

    # Verify budget
    res_budget = client.get(f"/api/projects/{project_id}/budget")
    assert res_budget.status_code == 200
    assert res_budget.json()["grand_total"] > 0

    # Verify call sheets
    res_calls = client.get(f"/api/projects/{project_id}/call-sheets")
    assert res_calls.status_code == 200
    assert len(res_calls.json()) > 0

    # Verify callback letters
    res_cb = client.get(f"/api/projects/{project_id}/callbacks")
    assert res_cb.status_code == 200
    assert len(res_cb.json()) > 0

    # Verify complete pre-production package ZIP export
    res_zip = client.get(f"/api/projects/{project_id}/export/package")
    assert res_zip.status_code == 200
    assert res_zip.headers["content-type"] == "application/zip"
    assert len(res_zip.content) > 1000
