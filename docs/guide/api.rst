Python API
==========

Manipulating sequences of dates
-------------------------------

Sequences of dates are represented by the
:class:`~earthkit.time.sequence.Sequence` class. Specific types of sequence are
defined as subclasses:

* :class:`~earthkit.time.sequence.DailySequence` for daily repeats
* :class:`~earthkit.time.sequence.WeeklySequence` for repeats on specific days each week
* :class:`~earthkit.time.sequence.MonthlySequence` for repeats on specific days each month
* :class:`~earthkit.time.sequence.YearlySequence` for repeats on specific days each year

A sequence object can be created by invoking the corresponding constructor:

.. code-block:: python

   from earthkit.time import WeeklySequence
   from earthkit.time.calendar import MONDAY, WEDNESDAY
   seq = WeeklySequence([MONDAY, WEDNESDAY])

It can also be loaded from a dictionary using
:meth:`Sequence.from_dict <earthkit.time.sequence.Sequence.from_dict>`, or from
a preset file using
:meth:`Sequence.from_resource <earthkit.time.sequence.Sequence.from_resource>`.

For convenience, calling the :func:`~earthkit.time.sequence.create_sequence`
function will dispatch to the appropriate constructor or factory method.


Sequence examples
~~~~~~~~~~~~~~~~~

===========================================================  =============================================================================================
Example                                                      Description
===========================================================  =============================================================================================
``DailySequence()``                                          Sequence recurring every day
``DailySequence(excludes=[31])``                             Sequence recurring every day, except the 31\ :sup:`st`
``WeeklySequence([MONDAY, THURSDAY])``                       Sequence recurring every Monday and Thursday
``MonthlySequence([1, 15])``                                 Sequence recurring every 1\ :sup:`st` and 15\ :sup:`th` of the month
``MonthlySequence([1, 8, 15, 22, 29], excludes=[(2, 29)])``  Sequence recurring every 7 days each month, skipping the 29\ :sup:`th` February
``YearlySequence((12, 25))``                                 Sequence recurring every year on the 25\ :sup:`th` December
``Sequence.from_resource("ecmwf-4days")``                    Pre-defined sequence (equivalent to ``MonthlySequence(range(1, 30, 4), excludes=[(2, 29)])``)
``create_sequence("daily")``                                 Equivalent to ``DailySequence()``
``create_sequence("resource", "ecmwf-2days")``               Equivalent to ``Sequence.from_resource("ecmwf-2days")``
===========================================================  =============================================================================================


Computing individual dates
~~~~~~~~~~~~~~~~~~~~~~~~~~

To get the previous or next date in a sequence, use
:meth:`Sequence.previous <earthkit.time.sequence.Sequence.previous>`
or :meth:`Sequence.next <earthkit.time.sequence.Sequence.next>`:

.. code-block:: pycon

    >>> seq = WeeklySequence([WEDNESDAY, FRIDAY])
    >>> seq.previous(date(2024, 5, 12))
    datetime.date(2024, 5, 10)
    >>> seq.next(date(2024, 5, 10))
    datetime.date(2024, 5, 15)
    >>> seq.next(date(2024, 5, 10), strict=False)
    datetime.date(2024, 5, 10)

If the given date is in the sequence, the default behaviour is to skip to the
previous or next one. To keep it, pass ``strict=False``.

Similarly, the sequence date closest to a given date can be computed using
:meth:`Sequence.nearest <earthkit.time.sequence.Sequence.nearest>`:

.. code-block:: pycon

    >>> seq = MonthlySequence([1, 15])
    >>> seq.nearest(date(2024, 7, 4))
    datetime.date(2024, 7, 1)
    >>> seq.nearest(date(2024, 3, 20))
    datetime.date(2024, 3, 15)
    >>> seq.nearest(date(2024, 8, 8))
    datetime.date(2024, 8, 1)
    >>> seq.nearest(date(2024, 8, 8), resolve="next")
    datetime.date(2024, 8, 15)

If there is a tie, meaning that the given date is equidistant from the previous
and next date in the sequence, the previous date is returned. This behaviour can
be explicitly controlled by passing ``resolve="previous"`` or
``resolve="next"``.


Computing sets of dates
~~~~~~~~~~~~~~~~~~~~~~~

To find all the sequence dates falling within a range, use
:meth:`Sequence.range <earthkit.time.sequence.Sequence.range>`:


.. code-block:: pycon

   >>> print_dates = lambda dates: print(", ".join(d.strftime("%Y%m%d") for d in dates))
   >>> seq = WeeklySequence([0, 2, 4])
   >>> print_dates(seq.range(date(2024, 12, 1), date(2024, 12, 16)))
   20241202, 20241204, 20241206, 20241209, 20241211, 20241213, 20241216
   >>> print_dates(seq.range(date(2024, 12, 1), date(2024, 12, 16), include_end=False))
   20241202, 20241204, 20241206, 20241209, 20241211, 20241213
   >>> print_dates(seq.range(date(2024, 12, 2), date(2024, 12, 16), include_start=False))
   20241204, 20241206, 20241209, 20241211, 20241213, 20241216

By default, ranges include the given start and end dates. The ``include_start``
and ``include_end`` arguments control this behaviour.

To get a given number of dates around one reference, use
:meth:`Sequence.bracket <earthkit.time.sequence.Sequence.bracket>`:


.. code-block:: pycon

   >>> seq = WeeklySequence(SATURDAY)
   >>> print_dates(seq.bracket(date(1999, 11, 27)))
   19991120, 19991204
   >>> print_dates(seq.bracket(date(1999, 11, 27), strict=False))
   19991120, 19991127, 19991204
   >>> print_dates(seq.bracket(date(2006, 5, 28), 3))
   20060513, 20060520, 20060527, 20060603, 20060610, 20060617
   >>> print_dates(seq.bracket(date(2015, 4, 3), (1, 2)))
   20150328, 20150404, 20150411
   >>> print_dates(seq.bracket(date(1993, 7, 17), (2, 1), strict=False))
   19930703, 19930710, 19930717, 19930724

The optional ``num`` argument represents the number of dates to output,
respectively before and after the reference date. If an integer is given, the
same number of dates either side is returned. If ``strict=False`` is passed and
the reference date is in the sequence, it is printed as well (but not counted
towards the numbers requested).


Sets of dates for model climates
--------------------------------

To get one date per year on the same day as a given reference, use
:meth:`~earthkit.time.climatology.date_range`:

.. code-block:: pycon

   >>> from earthkit.time import date_range
   >>> print_dates(date_range(date(2006, 10, 23), 2000, 2005))
   20001023, 20011023, 20021023, 20031023, 20041023, 20051023
   >>> print_dates(date_range(date(2005, 6, 2), date(2002, 6, 8), date(2004, 7, 1)))
   20030602, 20040602
   >>> from earthkit.time import RelativeYear
   >>> print_dates(date_range(date(2010, 8, 5), RelativeYear(-3), RelativeYear(-1)))
   20070805, 20080805, 20090805

To combine yearly dates with multiple reference dates taken from a sequence, use
:meth:`~earthkit.time.climatology.model_climate_dates`:

.. code-block:: pycon

   >>> from earthkit.time import model_climate_dates
   >>> seq = Sequence.from_resource("ecmwf-mon-thu")
   >>> print_dates(model_climate_dates(date(2023, 8, 6), 2018, 2020, 7, 7, seq))
   20180731, 20180803, 20180807, 20180810, 20190731, 20190803, 20190807, 20190810, 20200731, 20200803, 20200807, 20200810
   >>> print_dates(model_climate_dates(date(2023, 1, 1), RelativeYear(-7), RelativeYear(-4), 5, 5, seq))
   20151229, 20160102, 20160105, 20161229, 20170102, 20170105, 20171229, 20180102, 20180105, 20181229, 20190102, 20190105


Manipulating time steps and ranges
----------------------------------

A step range is represented as a ``start-end`` string, or a ``(start, end)``
tuple. The :func:`~earthkit.time.timesteps.parse_range` function converts the
string representation to a tuple of integers.


Simple manipulations
~~~~~~~~~~~~~~~~~~~~

Regularly-spaced step ranges of the same width repeating at a given interval can
be created with :func:`~earthkit.time.timesteps.regular_ranges`:

.. code-block:: pycon

   >>> from earthkit.time import regular_ranges
   >>> list(regular_ranges(24, 48, 12, 6))
   [(24, 36), (30, 42), (36, 48)]

To expand a step range into its steps, given an interval, use
:func:`~earthkit.time.timesteps.expand_range`:

.. code-block:: pycon

   >>> from earthkit.time import expand_range
   >>> list(expand_range("0-24", 6))
   [0, 6, 12, 18, 24]


The :func:`~earthkit.time.timesteps.hours_from_delta` function converts
:class:`~datetime.timedelta` objects to time step numbers in hours:

.. code-block:: pycon

   >>> from datetime import timedelta
   >>> from earthkit.time import hours_from_delta
   >>> hours_from_delta(timedelta(days=2))
   48


Daily ranges
~~~~~~~~~~~~

Conversion between day numbers and the corresponding step ranges can be done
with :func:`~earthkit.time.timesteps.range_from_day` and
:func:`~earthkit.time.timesteps.day_from_range`. Both functions take a forecast
base time (which can be a datetime or a time) and the starting time of the first
day.

.. code-block:: pycon

   >>> from datetime import time
   >>> from earthkit.time import range_from_day, day_from_range
   >>> range_from_day(1)
   (0, 24)
   >>> range_from_day(2, 12)
   (36, 60)
   >>> range_from_day(1, time(6), time(12))
   (6, 30)
   >>> day_from_range((24, 48))
   2
   >>> day_from_range((6, 30), time(6), time(12))
   1


Weekly ranges
~~~~~~~~~~~~~

Conversion between week numbers and the corresponding step ranges can be done
with :func:`~earthkit.time.timesteps.range_from_week` and
:func:`~earthkit.time.timesteps.week_from_range`. Both functions take a forecast
base time (which can be a date, a datetime, a time, a weeek day, or a (week day,
time) tuple) and a starting day of the week. The first week starts on the first
full day matching the given starting day (or the first full day if not given),
at 00:00.

.. code-block:: pycon

   >>> from datetime import date, datetime, time
   >>> from earthkit.time.calendar import MONDAY, SUNDAY, THURSDAY
   >>> from earthkit.time import range_from_week, week_from_range
   >>> range_from_week(1)
   (0, 168)
   >>> range_from_week(2, time(12))
   (180, 348)
   >>> range_from_week(1, THURSDAY, MONDAY)
   (96, 264)
   >>> range_from_week(1, (THURSDAY, time(12)), MONDAY)
   (84, 252)
   >>> range_from_week(3, date(2023, 11, 10), SUNDAY)  # 2023-11-10 is a Friday
   (384, 552)
   >>> range_from_week(3, datetime(2023, 11, 10, 6), SUNDAY)
   (378, 546)
   >>> week_from_range((336, 504))
   3
   >>> week_from_range((96, 264), THURSDAY, MONDAY)
   1


Monthly dates and ranges
~~~~~~~~~~~~~~~~~~~~~~~~

Monthly date computations can be done with
:func:`~earthkit.time.timesteps.startdate_from_month` and
:func:`~earthkit.time.timesteps.month_from_startdate`. Both functions take a
forecast base date (which can be a date, or a ``(year, month)`` tuple).
:func:`~earthkit.time.timesteps.startdate_from_month` optionally takes a start
day for the month (in the reverse case, the start day is inferred from the
date).

.. code-block:: pycon

   >>> from datetime import date
   >>> from earthkit.time import startdate_from_month, month_from_startdate
   >>> startdate_from_month(1, (2026, 1))
   date(2026, 1, 1)
   >>> startdate_from_month(3, date(2024, 1, 15))
   date(2024, 4, 1)
   >>> startdate_from_month(5, date(2022, 1, 1), 15)
   date(2022, 5, 15)
   >>> startdate_from_month(6, date(2021, 8, 1))
   date(2022, 1, 1)
   >>> month_from_startdate((2026, 1), (2026, 1))
   1
   >>> month_from_startdate(date(2024, 1, 1), (2024, 3))
   3
   >>> month_from_startdate(date(2020, 1, 15), date(2020, 8, 1))
   7
   >>> month_from_startdate(date(2019, 1, 15), date(2019, 8, 15))
   8
   >>> month_from_startdate(date(2018, 1, 1), date(2018, 9, 15))
   9
   >>> month_from_startdate((2017, 4), date(2018, 1, 1))
   10

Conversion between month numbers and the corresponding step ranges can be done
with :func:`~earthkit.time.timesteps.range_from_month` and
:func:`~earthkit.time.timesteps.month_from_range`. Both functions take a
forecast base date (which can be a date, or a ``(year, month)`` tuple) and a
starting day of the month.

.. code-block:: pycon

   >>> from datetime import date
   >>> from earthkit.time import range_from_month, month_from_range
   >>> range_from_month(1, (2026, 1))
   (0, 744)
   >>> range_from_month(2, date(2025, 1, 1))
   (744, 1416)
   >>> range_from_month(4, date(2023, 1, 15))
   (2544, 3288)
   >>> range_from_month(5, date(2022, 1, 15), 15)
   (2880, 3624)
   >>> month_from_range((744, 1416), (2025, 1))
   2
   >>> month_from_range((2544, 3288), date(2023, 1, 15))
   4
   >>> month_from_range((2880, 3624), date(2022, 1, 15), 15)
   5
