import re
from datetime import date, datetime, timedelta

import dateparser
from dateutil.relativedelta import relativedelta

_WEEKDAYS: dict[str, int] = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}

_WORD_TO_NUM: dict[str, int] = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50,
}

_UNIT_PAT = r"(?:days?|weeks?|months?|years?)"


def _normalize(s: str) -> str:
    """Replace word numbers that precede a time unit with digits."""
    def _replace(m: re.Match[str]) -> str:
        return str(_WORD_TO_NUM[m.group(1).lower()])

    pattern = (
        r"\b(" + "|".join(re.escape(w) for w in _WORD_TO_NUM) + r")"
        + r"(?=\s+" + _UNIT_PAT + r")"
    )
    return re.sub(pattern, _replace, s, flags=re.IGNORECASE)


def _parse_offset(s: str) -> relativedelta:
    """Parse '5 days', '1 year and 2 months', etc. into a relativedelta."""
    rd = relativedelta()
    for m in re.finditer(r"(\d+)\s+(" + _UNIT_PAT + r")", s, re.IGNORECASE):
        n = int(m.group(1))
        unit = m.group(2).rstrip("s").lower()
        if unit == "day":
            rd += relativedelta(days=n)
        elif unit == "week":
            rd += relativedelta(weeks=n)
        elif unit == "month":
            rd += relativedelta(months=n)
        elif unit == "year":
            rd += relativedelta(years=n)
    return rd


def _next_weekday(ref: date, weekday: int) -> date:
    days_ahead = (weekday - ref.weekday()) % 7 or 7
    return ref + timedelta(days=days_ahead)


def _last_weekday(ref: date, weekday: int) -> date:
    days_behind = (ref.weekday() - weekday) % 7 or 7
    return ref - timedelta(days=days_behind)


def parse(s: str, today: date | None = None) -> date:
    reference = today or date.today()
    normalized = _normalize(s)
    nl = normalized.strip().lower()

    # "next WEEKDAY"
    m1 = re.fullmatch(r"next\s+(\w+)", nl)
    if m1 and m1.group(1) in _WEEKDAYS:
        return _next_weekday(reference, _WEEKDAYS[m1.group(1)])

    # "last WEEKDAY"
    m2 = re.fullmatch(r"last\s+(\w+)", nl)
    if m2 and m2.group(1) in _WEEKDAYS:
        return _last_weekday(reference, _WEEKDAYS[m2.group(1)])

    # "N [and M] units before/after/from ANCHOR"
    m3 = re.match(r"^(.+?)\s+(before|after|from)\s+(.+)$", nl)
    if m3:
        rd = _parse_offset(m3.group(1))
        if rd != relativedelta():
            anchor = parse(m3.group(3), reference)
            return anchor - rd if m3.group(2) == "before" else anchor + rd

    # Fallback: dateparser
    settings: dict[str, object] = {
        "RELATIVE_BASE": datetime(reference.year, reference.month, reference.day),
        "PREFER_DAY_OF_MONTH": "first",
        "PREFER_DATES_FROM": "future",
        "RETURN_AS_TIMEZONE_AWARE": False,
    }
    result = dateparser.parse(normalized, settings=settings)

    if result is None:
        raise ValueError(f"Could not parse date string: {s!r}")

    return result.date()  # type: ignore[no-any-return]
