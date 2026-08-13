from __future__ import annotations

import calendar
from datetime import datetime, timedelta
from typing import Literal

Scale = Literal["daily", "weekly", "monthly"]


def floor_date(value: datetime, scale: Scale) -> datetime:
    value = value.replace(hour=0, minute=0, second=0, microsecond=0)
    if scale == "weekly":
        return value - timedelta(days=value.weekday())
    if scale == "monthly":
        return value.replace(day=1)
    return value


def next_date(value: datetime, scale: Scale) -> datetime:
    if scale == "daily":
        return value + timedelta(days=1)
    if scale == "weekly":
        return value + timedelta(days=7)
    year, month = value.year + (value.month == 12), value.month % 12 + 1
    return value.replace(year=year, month=month, day=1)


def buckets(
    start: datetime, finish: datetime, scale: Scale
) -> list[tuple[datetime, datetime]]:
    result = []
    cursor = floor_date(start, scale)
    while cursor <= finish:
        following = next_date(cursor, scale)
        result.append((cursor, following))
        cursor = following
    return result


def label(value: datetime, scale: Scale) -> str:
    if scale == "daily":
        return value.strftime("%d")
    if scale == "weekly":
        return value.strftime("%d %b")
    return calendar.month_abbr[value.month]
