"""Integration tests for the OS Generator FastAPI endpoints."""

import json
from pathlib import Path

import jsonschema
import pytest
from fastapi.testclient import TestClient

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)

SCHEMA_PATH = Path(__file__).parent.parent / "schema" / "os_config_v0.1.json"


def load_json_schema():
    return json.loads(SCHEMA_PATH.read_text())


# ── Health ─────────────────────────────────────────────────────────────────

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ── Archetypes list ────────────────────────────────────────────────────────

def test_archetypes_returns_five():
    resp = client.get("/archetypes")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["archetypes"]) == 5
    names = {a["name"] for a in data["archetypes"]}
    assert names == {
        "Strategic Commander",
        "Visionary Builder",
        "Adaptive Navigator",
        "Energetic Catalyst",
        "Steady Architect",
    }


# ── Generate ───────────────────────────────────────────────────────────────

def test_generate_basic():
    resp = client.post("/generate", json={
        "name": "Test User",
        "birth_date": "1984-06-15",
        "goals": ["Build great products"],
        "domains": ["Work", "Health"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["schema_version"] == "0.1"
    assert data["user"]["name"] == "Test User"
    assert data["user"]["bazi_element"] in ["Metal", "Wood", "Water", "Fire", "Earth"]
    assert len(data["buckets"]) == 6


def test_generate_all_six_bucket_ids_present():
    resp = client.post("/generate", json={
        "name": "Alice",
        "birth_date": "1990-05-15",
    })
    assert resp.status_code == 200
    bucket_ids = {b["id"] for b in resp.json()["buckets"]}
    assert bucket_ids == {"BUILD", "FIX", "IMPROVE", "OPERATE", "THINK", "PERSONAL"}


def test_generate_passes_json_schema_validation():
    resp = client.post("/generate", json={
        "name": "Schema Validator",
        "birth_date": "1988-03-21",
        "goals": ["Validate everything"],
        "domains": ["Engineering"],
    })
    assert resp.status_code == 200
    schema = load_json_schema()
    # Should not raise
    jsonschema.validate(instance=resp.json(), schema=schema)


def test_heidi_maps_to_strategic_commander():
    """
    Critical acceptance test: Heidi (CEO, born 1990) must map to Strategic Commander.
    Strong Metal year → Strategic Commander archetype.
    """
    resp = client.post("/generate", json={
        "name": "Heidi",
        "birth_date": "1990-01-01",  # Geng year = Metal
        "goals": ["Build the world's first personalized OS"],
        "domains": ["Strategy", "Product", "Leadership"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["bazi_element"] == "Metal"
    assert data["user"]["archetype"] == "Strategic Commander"
    assert data["tone"] == "battlefield intelligence officer"


def test_generate_without_optional_fields():
    resp = client.post("/generate", json={
        "name": "Minimal User",
        "birth_date": "1992-07-04",
    })
    assert resp.status_code == 200
    assert resp.json()["user"]["name"] == "Minimal User"


def test_generate_invalid_date_format():
    resp = client.post("/generate", json={
        "name": "Bad Date",
        "birth_date": "not-a-date",
    })
    assert resp.status_code == 422


def test_generate_missing_name():
    resp = client.post("/generate", json={
        "birth_date": "1990-01-01",
    })
    assert resp.status_code == 422


# ── Generate Tasks ──────────────────────────────────────────────────────────

def test_generate_tasks_basic():
    resp = client.post("/generate-tasks", json={
        "project_name": "Launch my startup",
        "goals": ["Build great products"],
        "domains": ["Work", "Health"],
        "birth_date": "1990-03-15",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "tasks" in data
    assert len(data["tasks"]) > 0
    assert data["archetype"] == "Strategic Commander"
    assert data["tasks"][0]["name"]
    assert data["tasks"][0]["duration_minutes"] > 0
    assert data["tasks"][0]["priority"] in ["high", "medium", "low"]
    assert data["tasks"][0]["schedule"]["bucket"] in ["BUILD", "FIX", "IMPROVE", "OPERATE", "THINK", "PERSONAL"]


def test_generate_tasks_returns_max_12_tasks():
    resp = client.post("/generate-tasks", json={
        "project_name": "Test Project",
        "goals": ["Goal 1", "Goal 2", "Goal 3"],
        "domains": ["Domain 1", "Domain 2", "Domain 3"],
        "birth_date": "1985-07-22",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["tasks"]) <= 12


def test_generate_tasks_validates_birth_date():
    resp = client.post("/generate-tasks", json={
        "project_name": "Test Project",
        "birth_date": "not-a-date",
    })
    assert resp.status_code == 422


def test_generate_tasks_for_heidi_metal_archetype():
    resp = client.post("/generate-tasks", json={
        "project_name": "Heidi's Project",
        "goals": ["Build the world's first personalized OS"],
        "domains": ["Strategy", "Product"],
        "birth_date": "1990-01-01",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["archetype"] == "Strategic Commander"
    assert data["tasks"][0]["schedule"]["bucket"] == "BUILD"


def test_generate_date_too_old():
    resp = client.post("/generate", json={
        "name": "Ancient",
        "birth_date": "1800-01-01",
    })
    assert resp.status_code == 422
    assert "Birth year must be between 1900 and 2100" in resp.json()["detail"]


def test_generate_future_date():
    resp = client.post("/generate", json={
        "name": "Time Traveler",
        "birth_date": "2099-01-01",
    })
    assert resp.status_code == 422
    assert "cannot be in the future" in resp.json()["detail"]


def test_generate_intelligent_projects_with_goals_and_domains():
    """Projects should be generated based on user's goals and domains."""
    resp = client.post("/generate", json={
        "name": "Startup Founder",
        "birth_date": "1990-03-15",
        "goals": ["Launch my startup", "Get promoted"],
        "domains": ["Career", "Health"],
    })
    assert resp.status_code == 200
    data = resp.json()
    buckets = {b["id"]: b for b in data["buckets"]}

    assert "Goal: Launch my startup" in buckets["BUILD"]["initial_projects"]
    assert "Career initiative" in buckets["BUILD"]["initial_projects"]
    assert "Resolve Career gaps" in buckets["FIX"]["initial_projects"]
    assert "Health protocols" in buckets["PERSONAL"]["initial_projects"]


def test_generate_default_projects_without_goals_domains():
    """When no goals/domains provided, default projects should be used."""
    resp = client.post("/generate", json={
        "name": "Minimal User",
        "birth_date": "1990-05-15",
    })
    assert resp.status_code == 200
    data = resp.json()
    buckets = {b["id"]: b for b in data["buckets"]}

    assert "Core infrastructure" in buckets["BUILD"]["initial_projects"]
    assert "Flagship product features" in buckets["BUILD"]["initial_projects"]
    assert buckets["BUILD"]["initial_projects"] == ["Core infrastructure", "Flagship product features"]


def test_generate_workflow_description_present():
    """Workflow description should be present and have 3-4 items."""
    resp = client.post("/generate", json={
        "name": "Test User",
        "birth_date": "1990-03-15",
        "goals": ["Test goal"],
        "domains": ["Test domain"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "workflow_description" in data
    assert 3 <= len(data["workflow_description"]) <= 4
