from datetime import date

import pytest

from nldate import parse

# Fixed reference date so tests are deterministic
TODAY = date(2025, 3, 10)  # Monday


# --- Absolute dates ---

@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("December 1st, 2025", date(2025, 12, 1)),
        ("March 15, 2024", date(2024, 3, 15)),
        ("February 29th, 2024", date(2024, 2, 29)),
        ("Feb 29 2024", date(2024, 2, 29)),
        ("29 February 2024", date(2024, 2, 29)),
        ("2025-07-04", date(2025, 7, 4)),
        ("2024-02-29", date(2024, 2, 29)),
        ("01/20/2026", date(2026, 1, 20)),
        ("02/29/2024", date(2024, 2, 29)),
        ("13/01/2025", date(2025, 1, 13)),
        ("01/13/2025", date(2025, 1, 13)),
    ],
)
def test_absolute_supported_formats(text: str, expected: date) -> None:
    assert parse(text, TODAY) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("March 2025", date(2025, 3, 1)),
        ("December 2025", date(2025, 12, 1)),
        ("2025", date(2025, 3, 1)),
    ],
)
def test_partial_absolute_dates_prefer_first_day(text: str, expected: date) -> None:
    assert parse(text, TODAY) == expected


# --- Relative: days ---

@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("today", TODAY),
        ("TODAY", TODAY),
        (" tomorrow ", date(2025, 3, 11)),
        ("yesterday", date(2025, 3, 9)),
        ("in 5 days", date(2025, 3, 15)),
        ("3 days from today", date(2025, 3, 13)),
        ("0 days after today", TODAY),
        ("in a day", date(2025, 3, 11)),
        ("in an week", date(2025, 3, 17)),
        ("in two weeks", date(2025, 3, 24)),
        ("two weeks from today", date(2025, 3, 24)),
        ("twenty days after today", date(2025, 3, 30)),
        ("thirty days before April 1, 2025", date(2025, 3, 2)),
        ("fifty weeks after today", date(2026, 2, 23)),
    ],
)
def test_relative_days_weeks_and_word_numbers(text: str, expected: date) -> None:
    assert parse(text, TODAY) == expected


# --- Relative: weeks / months / years ---

@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("in 2 weeks", date(2025, 3, 24)),
        ("2 weeks before today", date(2025, 2, 24)),
        ("2 weeks after yesterday", date(2025, 3, 23)),
        ("3 months after today", date(2025, 6, 10)),
        ("ten years before today", date(2015, 3, 10)),
        ("1 year and 2 months after yesterday", date(2026, 5, 9)),
        ("1 year and 2 months and 3 days after yesterday", date(2026, 5, 12)),
        ("5 days before December 1st, 2025", date(2025, 11, 26)),
        ("10 days after January 1st, 2026", date(2026, 1, 11)),
    ],
)
def test_relative_offsets_before_after_and_from(text: str, expected: date) -> None:
    assert parse(text, TODAY) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1 day before March 1, 2024", date(2024, 2, 29)),
        ("1 day after February 28, 2024", date(2024, 2, 29)),
        ("1 year after February 29, 2024", date(2025, 2, 28)),
        ("1 month after January 31, 2025", date(2025, 2, 28)),
        ("1 month before March 31, 2025", date(2025, 2, 28)),
        ("3 months from January 31, 2025", date(2025, 4, 30)),
        ("13 months after January 31, 2024", date(2025, 2, 28)),
    ],
)
def test_calendar_boundaries_and_month_end_clamping(
    text: str,
    expected: date,
) -> None:
    assert parse(text, TODAY) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("5 days before next Tuesday", date(2025, 3, 6)),
        ("5 days after last Friday", date(2025, 3, 12)),
        ("1 week before 2 days after today", date(2025, 3, 5)),
        ("2 months after 1 week before April 30, 2025", date(2025, 6, 23)),
    ],
)
def test_offsets_can_use_nested_anchors(text: str, expected: date) -> None:
    assert parse(text, TODAY) == expected


# --- Weekday navigation ---

@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("next Monday", date(2025, 3, 17)),
        ("next Tuesday", date(2025, 3, 11)),
        ("next Wednesday", date(2025, 3, 12)),
        ("next Thursday", date(2025, 3, 13)),
        ("next Friday", date(2025, 3, 14)),
        ("next Saturday", date(2025, 3, 15)),
        ("next Sunday", date(2025, 3, 16)),
        ("last Monday", date(2025, 3, 3)),
        ("last Tuesday", date(2025, 3, 4)),
        ("last Wednesday", date(2025, 3, 5)),
        ("last Thursday", date(2025, 3, 6)),
        ("last Friday", date(2025, 3, 7)),
        ("last Saturday", date(2025, 3, 8)),
        ("last Sunday", date(2025, 3, 9)),
    ],
)
def test_next_and_last_weekday_rollover(text: str, expected: date) -> None:
    assert parse(text, TODAY) == expected


def test_next_same_weekday_is_one_full_week_later() -> None:
    assert parse("next monday", TODAY) == date(2025, 3, 17)


def test_last_same_weekday_is_one_full_week_earlier() -> None:
    assert parse("last monday", TODAY) == date(2025, 3, 3)


# --- Error handling ---

@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "not a date at all zzz",
        "zero days after today",
        "next Tue",
        "last Fri",
        "next tuesday, please",
        "February 30, 2025",
        "April 31, 2025",
        "02/29/2025",
        "2025-02-29",
        "32 January 2025",
    ],
)
def test_invalid_dates_raise_value_error(text: str) -> None:
    with pytest.raises(ValueError):
        parse(text, TODAY)
