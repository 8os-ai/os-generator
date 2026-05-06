"""
BaZi Engine — element calculator using birth year heavenly stem (primary)
and birth month earthly branch (secondary influence).

BaZi (Four Pillars) is complex; for MVP we derive the dominant element from
the birth year's heavenly stem, which is well-defined and deterministic.
The birth month's earthly branch is incorporated as a secondary influence:
it can reinforce the year element but does not override it.

Heavenly stem cycle (10 stems, each linked to an element):
  Jia (Wood), Yi (Wood), Bing (Fire), Ding (Fire), Wu (Earth),
  Ji (Earth), Geng (Metal), Xin (Metal), Ren (Water), Gui (Water)

Stems repeat every 10 years. Year 4 CE is Jia year (stem index 0).

Earthly branch cycle (12 branches, mapped to months):
  Tiger(Feb)=Wood, Rabbit(Mar)=Wood, Dragon(Apr)=Earth, Snake(May)=Fire,
  Horse(Jun)=Fire, Goat(Jul)=Earth, Monkey(Aug)=Metal, Rooster(Sep)=Metal,
  Dog(Oct)=Earth, Pig(Nov)=Water, Rat(Dec)=Water, Ox(Jan)=Earth

Note: traditional BaZi uses solar-term boundaries (~Feb 4) rather than
calendar months. This implementation uses Gregorian months as an approximation.
"""

from datetime import date

_MIN_YEAR = 1900
_MAX_YEAR = 2100

STEM_ELEMENTS = [
    "Wood",   # Jia
    "Wood",   # Yi
    "Fire",   # Bing
    "Fire",   # Ding
    "Earth",  # Wu
    "Earth",  # Ji
    "Metal",  # Geng
    "Metal",  # Xin
    "Water",  # Ren
    "Water",  # Gui
]

# Month earthly branch → element mapping (keyed by Gregorian month 1–12)
MONTH_BRANCH_ELEMENTS = {
    1:  "Earth",  # January   — Ox (Chou) branch
    2:  "Wood",   # February  — Tiger (Yin) branch
    3:  "Wood",   # March     — Rabbit (Mao) branch
    4:  "Earth",  # April     — Dragon (Chen) branch
    5:  "Fire",   # May       — Snake (Si) branch
    6:  "Fire",   # June      — Horse (Wu) branch
    7:  "Earth",  # July      — Goat (Wei) branch
    8:  "Metal",  # August    — Monkey (Shen) branch
    9:  "Metal",  # September — Rooster (You) branch
    10: "Earth",  # October   — Dog (Xu) branch
    11: "Water",  # November  — Pig (Hai) branch
    12: "Water",  # December  — Rat (Zi) branch
}

# Scoring weights: year is primary, month is secondary
_YEAR_WEIGHT = 2
_MONTH_WEIGHT = 1

# Reference: year 4 CE is a Jia year (stem index 0)
_REFERENCE_YEAR = 4
_STEM_CYCLE = 10


def _validate_date(birth_date: date) -> None:
    if birth_date.year < _MIN_YEAR or birth_date.year > _MAX_YEAR:
        raise ValueError(
            f"Birth year must be between {_MIN_YEAR} and {_MAX_YEAR}, got {birth_date.year}"
        )
    if birth_date > date.today():
        raise ValueError("Birth date cannot be in the future")


def year_element(birth_date: date) -> str:
    """Return the element derived from the birth year's heavenly stem."""
    stem_index = (birth_date.year - _REFERENCE_YEAR) % _STEM_CYCLE
    return STEM_ELEMENTS[stem_index]


def month_element(birth_date: date) -> str:
    """Return the element derived from the birth month's earthly branch."""
    return MONTH_BRANCH_ELEMENTS[birth_date.month]


def dominant_element(birth_date: date) -> str:
    """Return the dominant BaZi element for a given birth date.

    Scoring:
      - Year heavenly stem contributes weight 2 to its element.
      - Month earthly branch contributes weight 1 to its element.

    The element with the highest total score wins. Because the year always
    carries twice the weight of the month, the year element can never be
    overridden by the month alone — but the month reinforces or adds a
    secondary pull that is meaningful when the same element appears in both
    pillars (raising its combined score to 3) versus when they differ.

    Raises:
        ValueError: if birth_date is outside 1900-2100 range or is in the future.

    Future roadmap: add day and hour pillars, yin/yang distinctions, and
    clash/combination interactions.
    """
    _validate_date(birth_date)
    y_elem = year_element(birth_date)
    m_elem = month_element(birth_date)

    # Tally scores across all five elements
    scores: dict[str, int] = {
        "Wood": 0, "Fire": 0, "Earth": 0, "Metal": 0, "Water": 0
    }
    scores[y_elem] += _YEAR_WEIGHT
    scores[m_elem] += _MONTH_WEIGHT

    # Return the element with the highest score.
    # Ties are broken by year element (it always has at least _YEAR_WEIGHT points).
    return max(scores, key=lambda e: (scores[e], e == y_elem))
