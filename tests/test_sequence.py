import bisect
import calendar
from datetime import date
from typing import List, Optional, Tuple

import pytest

from earthkit.dates.calendar import FRIDAY, MONDAY, THURSDAY
from earthkit.dates.sequence import (
    DailySequence,
    MonthlySequence,
    Sequence,
    WeeklySequence,
    YearlySequence,
)


class ExcludeLeapFeb28:
    def __contains__(self, day: date) -> bool:
        if not day.month == 2:
            return False
        if not calendar.isleap(day.year):
            return False
        return day.day == 28


class ExcludeNonTenYears:
    def __contains__(self, day: date) -> bool:
        return day.year % 10 != 0


@pytest.mark.parametrize(
    "seq, ymds, outside",
    [
        pytest.param(
            DailySequence(),
            [(1983, 4, 28), (1983, 4, 29), (1983, 4, 30), (1983, 5, 1), (1983, 5, 2)],
            None,
            id="daily-simple",
        ),
        pytest.param(
            DailySequence(),
            [
                (2001, 12, 29),
                (2001, 12, 30),
                (2001, 12, 31),
                (2002, 1, 1),
                (2002, 1, 2),
            ],
            None,
            id="daily-crossyear",
        ),
        pytest.param(
            DailySequence(),
            [(2003, 2, 26), (2003, 2, 27), (2003, 2, 28), (2003, 3, 1), (2003, 3, 2)],
            None,
            id="daily-feb28-nonleap",
        ),
        pytest.param(
            DailySequence(),
            [(2016, 2, 27), (2016, 2, 28), (2016, 2, 29), (2016, 3, 1), (2016, 3, 2)],
            None,
            id="daily-feb28-leap",
        ),
        pytest.param(
            DailySequence(excludes=[1]),
            [(1995, 4, 28), (1995, 4, 29), (1995, 4, 30), (1995, 5, 2), (1995, 5, 3)],
            (1995, 5, 1),
            id="daily-exclude",
        ),
        pytest.param(
            DailySequence(excludes=[29]),
            [(2000, 2, 26), (2000, 2, 27), (2000, 2, 28), (2000, 3, 1), (2000, 3, 2)],
            (2000, 2, 29),
            id="daily-exclude-leap",
        ),
        pytest.param(
            DailySequence(excludes=range(1, 29)),
            [(2020, 1, 30), (2020, 1, 31), (2020, 2, 29), (2020, 3, 29), (2020, 3, 30)],
            (2020, 2, 20),
            id="daily-exclude-almostall",
        ),
        pytest.param(
            WeeklySequence(2),
            [(1999, 3, 24), (1999, 3, 31), (1999, 4, 7), (1999, 4, 14), (1999, 4, 21)],
            (1999, 4, 20),
            id="weekly-simple",
        ),
        pytest.param(
            WeeklySequence(FRIDAY),
            [
                (2011, 12, 23),
                (2011, 12, 30),
                (2012, 1, 6),
                (2012, 1, 13),
                (2012, 1, 20),
            ],
            (2012, 1, 2),
            id="weekly-crossyear",
        ),
        pytest.param(
            WeeklySequence([2, 5]),
            [(2007, 2, 24), (2007, 2, 28), (2007, 3, 3), (2007, 3, 7), (2007, 3, 10)],
            (2007, 2, 25),
            id="weekly-feb28-nonleap",
        ),
        pytest.param(
            WeeklySequence([MONDAY, THURSDAY]),
            [(2024, 2, 22), (2024, 2, 26), (2024, 2, 29), (2024, 3, 4), (2024, 3, 7)],
            (2024, 2, 28),
            id="weekly-feb28-leap",
        ),
        pytest.param(
            MonthlySequence(15),
            [(1989, 3, 15), (1989, 4, 15), (1989, 5, 15), (1989, 6, 15), (1989, 7, 15)],
            (1989, 5, 19),
            id="monthly-simple",
        ),
        pytest.param(
            MonthlySequence([7, 21]),
            [
                (2014, 11, 21),
                (2014, 12, 7),
                (2014, 12, 21),
                (2015, 1, 7),
                (2015, 1, 21),
            ],
            (2014, 12, 31),
            id="monthly-crossyear",
        ),
        pytest.param(
            MonthlySequence(range(1, 32, 7)),
            [(2009, 2, 15), (2009, 2, 22), (2009, 3, 1), (2009, 3, 8), (2009, 3, 15)],
            (2009, 3, 14),
            id="monthly-feb28-nonleap",
        ),
        pytest.param(
            MonthlySequence([28, 29]),
            [(1992, 1, 29), (1992, 2, 28), (1992, 2, 29), (1992, 3, 28), (1992, 3, 29)],
            (1992, 2, 18),
            id="monthly-feb28-leap",
        ),
        pytest.param(
            MonthlySequence([11, 22], excludes=[(11, 11)]),
            [
                (1987, 10, 11),
                (1987, 10, 22),
                (1987, 11, 22),
                (1987, 12, 11),
                (1987, 12, 22),
            ],
            (1987, 11, 11),
            id="monthly-exclude",
        ),
        pytest.param(
            MonthlySequence([27, 29, 31], excludes=[(2, 29)]),
            [(2008, 1, 31), (2008, 2, 27), (2008, 3, 27), (2008, 3, 29), (2008, 3, 31)],
            (2008, 2, 29),
            id="monthly-exclude-leap",
        ),
        pytest.param(
            MonthlySequence(31, excludes=[(i, 31) for i in range(1, 10)]),
            [
                (2021, 10, 31),
                (2021, 12, 31),
                (2022, 10, 31),
                (2022, 12, 31),
                (2023, 10, 31),
            ],
            (2022, 5, 9),
            id="monthly-exclude-almostall",
        ),
        pytest.param(
            YearlySequence((1, 1)),
            [(1999, 1, 1), (2000, 1, 1), (2001, 1, 1), (2002, 1, 1), (2003, 1, 1)],
            (2002, 2, 2),
            id="yearly-simple",
        ),
        pytest.param(
            YearlySequence([(1, 1), (4, 2), (7, 2), (10, 1)]),
            [
                (2017, 7, 2),
                (2017, 10, 1),
                (2018, 1, 1),
                (2018, 4, 2),
                (2018, 7, 2),
            ],
            (2018, 6, 18),
            id="yearly-crossyear",
        ),
        pytest.param(
            YearlySequence([(2, 28), (2, 29), (3, 1)]),
            [(1994, 2, 28), (1994, 3, 1), (1995, 2, 28), (1995, 3, 1), (1996, 2, 28)],
            (1995, 2, 22),
            id="yearly-feb28-nonleap",
        ),
        pytest.param(
            YearlySequence([(i, 29) for i in range(1, 13)]),
            [(2008, 1, 29), (2008, 2, 29), (2008, 3, 29), (2008, 4, 29), (2008, 5, 29)],
            (2008, 2, 28),
            id="yearly-feb28-leap",
        ),
        pytest.param(
            YearlySequence((2, 29)),
            [(2000, 2, 29), (2004, 2, 29), (2008, 2, 29), (2012, 2, 29), (2016, 2, 29)],
            (2003, 2, 28),
            id="yearly-leaponly",
        ),
        pytest.param(
            YearlySequence([(7, 13)], excludes=[date(2023, 7, 13)]),
            [(2020, 7, 13), (2021, 7, 13), (2022, 7, 13), (2024, 7, 13), (2025, 7, 13)],
            (2023, 7, 13),
            id="yearly-exclude",
        ),
        pytest.param(
            YearlySequence([(1, 31), (2, 28), (2, 29)], excludes=ExcludeLeapFeb28()),
            [(2007, 1, 31), (2007, 2, 28), (2008, 1, 31), (2008, 2, 29), (2009, 1, 31)],
            (2008, 3, 10),
            id="yearly-exclude-leap",
        ),
        pytest.param(
            YearlySequence([(3, 31)], excludes=ExcludeNonTenYears()),  # FIXME
            [(1990, 3, 31), (2000, 3, 31), (2010, 3, 31), (2020, 3, 31), (2030, 3, 31)],
            (2001, 3, 31),
            id="yearly-exclude-almostall",
        ),
    ],
)
def test_sequence(
    seq: Sequence,
    ymds: List[Tuple[int, int, int]],
    outside: Optional[Tuple[int, int, int]],
):
    dates = [date(y, m, d) for y, m, d in ymds]
    if outside is not None:
        outside = date(*outside)

    for d in dates:
        assert d in seq

    for i in range(1, len(dates) - 1):
        prev = dates[i - 1]
        cur = dates[i]
        next = dates[i + 1]

        assert seq.next(cur) == next
        assert seq.next(cur, False) == cur
        assert seq.previous(cur) == prev
        assert seq.previous(cur, False) == cur

    assert list(seq.range(dates[0], dates[-1])) == dates
    assert list(seq.range(dates[0], dates[-1], include_start=False)) == dates[1:]
    assert (
        list(seq.range(dates[0], dates[-1], include_start=False, include_end=False))
        == dates[1:-1]
    )
    assert list(seq.range(dates[0], dates[-1], include_end=False)) == dates[:-1]

    assert list(seq.bracket(dates[2])) == [dates[1], dates[3]]
    assert list(seq.bracket(dates[2], 2)) == [dates[0], dates[1], dates[3], dates[4]]
    assert list(seq.bracket(dates[2], (1, 2))) == [dates[1], dates[3], dates[4]]
    assert list(seq.bracket(dates[2], 1, strict=False)) == dates[1:4]
    assert list(seq.bracket(dates[2], (2, 1), strict=False)) == dates[:4]

    if outside is not None:
        out_i = bisect.bisect_left(dates, outside)
        before = out_i
        after = len(dates) - out_i

        assert outside not in seq
        assert seq.next(outside) == dates[out_i]
        assert seq.previous(outside) == dates[out_i - 1]

        assert list(seq.range(outside, dates[-1])) == dates[out_i:]
        assert list(seq.range(outside, dates[-1], include_start=False)) == dates[out_i:]
        assert list(seq.range(dates[0], outside)) == dates[:out_i]
        assert list(seq.range(dates[0], outside, include_end=False)) == dates[:out_i]

        assert list(seq.bracket(outside)) == [dates[out_i - 1], dates[out_i]]
        assert list(seq.bracket(outside, (before, after))) == dates
        assert (
            list(seq.bracket(outside, (min(2, before), after)))
            == dates[max(0, out_i - 2) :]
        )
        assert (
            list(seq.bracket(outside, (before, min(2, after))))
            == dates[: min(len(dates), out_i + 2)]
        )
