earthkit-datetime - Manipulate datetimes
========================================

In this context, a datetime is defined as a ``YYYYMMDDHH`` string, and
differences are expressed in hours.

.. program:: earthkit-datetime

The :program:`earthkit-datetime` can be invoked with various actions documented
here, as follows::

   earthkit-datetime <action> [args...]

.. option:: -h, --help

   Print a help message and exit. Can be used as ``earthkit-datetime --help`` as
   well as for actions, e.g. ``earthkit-datetime shift --help``.


``shift`` - shift a datetime
----------------------------

Shift a datetime by the given number of hours::

   earthkit-datetime shift <datetime> <hours>

.. option:: datetime

   Reference datetime

.. option:: hours

   Number of hours (can be negative)


``diff`` - subtract two datetimes
---------------------------------

Subtract datetime2 from datetime1, returning the number of hours::

   earthkit-datetime diff <datetime1> <datetime2>

.. option:: datetime1

   First datetime (+)

.. option:: datetime2

   Second datetime (-)
