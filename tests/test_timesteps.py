from contextlib import nullcontext
from datetime import date, datetime, time, timedelta
from typing import List, Optional, Tuple, Union

import pytest

from earthkit.time.calendar import (
    FRIDAY,
    MONDAY,
    SATURDAY,
    SUNDAY,
    THURSDAY,
    TUESDAY,
    WEDNESDAY,
    MonthInYear,
    Weekday,
)
from earthkit.time.timesteps import (
    day_from_range,
    expand_range,
    hours_from_delta,
    month_from_range,
    month_from_startdate,
    parse_range,
    range_from_day,
    range_from_month,
    range_from_week,
    regular_ranges,
    startdate_from_month,
    week_from_range,
)


@pytest.mark.parametrize(
    "arg, expected",
    [
        pytest.param("24-48", (24, 48), id="range"),
        pytest.param("12", (12, 12), id="instant"),
        pytest.param("abc", None, id="invalid"),
    ],
)
def test_parse_range(arg: str, expected: Optional[Tuple[int, int]]):
    context = (
        pytest.raises(ValueError, match="^Invalid step range:")
        if expected is None
        else nullcontext()
    )
    with context:
        assert parse_range(arg) == expected


@pytest.mark.parametrize(
    "start, end, width, interval, expected",
    [
        pytest.param(
            0,
            120,
            24,
            24,
            [(0, 24), (24, 48), (48, 72), (72, 96), (96, 120)],
            id="0/120/24/24",
        ),
        pytest.param(24, 48, 12, 6, [(24, 36), (30, 42), (36, 48)], id="24/48/12/6"),
        pytest.param(
            120, 240, 0, 48, [(120, 120), (168, 168), (216, 216)], id="120/240/0/48"
        ),
    ],
)
def test_regular_ranges(
    start: int, end: int, width: int, interval: int, expected: List[Tuple[int, int]]
):
    ranges = regular_ranges(start, end, width, interval)
    assert list(ranges) == expected


@pytest.mark.parametrize(
    "steprange, interval, include_start, expected",
    [
        pytest.param("0-24", 6, None, [0, 6, 12, 18, 24], id="0-24/6"),
        pytest.param("12-36", 12, True, [12, 24, 36], id="12-36/12-start"),
        pytest.param("48-96", 24, False, [72, 96], id="48-96/24-nostart"),
        pytest.param(
            (120, 168), 12, None, [120, 132, 144, 156, 168], id="tup-120-168/12"
        ),
        pytest.param(
            (240, 360),
            24,
            True,
            [240, 264, 288, 312, 336, 360],
            id="tup-240-360/24-start",
        ),
        pytest.param((0, 48), 12, False, [12, 24, 36, 48], id="tup-0-48/12-nostart"),
    ],
)
def test_expand_range(
    steprange: Union[str, Tuple[int, int]],
    interval: int,
    include_start: Optional[bool],
    expected: List[int],
):
    steps = (
        expand_range(steprange, interval)
        if include_start is None
        else expand_range(steprange, interval, include_start)
    )
    assert list(steps) == expected


@pytest.mark.parametrize(
    "delta, expected",
    [
        pytest.param(timedelta(hours=5), 5, id="5h"),
        pytest.param(timedelta(days=2), 48, id="2d"),
        pytest.param(timedelta(days=1, hours=12), 36, id="1d12h"),
        pytest.param(timedelta(hours=120), 120, id="120h"),
    ],
)
def test_hours_from_delta(delta: timedelta, expected: int):
    assert hours_from_delta(delta) == expected


day_range_params = [
    pytest.param(1, 0, 0, 0, id="1/0/0"),
    pytest.param(4, 12, 0, 12, id="4/12/0"),
    pytest.param(3, time(6), 12, 6, id="4/time6/12"),
    pytest.param(2, datetime(2024, 6, 22, 18), time(12), 18, id="2/datetime18/time12"),
]


@pytest.mark.parametrize("day, base, daystart, exp_shift", day_range_params)
def test_range_from_day(
    day: int,
    base: Union[datetime, time, int],
    daystart: Union[time, int],
    exp_shift: int,
):
    assert range_from_day(day, base, daystart) == (
        exp_shift + 24 * (day - 1),
        exp_shift + 24 * day,
    )


@pytest.mark.parametrize("day, base, daystart, shift", day_range_params)
def test_day_from_range(
    day: int,
    base: Union[datetime, time, int],
    daystart: Union[time, int],
    shift: int,
):
    steprange = (
        (day - 1) * 24 + shift,
        day * 24 + shift,
    )
    assert day_from_range(steprange, base, daystart) == day


def test_day_from_range_invalid():
    with pytest.raises(ValueError, match="Range '.+' is not one day long"):
        day_from_range((0, 168))

    with pytest.raises(ValueError, match="Range '.+' does not align on a day"):
        day_from_range((1, 25))


week_range_params = [
    pytest.param(1, None, None, 0, 0, id="1/None/None"),
    pytest.param(5, None, None, 0, 0, id="5/None/None"),
    pytest.param(2, WEDNESDAY, None, 0, 0, id="2/wday/None"),
    pytest.param(3, date(2022, 7, 19), None, 0, 0, id="2/date/None"),
    pytest.param(4, datetime(2023, 3, 14, 15), None, 0, 9, id="4/datetime/None"),
    pytest.param(5, time(13), None, 0, 11, id="5/time/None"),
    pytest.param(1, (TUESDAY, time(9)), None, 0, 15, id="1/wday-time/None"),
    pytest.param(4, date(2025, 5, 17), MONDAY, 2, 0, id="4/date/wday"),
    pytest.param(3, THURSDAY, SUNDAY, 3, 0, id="3/wday/wday"),
    pytest.param(2, datetime(2024, 2, 29, 22), WEDNESDAY, 5, 2, id="2/datetime/wday"),
    pytest.param(4, (SATURDAY, time(20)), FRIDAY, 5, 4, id="4/wday-time/wday"),
]


@pytest.mark.parametrize("week, base, weekstart, expd, exph", week_range_params)
def test_range_from_week(
    week: int,
    base: Union[date, datetime, time, Weekday, Tuple[Weekday, time], None],
    weekstart: Union[Weekday, None],
    expd: int,
    exph: int,
):
    assert range_from_week(week, base, weekstart) == (
        ((week - 1) * 7 + expd) * 24 + exph,
        (week * 7 + expd) * 24 + exph,
    )


@pytest.mark.parametrize(
    "week, base, weekstart, shift_days, shift_hours", week_range_params
)
def test_week_from_range(
    week: int,
    base: Union[date, datetime, time, Weekday, Tuple[Weekday, time], None],
    weekstart: Union[Weekday, None],
    shift_days: int,
    shift_hours: int,
):
    steprange = (
        ((week - 1) * 7 + shift_days) * 24 + shift_hours,
        (week * 7 + shift_days) * 24 + shift_hours,
    )
    assert week_from_range(steprange, base, weekstart) == week


def test_week_from_range_invalid():
    with pytest.raises(ValueError, match="Range '.+' is not one week long"):
        week_from_range((0, 24))

    with pytest.raises(ValueError, match="Range '.+' does not align on a week"):
        week_from_range((1, 7 * 24 + 1))


@pytest.mark.parametrize(
    "month, base, mstart, expected",
    [
        pytest.param(1, (2026, 1), 1, date(2026, 1, 1), id="1/202601-tup"),
        pytest.param(2, MonthInYear(2025, 1), 1, date(2025, 2, 1), id="2/202501-month"),
        pytest.param(3, date(2024, 1, 15), 1, date(2024, 4, 1), id="3/20240115-date"),
        pytest.param(
            4, date(2023, 1, 15), 15, date(2023, 4, 15), id="4/20230115-date/15"
        ),
        pytest.param(
            5, date(2022, 1, 1), 15, date(2022, 5, 15), id="5/20220101-date/15"
        ),
        pytest.param(6, date(2021, 8, 1), 1, date(2022, 1, 1), id="6/20210801-date"),
    ],
)
def test_startdate_from_month(
    month: int,
    base: Union[date, MonthInYear, Tuple[int, int]],
    mstart: int,
    expected: date,
):
    assert startdate_from_month(month, base, mstart) == expected


@pytest.mark.parametrize(
    "base, start, expected",
    [
        pytest.param((2026, 1), (2026, 1), 1, id="202601-tup/202601-tup"),
        pytest.param(MonthInYear(2025, 1), (2025, 2), 2, id="202501-month/202502-tup"),
        pytest.param(date(2024, 1, 1), (2024, 3), 3, id="20240101/202403-tup"),
        pytest.param(
            date(2023, 1, 1), MonthInYear(2023, 4), 4, id="20230101/202304-month"
        ),
        pytest.param(date(2022, 1, 1), date(2022, 5, 1), 5, id="20220101/20230401"),
        pytest.param(
            MonthInYear(2021, 1),
            MonthInYear(2021, 6),
            6,
            id="202101-month/202104-month",
        ),
        pytest.param(date(2020, 1, 15), date(2020, 8, 1), 7, id="20200115/20200801"),
        pytest.param(date(2019, 1, 15), date(2019, 8, 15), 8, id="20190115/20190815"),
        pytest.param(date(2018, 1, 1), date(2018, 9, 15), 9, id="20180101/20180915"),
        pytest.param(date(2017, 4, 1), date(2018, 1, 1), 10, id="20170401/20180101"),
    ],
)
def test_month_from_startdate(
    base: Union[date, MonthInYear, Tuple[int, int]],
    start: Union[date, MonthInYear, Tuple[int, int]],
    expected: int,
):
    assert month_from_startdate(base, start) == expected


month_range_params = [
    pytest.param(1, (2026, 1), 1, (0, 744), id="1/202601-tup"),
    pytest.param(2, MonthInYear(2025, 1), 1, (744, 1416), id="2/202501-month"),
    pytest.param(3, date(2024, 1, 1), 1, (1440, 2184), id="3/20240101-date"),
    pytest.param(4, date(2023, 1, 15), 1, (2544, 3288), id="4/20230115-date"),
    pytest.param(5, date(2022, 1, 15), 15, (2880, 3624), id="5/20201115-date/15"),
]


@pytest.mark.parametrize(
    "month, base, mstart, expected",
    month_range_params,
)
def test_range_from_month(
    month: int,
    base: Union[date, MonthInYear, Tuple[int, int]],
    mstart: int,
    expected: Tuple[int, int],
):
    assert range_from_month(month, base, mstart) == expected


@pytest.mark.parametrize(
    "month, base, mstart, steprange",
    month_range_params,
)
def test_month_from_range(
    month: int,
    base: Union[date, MonthInYear, Tuple[int, int]],
    mstart: int,
    steprange: Tuple[int, int],
):
    assert month_from_range(steprange, base, mstart) == month


def test_month_from_range_invalid():
    with pytest.raises(
        ValueError, match="Range '.+' does not align on a forecast month"
    ):
        month_from_range((3216, 3960), (2022, 1))

    with pytest.raises(ValueError, match="Range '.+' is not one month long"):
        month_from_range((0, 168), (2022, 1))
