"""OS Generator — FastAPI service.

Endpoints:
  POST /generate      Transform quiz answers → OS config JSON
  GET  /health        Liveness probe
  GET  /archetypes    List all archetypes and metadata
"""

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from archetypes import get_archetype, list_archetypes
from bazi import dominant_element
from models import (
    ArchetypeInfo,
    ArchetypeListResponse,
    Bucket,
    EnergyHours,
    GenerateRequest,
    GenerateTasksRequest,
    GenerateTasksResponse,
    OSConfig,
    Task,
    TaskSchedule,
    UserProfile,
)
from scoring import QuizAnswers, calculate_archetype

app = FastAPI(
    title="OS Generator",
    description="Transforms quiz answers into a personalized OS config JSON using BaZi + Archetype mapping.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/archetypes", response_model=ArchetypeListResponse)
def archetypes() -> ArchetypeListResponse:
    return ArchetypeListResponse(
        archetypes=[ArchetypeInfo(**a) for a in list_archetypes()]
    )


_WORKFLOW_TEMPLATES = {
    "Metal": [
        "Execute with precision — cut through ambiguity and drive measurable outcomes",
        "Establish strategic cadence — weekly reviews with clear KPI tracking",
        "Build high-leverage systems — automate repetition, delegate variation",
    ],
    "Wood": [
        "Plant seeds daily — commit to consistent creation and growth rituals",
        "Nurture expansion — experiment with new approaches, measure what scales",
        "Build in public — let community growth validate direction",
    ],
    "Water": [
        "Flow with change — maintain adaptive systems that respond, not resist",
        "Deep observation first — gather signals before committing to a path",
        "Compose and connect — build flexible integrations over rigid monoliths",
    ],
    "Fire": [
        "Ignite momentum — rapid prototypes that spark engagement and energy",
        "Rally the team — high-energy ceremonies that sustain collective heat",
        "Burn through blockers — decisive action on obstacles before they calcify",
    ],
    "Earth": [
        "Lay stable foundations — prioritize durability over quick wins",
        "Maintain structural integrity — systematic reviews prevent accumulation of debt",
        "Build enduring systems — quality and reliability as core operating principles",
    ],
}

_ARCHETYPE_ID_TO_ELEMENT = {
    "strategic_commander": "Metal",
    "visionary_builder": "Wood",
    "adaptive_navigator": "Water",
    "energetic_catalyst": "Fire",
    "steady_architect": "Earth",
}


@app.post("/generate", response_model=OSConfig)
def generate(req: GenerateRequest) -> OSConfig:
    try:
        element = dominant_element(req.birth_date)
        archetype_result = None
        calculation_log: dict = {}

        if req.quiz is not None:
            quiz_answers = QuizAnswers(
                q01=req.quiz.q01,
                q02=req.quiz.q02,
                q03=req.quiz.q03,
                q04=req.quiz.q04,
                q05=req.quiz.q05,
                q06=req.quiz.q06,
                q07=req.quiz.q07,
                q08=req.quiz.q08,
                q09=req.quiz.q09,
                q10=req.quiz.q10,
                q11=req.quiz.q11,
                q12=req.quiz.q12,
                q13=req.quiz.q13,
                q14=req.quiz.q14,
                q15=req.quiz.q15,
            )
            archetype_result = calculate_archetype(req.birth_date, None, quiz_answers)

            archetype_id = archetype_result.archetype_id
            calculation_log = {
                "archetype_id": archetype_id,
                "confidence": archetype_result.confidence,
                "dominant_elements": archetype_result.dominant_elements,
                "personality_vector": {
                    "cognitive_style": archetype_result.personality_vector.cognitive_style,
                    "orientation": archetype_result.personality_vector.orientation,
                    "energy_source": archetype_result.personality_vector.energy_source,
                },
                "bazi_element_from_year": element,
                "edge_cases": [],
            }

            if len(archetype_result.dominant_elements) > 1:
                calculation_log["edge_cases"].append("balanced_bazi")
                calculation_log["edge_case_detail"] = f"Tied elements: {archetype_result.dominant_elements}"

            element = _ARCHETYPE_ID_TO_ELEMENT.get(archetype_id, element)

        archetype = get_archetype(element)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    user = UserProfile(
        name=req.name,
        bazi_element=element,  # type: ignore[arg-type]
        archetype=archetype["name"],
        archetype_descriptor=archetype["descriptor"],
    )

    buckets = _build_buckets(archetype, req.goals, req.domains)

    energy_hours_data = archetype.get("energy_hours")
    energy_hours = None
    if energy_hours_data:
        energy_hours = EnergyHours(
            peak_windows=energy_hours_data["peak_windows"],
            flexibility=energy_hours_data["flexibility"],
            user_adjustable=True,
        )

    config = OSConfig(
        schema_version="0.1",
        user=user,
        buckets=buckets,
        tone=archetype["tone"],
        workflow_description=archetype["workflow_description"],
        energy_hours=energy_hours,
        generated_at=datetime.now(tz=timezone.utc),
    )

    return config


def _build_buckets(archetype: dict, goals: list[str], domains: list[str]) -> list[Bucket]:
    buckets = []
    for bucket_template in archetype["buckets"]:
        initial_projects = _generate_projects(
            bucket_template["id"],
            bucket_template["archetype_focus"],
            goals,
            domains,
        )
        bucket = Bucket(
            id=bucket_template["id"],
            label=bucket_template["label"],
            description=bucket_template["description"],
            archetype_focus=bucket_template["archetype_focus"],
            initial_projects=initial_projects,
        )
        buckets.append(bucket)
    return buckets


def _generate_projects(
    bucket_id: str,
    archetype_focus: str,
    goals: list[str],
    domains: list[str],
) -> list[str]:
    if not goals and not domains:
        return _DEFAULT_PROJECTS.get(bucket_id, [])

    projects = []
    goals_lower = [g.lower() for g in goals]
    domains_lower = [d.lower() for d in domains]

    if bucket_id == "BUILD":
        if goals:
            projects.append(f"Goal: {goals[0]}")
        if domains:
            projects.append(f"{domains[0]} initiative")
        if len(projects) < 2:
            projects.append("Core infrastructure" if "Metal" in archetype_focus or "infrastructure" in archetype_focus.lower() else "New product development")
    elif bucket_id == "FIX":
        if domains:
            projects.append(f"Resolve {domains[0]} gaps")
        projects.append("Critical bug triage")
    elif bucket_id == "IMPROVE":
        if goals:
            projects.append(f"Optimize for: {goals[0]}")
        projects.append("Process refinement")
    elif bucket_id == "OPERATE":
        if domains:
            projects.append(f"{domains[0]} cadence")
        projects.append("Weekly reviews")
    elif bucket_id == "THINK":
        if goals:
            projects.append(f"Research: {goals[0]}")
        projects.append("Competitive landscape")
    elif bucket_id == "PERSONAL":
        if domains and "health" in domains_lower:
            projects.append("Health protocols")
        projects.append("Skill sharpening")

    return projects[:3] if len(projects) > 3 else projects


_DEFAULT_PROJECTS = {
    "BUILD": ["Core infrastructure", "Flagship product features"],
    "FIX": ["Critical bug triage", "System reliability"],
    "IMPROVE": ["Optimization sprints", "Process refinement"],
    "OPERATE": ["Weekly reviews", "Stakeholder comms"],
    "THINK": ["Competitive landscape", "Architecture decisions"],
    "PERSONAL": ["Health protocols", "Skill sharpening"],
}


_TASK_TEMPLATES: dict[str, dict[str, list[dict]]] = {
    "Metal": {
        "BUILD": [
            {"name": "Define strategic milestones", "duration": 90, "priority": "high", "time": "morning"},
            {"name": "Architect core systems", "duration": 120, "priority": "high", "time": "morning"},
            {"name": "Establish KPI framework", "duration": 60, "priority": "medium", "time": "afternoon"},
        ],
        "FIX": [
            {"name": "Critical path risk assessment", "duration": 45, "priority": "high", "time": "morning"},
            {"name": "Root cause analysis", "duration": 60, "priority": "high", "time": "afternoon"},
            {"name": "System reliability audit", "duration": 90, "priority": "medium", "time": "afternoon"},
        ],
        "IMPROVE": [
            {"name": "Process efficiency review", "duration": 60, "priority": "medium", "time": "morning"},
            {"name": "KPI optimization sprint", "duration": 90, "priority": "medium", "time": "afternoon"},
            {"name": "Performance benchmarking", "duration": 45, "priority": "low", "time": "morning"},
        ],
        "OPERATE": [
            {"name": "Weekly command review", "duration": 60, "priority": "high", "time": "morning"},
            {"name": "Stakeholder sync", "duration": 30, "priority": "medium", "time": "afternoon"},
            {"name": "Operational metrics review", "duration": 45, "priority": "medium", "time": "afternoon"},
        ],
        "THINK": [
            {"name": "Competitive landscape analysis", "duration": 90, "priority": "medium", "time": "morning"},
            {"name": "Strategic planning session", "duration": 120, "priority": "medium", "time": "morning"},
            {"name": "Architecture decision records", "duration": 60, "priority": "low", "time": "afternoon"},
        ],
        "PERSONAL": [
            {"name": "Physical readiness protocol", "duration": 45, "priority": "high", "time": "morning"},
            {"name": "Mental clarity practice", "duration": 30, "priority": "medium", "time": "evening"},
            {"name": "Strategic skill development", "duration": 60, "priority": "medium", "time": "evening"},
        ],
    },
    "Wood": {
        "BUILD": [
            {"name": "Vision and concept exploration", "duration": 90, "priority": "high", "time": "morning"},
            {"name": "Growth strategy mapping", "duration": 120, "priority": "high", "time": "morning"},
            {"name": "Community building plan", "duration": 60, "priority": "medium", "time": "afternoon"},
        ],
        "FIX": [
            {"name": "Growth blocker identification", "duration": 45, "priority": "high", "time": "morning"},
            {"name": "Bottleneck removal sprint", "duration": 90, "priority": "high", "time": "afternoon"},
            {"name": "Debt paydown prioritization", "duration": 60, "priority": "medium", "time": "afternoon"},
        ],
        "IMPROVE": [
            {"name": "Experiment design", "duration": 60, "priority": "medium", "time": "morning"},
            {"name": "A/B test analysis", "duration": 45, "priority": "medium", "time": "afternoon"},
            {"name": "Iteration retrospective", "duration": 30, "priority": "low", "time": "afternoon"},
        ],
        "OPERATE": [
            {"name": "Team sync ritual", "duration": 30, "priority": "medium", "time": "morning"},
            {"name": "Content publishing cadence", "duration": 60, "priority": "medium", "time": "afternoon"},
            {"name": "Growth metrics review", "duration": 45, "priority": "medium", "time": "afternoon"},
        ],
        "THINK": [
            {"name": "Future vision workshop", "duration": 120, "priority": "high", "time": "morning"},
            {"name": "Market opportunity research", "duration": 90, "priority": "medium", "time": "morning"},
            {"name": "Ideation session", "duration": 60, "priority": "medium", "time": "afternoon"},
        ],
        "PERSONAL": [
            {"name": "Learning sprint", "duration": 60, "priority": "medium", "time": "morning"},
            {"name": "Creative exploration", "duration": 45, "priority": "low", "time": "evening"},
            {"name": "Relationship building", "duration": 60, "priority": "medium", "time": "evening"},
        ],
    },
    "Water": {
        "BUILD": [
            {"name": "Flexible architecture design", "duration": 120, "priority": "high", "time": "morning"},
            {"name": "API integration mapping", "duration": 90, "priority": "high", "time": "morning"},
            {"name": "Composable component planning", "duration": 60, "priority": "medium", "time": "afternoon"},
        ],
        "FIX": [
            {"name": "Adaptive problem solving", "duration": 60, "priority": "high", "time": "morning"},
            {"name": "Integration issue resolution", "duration": 90, "priority": "high", "time": "afternoon"},
            {"name": "Flow restoration assessment", "duration": 45, "priority": "medium", "time": "afternoon"},
        ],
        "IMPROVE": [
            {"name": "Feedback loop setup", "duration": 45, "priority": "medium", "time": "morning"},
            {"name": "Workflow optimization", "duration": 60, "priority": "medium", "time": "afternoon"},
            {"name": "Adaptive refinement cycle", "duration": 90, "priority": "medium", "time": "afternoon"},
        ],
        "OPERATE": [
            {"name": "Resilient process check", "duration": 45, "priority": "medium", "time": "morning"},
            {"name": "Responsive ops review", "duration": 60, "priority": "medium", "time": "afternoon"},
            {"name": "Monitoring cadence", "duration": 30, "priority": "medium", "time": "morning"},
        ],
        "THINK": [
            {"name": "Deep pattern observation", "duration": 120, "priority": "high", "time": "morning"},
            {"name": "Scenario planning", "duration": 90, "priority": "medium", "time": "morning"},
            {"name": "Risk assessment", "duration": 60, "priority": "medium", "time": "afternoon"},
        ],
        "PERSONAL": [
            {"name": "Mindfulness practice", "duration": 30, "priority": "high", "time": "morning"},
            {"name": "Flexibility training", "duration": 45, "priority": "medium", "time": "evening"},
            {"name": "Social connections", "duration": 60, "priority": "medium", "time": "evening"},
        ],
    },
    "Fire": {
        "BUILD": [
            {"name": "MVP rapid prototype", "duration": 120, "priority": "high", "time": "morning"},
            {"name": "Launch campaign creation", "duration": 90, "priority": "high", "time": "morning"},
            {"name": "Spark momentum checklist", "duration": 45, "priority": "medium", "time": "afternoon"},
        ],
        "FIX": [
            {"name": "Legacy removal sprint", "duration": 90, "priority": "high", "time": "morning"},
            {"name": "Blocker elimination", "duration": 60, "priority": "high", "time": "afternoon"},
            {"name": "Bold decision session", "duration": 45, "priority": "medium", "time": "morning"},
        ],
        "IMPROVE": [
            {"name": "Growth hacking experiment", "duration": 60, "priority": "high", "time": "morning"},
            {"name": "Engagement amplification", "duration": 90, "priority": "medium", "time": "afternoon"},
            {"name": "Momentum tracking", "duration": 30, "priority": "medium", "time": "morning"},
        ],
        "OPERATE": [
            {"name": "Team energizer", "duration": 30, "priority": "high", "time": "morning"},
            {"name": "Daily standup facilitation", "duration": 15, "priority": "high", "time": "morning"},
            {"name": "High-energy ritual", "duration": 45, "priority": "medium", "time": "afternoon"},
        ],
        "THINK": [
            {"name": "Ideation burst", "duration": 60, "priority": "medium", "time": "morning"},
            {"name": "Inspiration seeking", "duration": 90, "priority": "medium", "time": "morning"},
            {"name": "Brainstorm session", "duration": 60, "priority": "low", "time": "afternoon"},
        ],
        "PERSONAL": [
            {"name": "Energy management", "duration": 45, "priority": "high", "time": "morning"},
            {"name": "Passion project time", "duration": 60, "priority": "medium", "time": "evening"},
            {"name": "Vitality exercise", "duration": 30, "priority": "medium", "time": "evening"},
        ],
    },
    "Earth": {
        "BUILD": [
            {"name": "Foundation architecture", "duration": 120, "priority": "high", "time": "morning"},
            {"name": "Platform stability planning", "duration": 90, "priority": "high", "time": "morning"},
            {"name": "Data architecture design", "duration": 120, "priority": "medium", "time": "afternoon"},
        ],
        "FIX": [
            {"name": "Structural integrity check", "duration": 60, "priority": "high", "time": "morning"},
            {"name": "Stability improvements", "duration": 90, "priority": "high", "time": "afternoon"},
            {"name": "Error reduction audit", "duration": 60, "priority": "medium", "time": "afternoon"},
        ],
        "IMPROVE": [
            {"name": "Process documentation", "duration": 60, "priority": "medium", "time": "morning"},
            {"name": "Quality metrics review", "duration": 45, "priority": "medium", "time": "afternoon"},
            {"name": "Systematic refinement", "duration": 90, "priority": "low", "time": "morning"},
        ],
        "OPERATE": [
            {"name": "SLA management review", "duration": 60, "priority": "high", "time": "morning"},
            {"name": "Runbook maintenance", "duration": 45, "priority": "medium", "time": "afternoon"},
            {"name": "Operational discipline check", "duration": 30, "priority": "medium", "time": "morning"},
        ],
        "THINK": [
            {"name": "Capacity planning", "duration": 90, "priority": "high", "time": "morning"},
            {"name": "Strategic roadmap review", "duration": 120, "priority": "medium", "time": "morning"},
            {"name": "Comprehensive risk analysis", "duration": 90, "priority": "medium", "time": "afternoon"},
        ],
        "PERSONAL": [
            {"name": "Daily routine maintenance", "duration": 45, "priority": "high", "time": "morning"},
            {"name": "Long-term learning", "duration": 60, "priority": "medium", "time": "evening"},
            {"name": "Steady relationship building", "duration": 60, "priority": "medium", "time": "evening"},
        ],
    },
}

_BUCKET_PRIORITY: dict[str, list[str]] = {
    "Metal": ["BUILD", "OPERATE", "FIX", "IMPROVE", "THINK", "PERSONAL"],
    "Wood": ["BUILD", "THINK", "IMPROVE", "OPERATE", "FIX", "PERSONAL"],
    "Water": ["THINK", "OPERATE", "BUILD", "IMPROVE", "FIX", "PERSONAL"],
    "Fire": ["BUILD", "FIX", "IMPROVE", "OPERATE", "THINK", "PERSONAL"],
    "Earth": ["BUILD", "OPERATE", "IMPROVE", "FIX", "THINK", "PERSONAL"],
}

_TIME_RATIONALE: dict[str, str] = {
    "morning": "best for focused, high-priority work",
    "afternoon": "suitable for collaborative and operational tasks",
    "evening": "optimal for reflection and personal activities",
}


@app.post("/generate-tasks", response_model=GenerateTasksResponse)
def generate_tasks(req: GenerateTasksRequest) -> GenerateTasksResponse:
    try:
        element = dominant_element(req.birth_date)
        archetype = get_archetype(element)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    tasks: list[Task] = []
    bucket_order = _BUCKET_PRIORITY.get(element, ["BUILD", "FIX", "IMPROVE", "OPERATE", "THINK", "PERSONAL"])
    templates = _TASK_TEMPLATES.get(element, _TASK_TEMPLATES["Metal"])

    goals_lower = [g.lower() for g in req.goals]
    domains_lower = [d.lower() for d in req.domains]

    for bucket_id in bucket_order:
        bucket_templates = templates.get(bucket_id, [])
        for i, tpl in enumerate(bucket_templates[:2]):
            if len(tasks) >= 12:
                break

            task_name = tpl["name"]
            if req.project_name and i == 0:
                task_name = f"{task_name} — {req.project_name}"

            time_rationale = _TIME_RATIONALE.get(tpl["time"], "balanced scheduling")

            task = Task(
                name=task_name,
                duration_minutes=tpl["duration"],
                priority=tpl["priority"],
                schedule=TaskSchedule(
                    bucket=bucket_id,
                    suggested_time=tpl["time"],
                    suggested_day=None,
                ),
                rationale=f"Prioritized for {archetype['name']} ({element}) — {time_rationale}",
            )
            tasks.append(task)

        if len(tasks) >= 12:
            break

    if req.goals and len(tasks) < 12:
        tasks.append(Task(
            name=f"Align with goal: {req.goals[0]}",
            duration_minutes=60,
            priority="high",
            schedule=TaskSchedule(bucket="THINK", suggested_time="morning"),
            rationale=f"Directly aligned with stated goal for {archetype['name']} archetype",
        ))

    if req.domains and len(tasks) < 12:
        tasks.append(Task(
            name=f"Focus area: {req.domains[0]}",
            duration_minutes=45,
            priority="medium",
            schedule=TaskSchedule(bucket="OPERATE", suggested_time="afternoon"),
            rationale=f"Dedicated time for {req.domains[0]} domain management",
        ))

    return GenerateTasksResponse(
        tasks=tasks,
        archetype=archetype["name"],
        generated_at=datetime.now(tz=timezone.utc),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
