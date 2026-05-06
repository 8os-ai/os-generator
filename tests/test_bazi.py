"""Tests for the BaZi element calculator."""

from datetime import date

import pytest

from bazi import dominant_element, month_element, year_element


# ---------------------------------------------------------------------------
# Original year-pillar tests (must remain passing)
# ---------------------------------------------------------------------------

def test_metal_element():
    # Geng year: 1990 → Metal
    assert dominant_element(date(1990, 1, 1)) == "Metal"


def test_wood_element():
    # Jia year: 1984 → Wood
    assert dominant_element(date(1984, 6, 15)) == "Wood"


def test_water_element():
    # Ren year: 1992 → Water
    assert dominant_element(date(1992, 3, 10)) == "Water"


def test_fire_element():
    # Bing year: 1986 → Fire
    assert dominant_element(date(1986, 11, 22)) == "Fire"


def test_earth_element():
    # Wu year: 1988 → Earth
    assert dominant_element(date(1988, 5, 5)) == "Earth"


def test_heidi_is_strong_metal():
    """
    CEO Heidi test case: birth date must map to Strong Metal → Strategic Commander.
    Heidi's birth date provided by CEO: 1990-xx-xx (Geng/Metal year).
    Using 1990-01-01 as representative Metal year date.
    """
    # Any date in 1990 is a Geng (Metal) year
    element = dominant_element(date(1990, 1, 1))
    assert element == "Metal", f"Expected Metal for 1990, got {element}"


# ---------------------------------------------------------------------------
# year_element() helper tests
# ---------------------------------------------------------------------------

def test_year_element_cycles():
    """Heavenly stem repeats every 10 years."""
    assert year_element(date(2000, 6, 1)) == year_element(date(1990, 6, 1))
    assert year_element(date(2010, 6, 1)) == year_element(date(2000, 6, 1))


def test_year_element_all_five():
    """Each of the five elements is reachable via the year stem."""
    assert year_element(date(1984, 1, 1)) == "Wood"    # Jia
    assert year_element(date(1986, 1, 1)) == "Fire"    # Bing
    assert year_element(date(1988, 1, 1)) == "Earth"   # Wu
    assert year_element(date(1990, 1, 1)) == "Metal"   # Geng
    assert year_element(date(1992, 1, 1)) == "Water"   # Ren


# ---------------------------------------------------------------------------
# month_element() helper tests — earthly branch mapping
# ---------------------------------------------------------------------------

def test_month_element_wood_months():
    # February (Tiger) and March (Rabbit) are both Wood
    assert month_element(date(2000, 2, 15)) == "Wood"
    assert month_element(date(2000, 3, 20)) == "Wood"


def test_month_element_fire_months():
    # May (Snake) and June (Horse) are both Fire
    assert month_element(date(2000, 5, 10)) == "Fire"
    assert month_element(date(2000, 6, 21)) == "Fire"


def test_month_element_earth_months():
    # Jan (Ox), Apr (Dragon), Jul (Goat), Oct (Dog) are Earth
    for month in (1, 4, 7, 10):
        assert month_element(date(2000, month, 15)) == "Earth", f"Month {month} should be Earth"


def test_month_element_metal_months():
    # August (Monkey) and September (Rooster) are Metal
    assert month_element(date(2000, 8, 8)) == "Metal"
    assert month_element(date(2000, 9, 9)) == "Metal"


def test_month_element_water_months():
    # November (Pig) and December (Rat) are Water
    assert month_element(date(2000, 11, 11)) == "Water"
    assert month_element(date(2000, 12, 31)) == "Water"


# ---------------------------------------------------------------------------
# Month-boundary edge cases: year element always dominates
# ---------------------------------------------------------------------------

def test_year_dominates_when_month_differs():
    """Year (weight 2) always beats month (weight 1) alone."""
    # 1990 = Metal year, January = Earth month → Metal wins (2 > 1)
    assert dominant_element(date(1990, 1, 15)) == "Metal"
    # 1992 = Water year, August = Metal month → Water wins
    assert dominant_element(date(1992, 8, 20)) == "Water"
    # 1984 = Wood year, October = Earth month → Wood wins
    assert dominant_element(date(1984, 10, 5)) == "Wood"


def test_month_reinforces_year_element():
    """When year and month share the same element, the score is 3 vs 0."""
    # 1990 = Metal year, August = Metal month → strongly Metal (score 3)
    assert dominant_element(date(1990, 8, 15)) == "Metal"
    # 1990 = Metal year, September = Metal month → strongly Metal (score 3)
    assert dominant_element(date(1990, 9, 30)) == "Metal"


def test_month_reinforcement_wood():
    # 1984 = Wood year, February = Wood month → reinforced Wood
    assert dominant_element(date(1984, 2, 20)) == "Wood"
    # 1984 = Wood year, March = Wood month → reinforced Wood
    assert dominant_element(date(1984, 3, 10)) == "Wood"


def test_month_reinforcement_water():
    # 1992 = Water year, November = Water month → reinforced Water
    assert dominant_element(date(1992, 11, 5)) == "Water"
    # 1992 = Water year, December = Water month → reinforced Water
    assert dominant_element(date(1992, 12, 25)) == "Water"


def test_month_reinforcement_fire():
    # 1986 = Fire year, May = Fire month → reinforced Fire
    assert dominant_element(date(1986, 5, 15)) == "Fire"
    # 1986 = Fire year, June = Fire month → reinforced Fire
    assert dominant_element(date(1986, 6, 1)) == "Fire"


def test_month_reinforcement_earth():
    # 1988 = Earth year, January = Earth month → reinforced Earth
    assert dominant_element(date(1988, 1, 31)) == "Earth"
    # 1988 = Earth year, April = Earth month → reinforced Earth
    assert dominant_element(date(1988, 4, 4)) == "Earth"


def test_year_boundary_different_months():
    """Same year, different months: year element is stable across the year."""
    for month in range(1, 13):
        result = dominant_element(date(1990, month, 1))
        assert result == "Metal", (
            f"1990 is a Metal year; month {month} should not override. Got {result}"
        )


def test_pre_and_post_year_boundary():
    """Dec of one year vs Jan of next: different year elements possible."""
    # Dec 1989 = Ji year (Earth), Dec month = Water
    assert dominant_element(date(1989, 12, 31)) == "Earth"
    # Jan 1990 = Geng year (Metal), Jan month = Earth
    assert dominant_element(date(1990, 1, 1)) == "Metal"


# ---------------------------------------------------------------------------
# Date validation tests
# ---------------------------------------------------------------------------

def test_valid_date_range_1900():
    """1900-01-01 is the minimum valid year."""
    assert dominant_element(date(1900, 1, 1)) == "Metal"


def test_valid_date_range_upper_edge():
    """A date in 2000 is within 1900-2100 range and clearly in the past."""
    assert dominant_element(date(2000, 1, 1)) == "Metal"


def test_invalid_date_too_old():
    """Dates before 1900 should raise ValueError."""
    with pytest.raises(ValueError, match="Birth year must be between 1900 and 2100"):
        dominant_element(date(1899, 12, 31))


def test_invalid_date_too_recent():
    """Dates after 2100 should raise ValueError."""
    with pytest.raises(ValueError, match="Birth year must be between 1900 and 2100"):
        dominant_element(date(2101, 1, 1))


def test_future_date_rejected():
    """Future dates should raise ValueError."""
    import datetime
    future = datetime.date.today() + datetime.timedelta(days=365)
    with pytest.raises(ValueError, match="Birth date cannot be in the future"):
        dominant_element(future)
