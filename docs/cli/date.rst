earthkit-date - Manipulate dates
================================

.. program:: earthkit-date

The :program:`earthkit-date` can be invoked with various actions documented
here, as follows::

   earthkit-date <action> [args...]

.. option:: -h, --help

   Print a help message and exit. Can be used as ``earthkit-date --help`` as well as
   for actions, e.g. ``earthkit-date shift --help``.


``shift`` - shift a date
------------------------

Shift a date by the given number of days::

   earthkit-date shift <date> <days>

.. option:: date

   Reference date

.. option:: days

   Number of days (can be negative)


``diff`` - subtract two dates
-----------------------------

Subtract date2 from date1, returning the number of days::

   earthkit-date diff <date1> <date2>

.. option:: date1

   First date (+)

.. option:: date2

   Second date (-)
