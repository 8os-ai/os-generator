"""
Archetype Scoring Engine — combines BaZi Day Master calculation
with personality quiz responses to produce archetype, confidence,
dominant_elements, and personality_vector.

Quiz structure (15 questions, 3 dimensions):
  - cognitive_style: systematic (1-5) vs intuitive (6-10)
  - orientation: goal (1-5) vs process (6-10)
  - energy_source: internal (1-5) vs external (6-10)
"""

from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, Field

ELEMENTS = Literal["Metal", "Wood", "Water", "Fire", "Earth"]
DAYS_CYCLE = 10
STEM_ELEMENTS = [
    "Wood", "Wood", "Fire", "Fire", "Earth",
    "Earth", "Metal", "Metal", "Water", "Water",
]
MONTH_BRANCH_ELEMENTS = {
    1: "Earth", 2: "Wood", 3: "Wood", 4: "Earth", 5: "Fire", 6: "Fire",
    7: "Earth", 8: "Metal", 9: "Metal", 10: "Earth", 11: "Water", 12: "Water",
}
_REF_DATE = date(2000, 1, 1)


def _jd_from_date(d: date) -> int:
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3
    return d.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _jd_to_date(jd: int) -> date:
    a = jd + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    return date(year, month, day)


def _ref_jd() -> int:
    return _jd_from_date(_REF_DATE)


def day_stem_index(d: date) -> int:
    return (_jd_from_date(d) - _ref_jd()) % DAYS_CYCLE


def day_master(d: date) -> str:
    return STEM_ELEMENTS[day_stem_index(d)]


def element_strength(birth_date: date) -> Literal["Strong", "Weak"]:
    year_elem = STEM_ELEMENTS[(birth_date.year - 4) % 10]
    month_elem = MONTH_BRANCH_ELEMENTS[birth_date.month]
    day_elem = day_master(birth_date)
    counts: dict[str, int] = {"Wood": 0, "Fire": 0, "Earth": 0, "Metal": 0, "Water": 0}
    counts[year_elem] += 2
    counts[month_elem] += 1
    counts[day_elem] += 1
    dominant = max(counts.values())
    total = sum(counts.values())
    return "Strong" if dominant >= 3 else "Weak"


def year_element(birth_date: date) -> str:
    return STEM_ELEMENTS[(birth_date.year - 4) % 10]


def month_element(birth_date: date) -> str:
    return MONTH_BRANCH_ELEMENTS[birth_date.month]


def assess_strength(birth_date: date) -> Literal["Strong", "Weak"]:
    counts: dict[str, int] = {"Wood": 0, "Fire": 0, "Earth": 0, "Metal": 0, "Water": 0}
    y_e = year_element(birth_date)
    m_e = month_element(birth_date)
    d_e = day_master(birth_date)
    counts[y_e] += 2
    counts[m_e] += 1
    counts[d_e] += 1
    dominant = max(counts.values())
    return "Strong" if dominant >= 3 else "Weak"


class QuizAnswers(BaseModel):
    q01: int = Field(..., ge=1, le=10, description="Systematic (1-5) vs Intuitive (6-10)")
    q02: int = Field(..., ge=1, le=10, description="Systematic (1-5) vs Intuitive (6-10)")
    q03: int = Field(..., ge=1, le=10, description="Systematic (1-5) vs Intuitive (6-10)")
    q04: int = Field(..., ge=1, le=10, description="Systematic (1-5) vs Intuitive (6-10)")
    q05: int = Field(..., ge=1, le=10, description="Systematic (1-5) vs Intuitive (6-10)")
    q06: int = Field(..., ge=1, le=10, description="Goal (1-5) vs Process (6-10)")
    q07: int = Field(..., ge=1, le=10, description="Goal (1-5) vs Process (6-10)")
    q08: int = Field(..., ge=1, le=10, description="Goal (1-5) vs Process (6-10)")
    q09: int = Field(..., ge=1, le=10, description="Goal (1-5) vs Process (6-10)")
    q10: int = Field(..., ge=1, le=10, description="Goal (1-5) vs Process (6-10)")
    q11: int = Field(..., ge=1, le=10, description="Internal (1-5) vs External (6-10)")
    q12: int = Field(..., ge=1, le=10, description="Internal (1-5) vs External (6-10)")
    q13: int = Field(..., ge=1, le=10, description="Internal (1-5) vs External (6-10)")
    q14: int = Field(..., ge=1, le=10, description="Internal (1-5) vs External (6-10)")
    q15: int = Field(..., ge=1, le=10, description="Internal (1-5) vs External (6-10)")


class PersonalityVector(BaseModel):
    cognitive_style: float = Field(..., description="1.0 = fully systematic, 0.0 = fully intuitive")
    orientation: float = Field(..., description="1.0 = fully goal, 0.0 = fully process")
    energy_source: float = Field(..., description="1.0 = fully external, 0.0 = fully internal")


class ArchetypeResult(BaseModel):
    archetype_id: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    dominant_elements: list[str]
    personality_vector: PersonalityVector


SYSTEMATIC_THRESHOLD = 5.5
ORIENTATION_THRESHOLD = 5.5
ENERGY_THRESHOLD = 5.5


def score_quiz(quiz: QuizAnswers) -> PersonalityVector:
    systematic_sum = sum([quiz.q01, quiz.q02, quiz.q03, quiz.q04, quiz.q05])
    orientation_sum = sum([quiz.q06, quiz.q07, quiz.q08, quiz.q09, quiz.q10])
    energy_sum = sum([quiz.q11, quiz.q12, quiz.q13, quiz.q14, quiz.q15])

    cognitive = (systematic_sum / 5.0 - 1) / 9
    cognitive = max(0.0, min(1.0, cognitive))

    orient = (orientation_sum / 5.0 - 1) / 9
    orient = max(0.0, min(1.0, orient))

    energy = (energy_sum / 5.0 - 1) / 9
    energy = max(0.0, min(1.0, energy))

    return PersonalityVector(
        cognitive_style=cognitive,
        orientation=orient,
        energy_source=energy,
    )


_ARCHETYPE_MAP = {
    ("Metal", "Strong", "systematic"): "strategic_commander",
    ("Metal", "Weak", "systematic"): "strategic_commander",
    ("Metal", "Strong", "intuitive"): "strategic_commander",
    ("Metal", "Weak", "intuitive"): "strategic_commander",
    ("Wood", "Strong", "systematic"): "visionary_builder",
    ("Wood", "Weak", "systematic"): "visionary_builder",
    ("Wood", "Strong", "intuitive"): "visionary_builder",
    ("Wood", "Weak", "intuitive"): "visionary_builder",
    ("Water", "Strong", "systematic"): "adaptive_navigator",
    ("Water", "Weak", "systematic"): "adaptive_navigator",
    ("Water", "Strong", "intuitive"): "adaptive_navigator",
    ("Water", "Weak", "intuitive"): "adaptive_navigator",
    ("Fire", "Strong", "systematic"): "energetic_catalyst",
    ("Fire", "Weak", "systematic"): "energetic_catalyst",
    ("Fire", "Strong", "intuitive"): "energetic_catalyst",
    ("Fire", "Weak", "intuitive"): "energetic_catalyst",
    ("Earth", "Strong", "systematic"): "steady_architect",
    ("Earth", "Weak", "systematic"): "steady_architect",
    ("Earth", "Strong", "intuitive"): "steady_architect",
    ("Earth", "Weak", "intuitive"): "steady_architect",
}


def calculate_archetype(
    birth_date: date,
    birth_time: time | None,
    quiz_answers: QuizAnswers,
) -> ArchetypeResult:
    year_elem = year_element(birth_date)
    month_elem = month_element(birth_date)
    day_elem = day_master(birth_date)

    counts: dict[str, int] = {"Wood": 0, "Fire": 0, "Earth": 0, "Metal": 0, "Water": 0}
    counts[year_elem] += 2
    counts[month_elem] += 1
    counts[day_elem] += 1
    dominant_count = max(counts.values())
    dominant_elements = [e for e, c in counts.items() if c == dominant_count]
    dominant_elements.sort(key=lambda e: (counts[e], e == year_elem), reverse=True)
    primary_element = dominant_elements[0]

    strength = "Strong" if dominant_count >= 3 else "Weak"

    personality = score_quiz(quiz_answers)
    cognitive = "systematic" if personality.cognitive_style < 0.5 else "intuitive"

    archetype_key = (primary_element, strength, cognitive)
    archetype_id = _ARCHETYPE_MAP.get(archetype_key, "adaptive_navigator")

    confidence = 0.75 if len(dominant_elements) == 1 else 0.65

    return ArchetypeResult(
        archetype_id=archetype_id,
        confidence=round(confidence, 2),
        dominant_elements=dominant_elements,
        personality_vector=personality,
    )