Command-line Interface
======================

For a detailed description of the command-line interface, see :ref:`cli_ref`.


Date arithmetic
---------------

The :program:`earthkit-date` command provides utilities to shift and subtract
dates. For instance, to get the date 13 days before a reference:

.. code-block:: console

   $ earthkit-date shift 20160219 -13
   20160206

Positive and negative shifts are supported. To do the reverse and compute how
many days there are between two dates:

.. code-block:: console

   $ earthkit-date diff 20241225 20240314
   286


Date sequences
--------------

The :program:`earthkit-dateseq` command provides various utilities to manipulate
sequences of recurring dates.


Specifying a sequence
~~~~~~~~~~~~~~~~~~~~~

=========================================  ===============================================================================
Example                                    Description
=========================================  ===============================================================================
``--daily``                                Sequence recurring every day
``--daily --exclude 31``                   Sequence recurring every day, except the 31\ :sup:`st`
``--weekly mon/thu``                       Sequence recurring every Monday and Thursday
``--monthly 1/15``                         Sequence recurring every 1\ :sup:`st` and 15\ :sup:`th` of the month
``--monthly 1/8/15/22/29 --exclude 0229``  Sequence recurring every 7 days each month, skipping the 29\ :sup:`th` February
``--yearly 1225``                          Sequence recurring every year on the 25\ :sup:`th` December
``--preset ecmwf-4days``                   Pre-defined sequence (equivalent to ``--monthly 1/5/.../29 --exclude 0229``)
=========================================  ===============================================================================

All the arguments can take slash-separated lists to specify multiple occurrences
within a week, month, or year, as well as multiple excludes. Week days can be
numeric (0 is Monday, 1 is Tuesday, etc.) or any unambiguous prefix of the name
(e.g., M, sa, FRIDAY).


Computing individual dates
~~~~~~~~~~~~~~~~~~~~~~~~~~

To get the previous or next date in a sequence, use ``earthkit-dateseq
previous`` or ``earthkit-dateseq next``:

.. code-block:: console

   $ earthkit-dateseq previous --weekly wed/fri 20240512
   20240510
   $ earthkit-dateseq next --weekly wed/fri 20240510
   20240515
   $ earthkit-dateseq next --weekly wed/fri --inclusive 20240510
   20240510
   $ earthkit-dateseq next --weekly wed/fri --skip 3 20240510
   20240524

If the given date is in the sequence, the default behaviour is to skip to the
previous or next one. To keep it, add the ``--inclusive`` option. More dates can
be skipped with the ``--skip`` option.

Similarly, the sequence date closest to a given date can be computed using
``earthkit-dateseq nearest``:

.. code-block:: console

   $ earthkit-dateseq nearest --monthly 1/15 20240704
   20240701
   $ earthkit-dateseq nearest --monthly 1/15 20240320
   20240315
   $ earthkit-dateseq nearest --monthly 1/15 20240808
   20240801
   $ earthkit-dateseq nearest --monthly 1/15 --resolve next 20240808
   20240815

If there is a tie, meaning that the given date is equidistant from the previous
and next date in the sequence, the previous date is returned. This behaviour can
be explicitly controlled by passing ``--resolve previous`` or ``--resolve
next``.


Computing sets of dates
~~~~~~~~~~~~~~~~~~~~~~~

To find all the sequence dates falling within a range, use ``earthkit-dateseq range``:

.. code-block:: console

   $ earthkit-dateseq range --sep ", " --weekly 0/2/4 20241201 20241216
   20241202, 20241204, 20241206, 20241209, 20241211, 20241213, 20241216
   $ earthkit-dateseq range --sep ", " --weekly 0/2/4 --exclude-end 20241201 20241216
   20241202, 20241204, 20241206, 20241209, 20241211, 20241213
   $ earthkit-dateseq range --sep ", " --weekly 0/2/4 --exclude-start 20241202 20241216
   20241204, 20241206, 20241209, 20241211, 20241213, 20241216

By default, ranges include the given start and end dates. The
``--exclude-start`` and ``--exclude-end`` flags override this behaviour.

The output sequences are formatted using the value of ``--sep``, if present,
otherwise each date is printed on a separate line.

To get a given number of dates around one reference, use ``earthkit-dateseq bracket``:

.. code-block:: console

   $ earthkit-dateseq bracket --sep ", " --weekly Saturday 19991127
   19991120, 19991204
   $ earthkit-dateseq bracket --sep ", " --weekly Saturday --inclusive 19991127
   19991120, 19991127, 19991204
   $ earthkit-dateseq bracket --sep ", " --weekly Saturday 20060528 3
   20060513, 20060520, 20060527, 20060603, 20060610, 20060617
   $ earthkit-dateseq bracket --sep ", " --weekly Saturday 20150403 1 2
   20150328, 20150404, 20150411
   $ earthkit-dateseq bracket --sep ", " --weekly Saturday --inclusive 19930717 2 1
   19930703, 19930710, 19930717, 19930724

The last two optional arguments are the number of dates to output, respectively
before and after the reference date. If none is given, one date either side is
returned. If one is given, the same number of dates either side is returned. If
the ``--inclusive`` flag is set and the reference date is in the sequence, it is
printed as well (but not counted towards the numbers requested).


Model climate dates
-------------------

The :program:`earthkit-climdates` command provides utilities to create sets of
dates for model climates.

To get one date per year on the same day as a given reference, use
``earthkit-climdates range``:

.. code-block:: console

   $ earthkit-climdates range --sep ", " --from-year 2000 --to-year 2005 20061023
   20001023, 20011023, 20021023, 20031023, 20041023, 20051023
   $ earthkit-climdates range --sep ", " --from-date 20020608 --to-date 20040701 20050602
   20030602, 20040602
   $ earthkit-climdates range --sep ", " --from-rel-year -3 --to-rel-year -1 20100805
   20070805, 20080805, 20090805

To combine yearly dates with multiple reference dates taken from a sequence, use
``earthkit-climdates mclim``:

.. code-block:: console

   $ earthkit-climdates mclim --sep ", " --from-year 2018 --to-year 2020 --before 7 --after 7 --preset ecmwf-mon-thu 20230806
   20180731, 20180803, 20180807, 20180810, 20190731, 20190803, 20190807, 20190810, 20200731, 20200803, 20200807, 20200810
   $ earthkit-climdates mclim --sep ", " --from-rel-year -7 --to-rel-year -4 --before 5 --after 5 --preset ecmwf-mon-thu 20230101
   20151229, 20160102, 20160105, 20161229, 20170102, 20170105, 20171229, 20180102, 20180105, 20181229, 20190102, 20190105
