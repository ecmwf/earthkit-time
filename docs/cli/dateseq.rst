earthkit-dateseq - Manipulate sequences of dates
================================================

.. program:: earthkit-dateseq

The :program:`earthkit-dateseq` can be invoked with various actions documented
here, as follows::

   earthkit-dateseq <action> [args...]

.. option:: -h, --help

   Print a help message and exit. Can be used as ``earthkit-dateseq --help`` as
   well as for actions, e.g. ``earthkit-dateseq next --help``.


.. _cli_seq:

Specifying sequences
--------------------

Sequences can be described according to their type, using the corresponding argument.

.. option:: --daily

   Daily inputs

.. option:: --weekly <days>

   Weekly inputs on these days (slash-separated). Week days can be specified
   either by number (0 = Monday, 1 = Tuesday, etc) or by any unambiguous prefix
   of the name (case-insensitive, e.g. M, tue, Friday)

.. option:: --monthly <days>

   Monthly inputs on these days (slash-separated)

.. option:: --yearly <days>

   Yearly inputs on these days (MMDD, slash-separated)

.. option:: --preset <preset>

   Name of a preset sequence, or path to a valid YAML preset file. Sequence
   presets can be stored in the package as well as externally defined. If a
   preset name is given, the corresponding file will be searched in
   :envvar:`EARTHKIT_TIME_SEQ_PATH`, then in the package itself.

.. envvar:: EARTHKIT_TIME_SEQ_PATH

    Colon-separated list of paths where to look for sequence presets. Will take
    precedence over the ones provided by earthkit-time.

.. option:: --excludes <excludes>

   Exclude specific days from the sequence, as follows:

   * daily: exclude specific days of the month
   * monthly: exclude specific dates in the year (MMDD)
   * yearly: exclude specific dates (YYYYMMDD)


``previous``, ``next`` - Compute the previous and next date in the given sequence
---------------------------------------------------------------------------------

Usage::

   earthkit-dateseq previous <sequence> [--inclusive] <date>
   earthkit-dateseq next <sequence> [--inclusive] <date>

The sequence is described as documented in :ref:`cli_seq`.

.. option:: --inclusive

   If this flag is set and the given date is in the sequence, it is returned.

.. option:: date

   The date to use as a reference (YYYYMMDD)


``nearest`` - Compute the nearest date in the given sequence
------------------------------------------------------------

Usage::

   earthkit-dateseq nearest <sequence> [--resolve <resolve>] <date>

The sequence is described as documented in :ref:`cli_seq`.

.. option:: --resolve <resolve>

   Can be either ``previous`` or ``next``. If two consecutive dates in the
   sequence are equally close, use this one. By default, the previous date is
   used.

.. option:: date

   The date to use as a reference (YYYYMMDD)


``range`` - Compute the sequence dates that fall within a range
---------------------------------------------------------------

Usage::

   earthkit-dateseq range <sequence> [--sep <sep>] [--exclude-start] [--exclude-end] <from> <to>

The sequence is described as documented in :ref:`cli_seq`. The list is printed
using the given separator, as documented in :ref:`cli_sep`.

.. option:: --exclude-start

   If specified and the start date is in the sequence, do not print it.

.. option:: --exclude-end

   If specified and the end date is in the sequence, do not print it.

.. option:: from

   Start date

.. option:: to

   End date


``bracket`` - Compute the sequence dates around a date
------------------------------------------------------

Usage::

   earthkit-dateseq bracket <sequence> [--sep <sep>] [--inclusive] <date> <before> <after>

The sequence is described as documented in :ref:`cli_seq`. The list is printed
using the given separator, as documented in :ref:`cli_sep`.

.. option:: --inclusive

   If this flag is set and the given date is in the sequence, it is returned (not counted).

.. option:: date

   The date to use as a reference (YYYYMMDD)

.. option:: before

   Number of dates to print before the given date (default 1)

.. option:: after

   Number of dates to print after the given date (default: same number as before)


.. _cli_sep:

Formatting lists of dates
-------------------------

If the following option is not set, each date will be printed on a separate
line.

.. option:: --sep <sep>

   separators can be any string of characters, with some escape
   sequences evaluated:

   * ``\0``, ``\a``, ``\b``, ``\f``, ``\n``, ``\r``, ``\t``, ``\v``: NUL, BEL, BS, FF, LF, CR, TAB, VT
   * ``\xhh``: character with hex value ``hh``
   * ``\ooo``: character with octal value ``ooo``
   * ``\\``: literal ``\``
