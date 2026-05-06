"""Tests for the archetype scoring engine."""

from datetime import date, time

import pytest

from scoring import (
    QuizAnswers,
    assess_strength,
    calculate_archetype,
    day_master,
    day_stem_index,
    score_quiz,
)


def test_heidi_profile_strategic_commander():
    """
    Heidi: 庚 Geng Metal, Strong, Systematic-Intuitive → strategic_commander
    Born 1990-xx-xx (Geng/Metal year), Strong day master, systematic quiz answers.
    """
    birth_date = date(1990, 3, 15)
    quiz = QuizAnswers(
        q01=3, q02=4, q03=3, q04=4, q05=3,
        q06=6, q07=7, q08=6, q09=7, q10=6,
        q11=3, q12=4, q13=3, q14=4, q15=3,
    )
    result = calculate_archetype(birth_date, None, quiz)
    assert result.archetype_id == "strategic_commander", f"Expected strategic_commander, got {result.archetype_id}"


def test_profile_metal_strong_systematic():
    birth_date = date(1990, 1, 1)
    quiz = QuizAnswers(
        q01=3, q02=3, q03=3, q04=3, q05=3,
        q06=3, q07=3, q08=3, q09=3, q10=3,
        q11=3, q12=3, q13=3, q14=3, q15=3,
    )
    result = calculate_archetype(birth_date, None, quiz)
    assert result.archetype_id == "strategic_commander"


def test_profile_wood_intuitive():
    birth_date = date(1984, 6, 15)
    quiz = QuizAnswers(
        q01=7, q02=8, q03=7, q04=8, q05=7,
        q06=7, q07=8, q08=7, q09=8, q10=7,
        q11=7, q12=8, q13=7, q14=8, q15=7,
    )
    result = calculate_archetype(birth_date, None, quiz)
    assert result.archetype_id == "visionary_builder"


def test_profile_water_intuitive():
    birth_date = date(1992, 11, 5)
    quiz = QuizAnswers(
        q01=8, q02=7, q03=8, q04=7, q05=8,
        q06=7, q07=8, q08=7, q09=8, q10=7,
        q11=7, q12=8, q13=7, q14=8, q15=7,
    )
    result = calculate_archetype(birth_date, None, quiz)
    assert result.archetype_id == "adaptive_navigator"


def test_profile_fire_goal():
    birth_date = date(1986, 5, 15)
    quiz = QuizAnswers(
        q01=3, q02=4, q03=3, q04=4, q05=3,
        q06=3, q07=4, q08=3, q09=4, q10=3,
        q11=3, q12=4, q13=3, q14=4, q15=3,
    )
    result = calculate_archetype(birth_date, None, quiz)
    assert result.archetype_id == "energetic_catalyst"


def test_profile_earth_systematic():
    birth_date = date(1988, 1, 31)
    quiz = QuizAnswers(
        q01=2, q02=3, q03=2, q04=3, q05=2,
        q06=2, q07=3, q08=2, q09=3, q10=2,
        q11=2, q12=3, q13=2, q14=3, q15=2,
    )
    result = calculate_archetype(birth_date, None, quiz)
    assert result.archetype_id == "steady_architect"


def test_confidence_in_range():
    birth_date = date(1990, 1, 1)
    quiz = QuizAnswers(
        q01=5, q02=5, q03=5, q04=5, q05=5,
        q06=5, q07=5, q08=5, q09=5, q10=5,
        q11=5, q12=5, q13=5, q14=5, q15=5,
    )
    result = calculate_archetype(birth_date, None, quiz)
    assert 0.0 <= result.confidence <= 1.0


def test_personality_vector_in_range():
    quiz = QuizAnswers(
        q01=1, q02=1, q03=1, q04=1, q05=1,
        q06=1, q07=1, q08=1, q09=1, q10=1,
        q11=1, q12=1, q13=1, q14=1, q15=1,
    )
    pv = score_quiz(quiz)
    assert 0.0 <= pv.cognitive_style <= 1.0
    assert 0.0 <= pv.orientation <= 1.0
    assert 0.0 <= pv.energy_source <= 1.0


def test_day_stem_index_deterministic():
    d = date(1990, 3, 15)
    idx1 = day_stem_index(d)
    idx2 = day_stem_index(d)
    assert idx1 == idx2
    assert 0 <= idx1 < 10


def test_day_master_stable():
    assert day_master(date(2000, 1, 1)) == day_master(date(2000, 1, 1))


def test_assess_strength():
    birth_date = date(1990, 1, 1)
    strength = assess_strength(birth_date)
    assert strength in ("Strong", "Weak")


def test_dominant_elements_non_empty():
    birth_date = date(1990, 3, 15)
    quiz = QuizAnswers(
        q01=5, q02=5, q03=5, q04=5, q05=5,
        q06=5, q07=5, q08=5, q09=5, q10=5,
        q11=5, q12=5, q13=5, q14=5, q15=5,
    )
    result = calculate_archetype(birth_date, None, quiz)
    assert len(result.dominant_elements) >= 1
    assert all(e in ["Metal", "Wood", "Water", "Fire", "Earth"] for e in result.dominant_elements)