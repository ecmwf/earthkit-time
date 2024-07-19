import bisect
import calendar
import os
from datetime import date
from typing import List, Optional, Tuple, Type

import pytest
import yaml

from earthkit.time.calendar import (
    FRIDAY,
    MONDAY,
    SATURDAY,
    SUNDAY,
    THURSDAY,
    WEDNESDAY,
    month_length,
)
from earthkit.time.sequence import (
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
            [],
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
            [],
            id="daily-crossyear",
        ),
        pytest.param(
            DailySequence(),
            [(2003, 2, 26), (2003, 2, 27), (2003, 2, 28), (2003, 3, 1), (2003, 3, 2)],
            [],
            id="daily-feb28-nonleap",
        ),
        pytest.param(
            DailySequence(),
            [(2016, 2, 27), (2016, 2, 28), (2016, 2, 29), (2016, 3, 1), (2016, 3, 2)],
            [],
            id="daily-feb28-leap",
        ),
        pytest.param(
            DailySequence(excludes=[1]),
            [(1995, 4, 28), (1995, 4, 29), (1995, 4, 30), (1995, 5, 2), (1995, 5, 3)],
            [(1995, 5, 1)],
            id="daily-exclude",
        ),
        pytest.param(
            DailySequence(excludes=[29]),
            [(2000, 2, 26), (2000, 2, 27), (2000, 2, 28), (2000, 3, 1), (2000, 3, 2)],
            [(2000, 2, 29)],
            id="daily-exclude-leap",
        ),
        pytest.param(
            DailySequence(excludes=range(1, 29)),
            [(2020, 1, 30), (2020, 1, 31), (2020, 2, 29), (2020, 3, 29), (2020, 3, 30)],
            [(2020, 2, 20)],
            id="daily-exclude-almostall",
        ),
        pytest.param(
            WeeklySequence(2),
            [(1999, 3, 24), (1999, 3, 31), (1999, 4, 7), (1999, 4, 14), (1999, 4, 21)],
            [(1999, 4, 20)],
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
            [(2012, 1, 2)],
            id="weekly-crossyear",
        ),
        pytest.param(
            WeeklySequence([2, 5]),
            [(2007, 2, 24), (2007, 2, 28), (2007, 3, 3), (2007, 3, 7), (2007, 3, 10)],
            [(2007, 2, 25), (2007, 3, 5)],
            id="weekly-feb28-nonleap",
        ),
        pytest.param(
            WeeklySequence([MONDAY, THURSDAY]),
            [(2024, 2, 22), (2024, 2, 26), (2024, 2, 29), (2024, 3, 4), (2024, 3, 7)],
            [(2024, 2, 28), (2024, 3, 2)],
            id="weekly-feb28-leap",
        ),
        pytest.param(
            MonthlySequence(15),
            [(1989, 3, 15), (1989, 4, 15), (1989, 5, 15), (1989, 6, 15), (1989, 7, 15)],
            [(1989, 4, 30), (1989, 5, 19)],
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
            [(2014, 12, 14), (2014, 12, 31)],
            id="monthly-crossyear",
        ),
        pytest.param(
            MonthlySequence(range(1, 32, 7)),
            [(2009, 2, 15), (2009, 2, 22), (2009, 3, 1), (2009, 3, 8), (2009, 3, 15)],
            [(2009, 3, 14)],
            id="monthly-feb28-nonleap",
        ),
        pytest.param(
            MonthlySequence([28, 29]),
            [(1992, 1, 29), (1992, 2, 28), (1992, 2, 29), (1992, 3, 28), (1992, 3, 29)],
            [(1992, 2, 18), (1992, 3, 14)],
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
            [(1987, 11, 11)],
            id="monthly-exclude",
        ),
        pytest.param(
            MonthlySequence([27, 29, 31], excludes=[(2, 29)]),
            [(2008, 1, 31), (2008, 2, 27), (2008, 3, 27), (2008, 3, 29), (2008, 3, 31)],
            [(2008, 2, 29), (2008, 3, 28)],
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
            [(2022, 5, 9), (2022, 6, 1)],
            id="monthly-exclude-almostall",
        ),
        pytest.param(
            YearlySequence((1, 1)),
            [(1999, 1, 1), (2000, 1, 1), (2001, 1, 1), (2002, 1, 1), (2003, 1, 1)],
            [(2000, 7, 2), (2002, 2, 2)],
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
            [(2017, 11, 16), (2018, 6, 18)],
            id="yearly-crossyear",
        ),
        pytest.param(
            YearlySequence([(2, 28), (2, 29), (3, 1)]),
            [(1994, 2, 28), (1994, 3, 1), (1995, 2, 28), (1995, 3, 1), (1996, 2, 28)],
            [(1994, 8, 30), (1995, 2, 22)],
            id="yearly-feb28-nonleap",
        ),
        pytest.param(
            YearlySequence([(i, 29) for i in range(1, 13)]),
            [(2008, 1, 29), (2008, 2, 29), (2008, 3, 29), (2008, 4, 29), (2008, 5, 29)],
            [(2008, 2, 28), (2008, 5, 14)],
            id="yearly-feb28-leap",
        ),
        pytest.param(
            YearlySequence((2, 29)),
            [(2000, 2, 29), (2004, 2, 29), (2008, 2, 29), (2012, 2, 29), (2016, 2, 29)],
            [(2003, 2, 28)],
            id="yearly-leaponly",
        ),
        pytest.param(
            YearlySequence([(7, 13)], excludes=[date(2023, 7, 13)]),
            [(2020, 7, 13), (2021, 7, 13), (2022, 7, 13), (2024, 7, 13), (2025, 7, 13)],
            [(2023, 7, 13)],
            id="yearly-exclude",
        ),
        pytest.param(
            YearlySequence([(1, 31), (2, 28), (2, 29)], excludes=ExcludeLeapFeb28()),
            [(2007, 1, 31), (2007, 2, 28), (2008, 1, 31), (2008, 2, 29), (2009, 1, 31)],
            [(2007, 2, 14), (2008, 3, 10)],
            id="yearly-exclude-leap",
        ),
        pytest.param(
            YearlySequence([(3, 31)], excludes=ExcludeNonTenYears()),  # FIXME
            [(1990, 3, 31), (2000, 3, 31), (2010, 3, 31), (2020, 3, 31), (2030, 3, 31)],
            [(2001, 3, 31), (2005, 3, 31)],
            id="yearly-exclude-almostall",
        ),
    ],
)
def test_sequence(
    seq: Sequence,
    ymds: List[Tuple[int, int, int]],
    outside: List[Tuple[int, int, int]],
):
    dates = [date(y, m, d) for y, m, d in ymds]

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
        assert seq.nearest(cur) == cur
        assert seq.nearest(cur, resolve="previous") == cur
        assert seq.nearest(cur, resolve="next") == cur

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

    for out_tup in outside:
        out_date = date(*out_tup)
        out_i = bisect.bisect_left(dates, out_date)
        before = out_i
        after = len(dates) - out_i

        assert out_date not in seq
        assert seq.next(out_date) == dates[out_i]
        assert seq.previous(out_date) == dates[out_i - 1]

        db = (out_date - dates[out_i - 1]).days
        da = (dates[out_i] - out_date).days
        if db != da:
            exp_nearest = dates[out_i - 1] if db < da else dates[out_i]
            assert seq.nearest(out_date) == exp_nearest
        else:
            assert seq.nearest(out_date) == dates[out_i - 1]
            assert seq.nearest(out_date, resolve="previous") == dates[out_i - 1]
            assert seq.nearest(out_date, resolve="next") == dates[out_i]

        assert list(seq.range(out_date, dates[-1])) == dates[out_i:]
        assert (
            list(seq.range(out_date, dates[-1], include_start=False)) == dates[out_i:]
        )
        assert list(seq.range(dates[0], out_date)) == dates[:out_i]
        assert list(seq.range(dates[0], out_date, include_end=False)) == dates[:out_i]

        assert list(seq.bracket(out_date)) == [dates[out_i - 1], dates[out_i]]
        assert list(seq.bracket(out_date, (before, after))) == dates
        assert (
            list(seq.bracket(out_date, (min(2, before), after)))
            == dates[max(0, out_i - 2) :]
        )
        assert (
            list(seq.bracket(out_date, (before, min(2, after))))
            == dates[: min(len(dates), out_i + 2)]
        )


@pytest.mark.parametrize(
    "seq_dict, expect_type, expect_days, expect_excludes",
    [
        pytest.param({"type": "daily"}, DailySequence, None, set(), id="daily"),
        pytest.param(
            {"type": "daily", "excludes": [2, 4, 6]},
            DailySequence,
            None,
            {2, 4, 6},
            id="daily-excludes",
        ),
        pytest.param(
            {"type": "weekly", "days": 2},
            WeeklySequence,
            [WEDNESDAY],
            None,
            id="weekly",
        ),
        pytest.param(
            {"type": "weekly", "days": "Th"},
            WeeklySequence,
            [THURSDAY],
            None,
            id="weekly-str",
        ),
        pytest.param(
            {"type": "weekly", "days": [4, 6]},
            WeeklySequence,
            [FRIDAY, SUNDAY],
            None,
            id="weekly-intlist",
        ),
        pytest.param(
            {"type": "weekly", "days": ["mon", "sat"]},
            WeeklySequence,
            [MONDAY, SATURDAY],
            None,
            id="weekly-strlist",
        ),
        pytest.param(
            {"type": "monthly", "days": 13}, MonthlySequence, [13], set(), id="monthly"
        ),
        pytest.param(
            {"type": "monthly", "days": [7, 21]},
            MonthlySequence,
            [7, 21],
            set(),
            id="monthly-list",
        ),
        pytest.param(
            {"type": "monthly", "days": [4, 8, 12, 29], "excludes": [[2, 29]]},
            MonthlySequence,
            [4, 8, 12, 29],
            {(2, 29)},
            id="monthly-list-exclude",
        ),
        pytest.param(
            {"type": "monthly", "days": [4, 8, 12, 29], "excludes": ["0229", "0312"]},
            MonthlySequence,
            [4, 8, 12, 29],
            {(2, 29), (3, 12)},
            id="monthly-list-strexclude",
        ),
        pytest.param(
            {"type": "yearly", "days": [3, 14]},
            YearlySequence,
            [(3, 14)],
            set(),
            id="yearly",
        ),
        pytest.param(
            {"type": "yearly", "days": "1203"},
            YearlySequence,
            [(12, 3)],
            set(),
            id="yearly-str",
        ),
        pytest.param(
            {"type": "yearly", "days": [[5, 22], [8, 24]]},
            YearlySequence,
            [(5, 22), (8, 24)],
            set(),
            id="yearly-mdlist",
        ),
        pytest.param(
            {"type": "yearly", "days": ["1001", "1111"]},
            YearlySequence,
            [(10, 1), (11, 11)],
            set(),
            id="yearly-strlist",
        ),
        pytest.param(
            {
                "type": "yearly",
                "days": ["0311", "0722", "1224"],
                "excludes": [[2000, 12, 24]],
            },
            YearlySequence,
            [(3, 11), (7, 22), (12, 24)],
            {date(2000, 12, 24)},
            id="yearly-strlist-exclude",
        ),
        pytest.param(
            {
                "type": "yearly",
                "days": ["0311", "0722", "1224"],
                "excludes": ["20110311", "20070722"],
            },
            YearlySequence,
            [(3, 11), (7, 22), (12, 24)],
            {date(2011, 3, 11), date(2007, 7, 22)},
            id="yearly-strlist-strexclude",
        ),
    ],
)
def test_create_sequence(
    seq_dict: dict,
    expect_type: Type[Sequence],
    expect_days: Optional[list],
    expect_excludes: Optional[set],
):
    seq = Sequence.from_dict(seq_dict)
    assert type(seq) is expect_type
    if expect_days is not None:
        assert seq.days == expect_days
    if expect_excludes is not None:
        assert seq.excludes == expect_excludes


@pytest.mark.parametrize(
    "seq_dict, expect_msg",
    [
        pytest.param({}, "^Sequence dictionary must contain `type` key$", id="notype"),
        pytest.param(
            {"type": "sesquiannual"}, "^Unknown type 'sesquiannual'$", id="unknowntype"
        ),
        pytest.param(
            {"type": "weekly"},
            "^Weekly sequence must provide `days`$",
            id="weekly-nodays",
        ),
        pytest.param(
            {"type": "monthly"},
            "^Monthly sequence must provide `days`$",
            id="monthly-nodays",
        ),
        pytest.param(
            {"type": "yearly"},
            "^Yearly sequence must provide `days`$",
            id="yearly-nodays",
        ),
    ],
)
def test_create_sequence_invalid(seq_dict: dict, expect_msg: str):
    with pytest.raises(ValueError, match=expect_msg):
        Sequence.from_dict(seq_dict)


def test_sequence_from_resource(
    monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory
):
    seq = Sequence.from_resource("ecmwf-mon-thu")
    assert type(seq) is WeeklySequence
    assert seq.days == [MONDAY, THURSDAY]

    with pytest.raises(FileNotFoundError):
        Sequence.from_resource("invalid-sequence")

    seq_path1 = tmp_path_factory.mktemp("seqs1")
    (seq_path1 / "wednesdays.yaml").write_text(
        yaml.safe_dump({"type": "weekly", "days": ["Wednesday"]})
    )
    (seq_path1 / "foo.yaml").write_text(
        yaml.safe_dump({"type": "monthly", "days": [2, 4, 6, 8]})
    )

    seq_path2 = tmp_path_factory.mktemp("seqs2")
    (seq_path2 / "foo.yaml").write_text(yaml.safe_dump({"type": "daily"}))
    (seq_path2 / "ecmwf-4days.yaml").write_text(
        yaml.safe_dump(
            {
                "type": "yearly",
                "days": [
                    (m, d)
                    for m in range(1, 13)
                    for d in range(1, month_length(1999, m) + 1, 4)
                ],
            }
        )
    )

    envname = "EARTHKIT_TIME_SEQ_PATH"
    monkeypatch.setenv(envname, os.pathsep.join([str(seq_path1), str(seq_path2)]))

    print(os.getenv(envname))

    seq = Sequence.from_resource("wednesdays")
    assert type(seq) is WeeklySequence
    assert seq.days == [WEDNESDAY]

    seq = Sequence.from_resource("foo")
    assert type(seq) is MonthlySequence
    assert seq.days == [2, 4, 6, 8]

    seq = Sequence.from_resource("ecmwf-4days")
    assert type(seq) is YearlySequence
