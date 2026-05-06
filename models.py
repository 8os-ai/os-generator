"""Pydantic v2 models for request/response validation."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


# ── Request ────────────────────────────────────────────────────────────────

class QuizInput(BaseModel):
    q01: int = Field(default=5, ge=1, le=10, description="Systematic (1-5) vs Intuitive (6-10)")
    q02: int = Field(default=5, ge=1, le=10, description="Systematic (1-5) vs Intuitive (6-10)")
    q03: int = Field(default=5, ge=1, le=10, description="Systematic (1-5) vs Intuitive (6-10)")
    q04: int = Field(default=5, ge=1, le=10, description="Systematic (1-5) vs Intuitive (6-10)")
    q05: int = Field(default=5, ge=1, le=10, description="Systematic (1-5) vs Intuitive (6-10)")
    q06: int = Field(default=5, ge=1, le=10, description="Goal (1-5) vs Process (6-10)")
    q07: int = Field(default=5, ge=1, le=10, description="Goal (1-5) vs Process (6-10)")
    q08: int = Field(default=5, ge=1, le=10, description="Goal (1-5) vs Process (6-10)")
    q09: int = Field(default=5, ge=1, le=10, description="Goal (1-5) vs Process (6-10)")
    q10: int = Field(default=5, ge=1, le=10, description="Goal (1-5) vs Process (6-10)")
    q11: int = Field(default=5, ge=1, le=10, description="Internal (1-5) vs External (6-10)")
    q12: int = Field(default=5, ge=1, le=10, description="Internal (1-5) vs External (6-10)")
    q13: int = Field(default=5, ge=1, le=10, description="Internal (1-5) vs External (6-10)")
    q14: int = Field(default=5, ge=1, le=10, description="Internal (1-5) vs External (6-10)")
    q15: int = Field(default=5, ge=1, le=10, description="Internal (1-5) vs External (6-10)")


class GenerateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="User's full name")
    birth_date: date = Field(..., description="Date of birth (YYYY-MM-DD)")
    goals: list[str] = Field(default_factory=list, description="High-level personal/professional goals")
    domains: list[str] = Field(default_factory=list, description="Life/work domains the user wants to manage")
    quiz: QuizInput | None = Field(default=None, description="Optional quiz answers for weighted archetype calculation")


# ── Response ───────────────────────────────────────────────────────────────

BaZiElement = Literal["Metal", "Wood", "Water", "Fire", "Earth"]

BucketId = Literal["BUILD", "FIX", "IMPROVE", "OPERATE", "THINK", "PERSONAL"]


class UserProfile(BaseModel):
    name: str
    bazi_element: BaZiElement
    archetype: str
    archetype_descriptor: str


class Bucket(BaseModel):
    id: BucketId
    label: str
    description: str
    archetype_focus: str
    initial_projects: list[str]


class EnergyHours(BaseModel):
    peak_windows: list[str] = Field(
        ..., description="List of peak energy time windows, e.g. ['06:00-09:00', '15:00-18:00']"
    )
    flexibility: str = Field(
        ..., description="Energy schedule flexibility: 'flexible', 'moderate', or 'structured'"
    )
    user_adjustable: bool = Field(
        default=True, description="Whether the user can manually adjust energy hours"
    )


class OSConfig(BaseModel):
    schema_version: str = "0.1"
    user: UserProfile
    buckets: list[Bucket] = Field(..., min_length=6, max_length=6)
    workflow_description: list[str] = Field(..., min_length=3, max_length=4)
    tone: str
    energy_hours: EnergyHours | None = Field(default=None, description="Peak energy hours based on archetype")
    generated_at: datetime


# ── Archetype list response ────────────────────────────────────────────────

class ArchetypeInfo(BaseModel):
    element: BaZiElement
    name: str
    descriptor: str
    tone: str


class TaskSchedule(BaseModel):
    bucket: BucketId
    suggested_time: str | None = Field(default=None, description="Suggested time of day: morning, afternoon, evening")
    suggested_day: str | None = Field(default=None, description="Suggested day of week: Monday-Sunday")


class Task(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    duration_minutes: int = Field(..., ge=15, le=480, description="Estimated duration in minutes (15min-8hr)")
    priority: Literal["high", "medium", "low"]
    schedule: TaskSchedule
    rationale: str = Field(..., description="Why this task was generated for this archetype")


class GenerateTasksRequest(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=200, description="Name of the project")
    project_description: str | None = Field(default=None, max_length=1000, description="Optional project description")
    goals: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    birth_date: date = Field(..., description="User's birth date for BaZi calculation")


class GenerateTasksResponse(BaseModel):
    tasks: list[Task]
    archetype: str
    generated_at: datetime


class ArchetypeListResponse(BaseModel):
    archetypes: list[ArchetypeInfo]
