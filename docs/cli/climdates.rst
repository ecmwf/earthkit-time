earthkit-climdates - Compute model climate dates
================================================

.. program:: earthkit-climdates

The :program:`earthkit-climdates` can be invoked with various actions documented
here, as follows::

   earthkit-climdates <action> [args...]

.. option:: -h, --help

   Print a help message and exit. Can be used as ``earthkit-climdates --help``
   as well as for actions, e.g. ``earthkit-climdates range --help``.


.. _cli_mclim_range:

``range`` - Compute climatological date ranges
----------------------------------------------

Compute climatological date ranges, one day per year in a given range::

   earthkit-climdates range [--sep <sep>] (--from-date <start> | --from-year <start> | --from-rel-year <start>) (--to-date <end> | --to-year <end> | --to-rel-year <end>) <date>

The list is printed using the given separator, as documented in :ref:`cli_sep`.

.. option:: --from-date <start>

   Return dates starting from this one

.. option:: --from-year <start>

   Return dates starting from this year

.. option:: --from-rel-year <start>

   Return dates starting from this number after the year in :option:`date` (e.g.
   ``--from-rel-year -5`` will start 5 years earlier)

.. option:: --to-date <end>

   Return dates up to this one

.. option:: --to-year <end>

   Return dates up to this year

.. option:: --to-rel-year <end>

   Return dates up to this number after the year in :option:`date` (e.g.
   ``--to-rel-year -1`` will end in the year before)

.. option:: date

   The date to use as a reference (YYYYMMDD)


``mclim`` - Compute sets of dates for model climatologies
---------------------------------------------------------

This combines a climatological range (see :ref:`cli_mclim_range`) and a
recurring source (e.g. twice a week).

Usage::

   earthkit-climdates mclim <sequence> [--sep <sep>] (--from-date <start> | --from-year <start> | --from-rel-year <start>) (--to-date <end> | --to-year <end> | --to-rel-year <end>) --before <num> --after <num> <date>

The sequence is described as documented in :ref:`cli_seq`. The list is printed
using the given separator, as documented in :ref:`cli_sep`.

.. option:: --from-date <start>

   Return dates starting from this one

.. option:: --from-year <start>

   Return dates starting from this year

.. option:: --from-rel-year <start>

   Return dates starting from this number after the year of the current date
   (e.g.  ``--from-rel-year -5`` will start 5 years earlier)

.. option:: --to-date <end>

   Return dates up to this one

.. option:: --to-year <end>

   Return dates up to this year

.. option:: --before <num>

   Pick up all inputs starting from *num* days before the chosen date

.. option:: --after <num>

   Pick up all inputs up to *num* days after the chosen date

.. option:: --to-rel-year <end>

   Return dates up to this number after the year of the current date (e.g.
   ``--to-rel-year -1`` will end in the year before)

.. option:: date

   The date to use as a reference (YYYYMMDD)
