"""
Archetype definitions and bucket templates per element.

Each archetype defines:
  - name
  - descriptor
  - tone (voice/style for the OS)
  - bucket descriptions specific to that archetype's strengths
"""

from typing import TypedDict


class BucketTemplate(TypedDict):
    id: str
    label: str
    description: str
    archetype_focus: str
    initial_projects: list[str]


class EnergyHoursTemplate(TypedDict):
    peak_windows: list[str]
    flexibility: str


class Archetype(TypedDict):
    name: str
    descriptor: str
    tone: str
    buckets: list[BucketTemplate]
    workflow_description: list[str]
    energy_hours: EnergyHoursTemplate


ARCHETYPES: dict[str, Archetype] = {
    "Metal": {
        "name": "Strategic Commander",
        "descriptor": "Precision-driven leader who cuts through ambiguity and executes with discipline",
        "tone": "battlefield intelligence officer",
        "workflow_description": [
            "Mission banners surface priority across all 6 buckets",
            "Pressure calibration tracks intensity and urgency per bucket",
            "Weekly command reviews align all work to strategic objectives",
            "Decisive action orientation with clear success metrics",
        ],
        "buckets": [
            {
                "id": "BUILD",
                "label": "Build",
                "description": "Construct the systems that give you strategic advantage — no wasted effort",
                "archetype_focus": "High-leverage creation with measurable outcomes",
                "initial_projects": ["Core infrastructure", "Flagship product features"],
            },
            {
                "id": "FIX",
                "label": "Fix",
                "description": "Eliminate friction and failure points before they become liabilities",
                "archetype_focus": "Root-cause elimination, not symptom suppression",
                "initial_projects": ["Critical bug triage", "System reliability"],
            },
            {
                "id": "IMPROVE",
                "label": "Improve",
                "description": "Sharpen what works — marginal gains compound into decisive advantage",
                "archetype_focus": "Performance, efficiency, and edge-case hardening",
                "initial_projects": ["Optimization sprints", "Process refinement"],
            },
            {
                "id": "OPERATE",
                "label": "Operate",
                "description": "Run the machine: recurring ops that keep the mission on track",
                "archetype_focus": "Cadence, discipline, and operational integrity",
                "initial_projects": ["Weekly reviews", "Stakeholder comms"],
            },
            {
                "id": "THINK",
                "label": "Think",
                "description": "Strategic analysis, research, and decision-making inputs",
                "archetype_focus": "Intel gathering and high-signal synthesis",
                "initial_projects": ["Competitive landscape", "Architecture decisions"],
            },
            {
                "id": "PERSONAL",
                "label": "Personal",
                "description": "Maintain peak readiness — the commander must be fit to command",
                "archetype_focus": "Physical discipline, mental clarity, recovery",
                "initial_projects": ["Health protocols", "Skill sharpening"],
            },
        ],
        "energy_hours": {
            "peak_windows": ["06:00-09:00", "15:00-18:00"],
            "flexibility": "structured",
        },
    },
    "Wood": {
        "name": "Visionary Builder",
        "descriptor": "Growth-oriented creator who plants seeds today for tomorrow's forest",
        "tone": "optimistic architect of futures",
        "workflow_description": [
            "Seasonal windows mark growth cycles and creative sprints",
            "Rituals align daily work with long-term vision",
            "Growth metrics track momentum and expansion",
            "Greenfield projects bloom from strategic planting",
        ],
        "buckets": [
            {
                "id": "BUILD",
                "label": "Build",
                "description": "Bring new ideas to life — growth requires constant creation",
                "archetype_focus": "Innovative features and greenfield initiatives",
                "initial_projects": ["New product concepts", "Community-building"],
            },
            {
                "id": "FIX",
                "label": "Fix",
                "description": "Prune what inhibits growth — remove blockers to let things flourish",
                "archetype_focus": "Bottleneck removal and debt paydown",
                "initial_projects": ["Tech debt", "UX friction points"],
            },
            {
                "id": "IMPROVE",
                "label": "Improve",
                "description": "Nurture and iterate — small improvements sustain long-term growth",
                "archetype_focus": "Continuous improvement and experimentation",
                "initial_projects": ["A/B tests", "Feature iteration"],
            },
            {
                "id": "OPERATE",
                "label": "Operate",
                "description": "Tend the garden: recurring work that keeps everything alive",
                "archetype_focus": "Consistent rituals and team health",
                "initial_projects": ["Team syncs", "Content publishing"],
            },
            {
                "id": "THINK",
                "label": "Think",
                "description": "Envision what's possible — the future needs to be imagined before it's built",
                "archetype_focus": "Long-horizon planning and creative ideation",
                "initial_projects": ["Vision documents", "Market opportunities"],
            },
            {
                "id": "PERSONAL",
                "label": "Personal",
                "description": "Root deeply — personal growth sustains the visionary's energy",
                "archetype_focus": "Learning, creativity, and relationships",
                "initial_projects": ["Reading list", "Side projects"],
            },
        ],
        "energy_hours": {
            "peak_windows": ["09:00-12:00", "18:00-21:00"],
            "flexibility": "moderate",
        },
    },
    "Water": {
        "name": "Adaptive Navigator",
        "descriptor": "Fluid problem-solver who finds the path of least resistance through any obstacle",
        "tone": "calm deep-sea navigator",
        "workflow_description": [
            "Relationship tags connect context across buckets",
            "Shared rituals sync with team and environment",
            "Group goals flow through adaptive collaboration",
            "Deep-sea navigation reads currents before moving",
        ],
        "buckets": [
            {
                "id": "BUILD",
                "label": "Build",
                "description": "Create adaptable systems that flow with change rather than against it",
                "archetype_focus": "Flexible architectures and modular design",
                "initial_projects": ["API integrations", "Composable components"],
            },
            {
                "id": "FIX",
                "label": "Fix",
                "description": "Navigate around obstacles — find the path that restores flow",
                "archetype_focus": "Creative problem-solving and workarounds",
                "initial_projects": ["Incident response", "Integration issues"],
            },
            {
                "id": "IMPROVE",
                "label": "Improve",
                "description": "Refine your navigation — each iteration reveals a better route",
                "archetype_focus": "Adaptive refinement and feedback loops",
                "initial_projects": ["User feedback integration", "Workflow optimization"],
            },
            {
                "id": "OPERATE",
                "label": "Operate",
                "description": "Keep currents flowing — steady operations through changing conditions",
                "archetype_focus": "Resilient processes and responsive ops",
                "initial_projects": ["Monitoring", "Customer support"],
            },
            {
                "id": "THINK",
                "label": "Think",
                "description": "Read the currents — deep observation before decisive movement",
                "archetype_focus": "Pattern recognition and scenario planning",
                "initial_projects": ["Data analysis", "Risk assessment"],
            },
            {
                "id": "PERSONAL",
                "label": "Personal",
                "description": "Stay fluid — personal resilience and adaptability as a practice",
                "archetype_focus": "Mindfulness, flexibility, and recovery",
                "initial_projects": ["Meditation practice", "Social connections"],
            },
        ],
        "energy_hours": {
            "peak_windows": [],
            "flexibility": "flexible",
        },
    },
    "Fire": {
        "name": "Energetic Catalyst",
        "descriptor": "High-energy igniter who sparks transformation and rallies others to action",
        "tone": "passionate rallying coach",
        "workflow_description": [
            "Streaks track momentum and daily ignition",
            "Checklists channel high energy into focused action",
            "Celebrations amplify wins and rally the team",
            "Rapid sprints turn momentum into measurable results",
        ],
        "buckets": [
            {
                "id": "BUILD",
                "label": "Build",
                "description": "Ignite new things — your energy turns sparks into blazes",
                "archetype_focus": "Rapid prototyping and energetic launches",
                "initial_projects": ["MVP launches", "Campaign creation"],
            },
            {
                "id": "FIX",
                "label": "Fix",
                "description": "Burn away the old — clear what's blocking the heat of progress",
                "archetype_focus": "Bold decisions and swift removal of blockers",
                "initial_projects": ["Legacy removal", "Blocker sprint"],
            },
            {
                "id": "IMPROVE",
                "label": "Improve",
                "description": "Fan the flames — amplify what's already working with new energy",
                "archetype_focus": "Amplification and momentum-building",
                "initial_projects": ["Growth hacking", "Engagement improvements"],
            },
            {
                "id": "OPERATE",
                "label": "Operate",
                "description": "Keep the fire burning — consistent energy sustains the mission",
                "archetype_focus": "High-energy rituals and team motivation",
                "initial_projects": ["Team energizers", "Daily standups"],
            },
            {
                "id": "THINK",
                "label": "Think",
                "description": "Illuminate possibilities — bright ideas need space to catch fire",
                "archetype_focus": "Brainstorming and inspiration-seeking",
                "initial_projects": ["Ideation sessions", "Inspiration research"],
            },
            {
                "id": "PERSONAL",
                "label": "Personal",
                "description": "Tend your inner flame — a catalyst must not burn out",
                "archetype_focus": "Energy management and passion renewal",
                "initial_projects": ["Passion projects", "Exercise and vitality"],
            },
        ],
        "energy_hours": {
            "peak_windows": ["06:00-09:00"],
            "flexibility": "structured",
        },
    },
    "Earth": {
        "name": "Steady Architect",
        "descriptor": "Grounded systems-thinker who builds enduring structures on solid foundations",
        "tone": "grounded master builder",
        "workflow_description": [
            "Solid foundations mark milestone achievements",
            "Structural integrity checks ensure lasting quality",
            "Methodical refinement over rapid change",
            "Steady rhythms build enduring momentum",
        ],
        "buckets": [
            {
                "id": "BUILD",
                "label": "Build",
                "description": "Lay foundations that last — every structure starts with solid ground",
                "archetype_focus": "Durable systems and stable infrastructure",
                "initial_projects": ["Platform foundations", "Data architecture"],
            },
            {
                "id": "FIX",
                "label": "Fix",
                "description": "Stabilize and reinforce — shore up what's cracked before building higher",
                "archetype_focus": "Structural integrity and reliability",
                "initial_projects": ["Stability improvements", "Error reduction"],
            },
            {
                "id": "IMPROVE",
                "label": "Improve",
                "description": "Refine methodically — steady, consistent improvement over time",
                "archetype_focus": "Systematic quality improvements",
                "initial_projects": ["Process documentation", "Quality metrics"],
            },
            {
                "id": "OPERATE",
                "label": "Operate",
                "description": "Maintain the ground — stable operations are the bedrock of everything",
                "archetype_focus": "Reliable, repeatable operational discipline",
                "initial_projects": ["SLA management", "Runbook maintenance"],
            },
            {
                "id": "THINK",
                "label": "Think",
                "description": "Survey the terrain — thorough analysis before any move",
                "archetype_focus": "Comprehensive planning and risk analysis",
                "initial_projects": ["Capacity planning", "Strategic roadmap"],
            },
            {
                "id": "PERSONAL",
                "label": "Personal",
                "description": "Stay grounded — stability in self sustains stability in all you build",
                "archetype_focus": "Routine, health, and steady relationships",
                "initial_projects": ["Daily routines", "Long-term learning"],
            },
        ],
        "energy_hours": {
            "peak_windows": ["09:00-12:00", "14:00-17:00"],
            "flexibility": "structured",
        },
    },
}


def get_archetype(element: str) -> Archetype:
    if element not in ARCHETYPES:
        raise ValueError(f"Unknown element: {element}. Must be one of {list(ARCHETYPES)}")
    return ARCHETYPES[element]


def list_archetypes() -> list[dict]:
    return [
        {
            "element": element,
            "name": arch["name"],
            "descriptor": arch["descriptor"],
            "tone": arch["tone"],
        }
        for element, arch in ARCHETYPES.items()
    ]
