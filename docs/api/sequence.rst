earthkit.time.sequence - Manipulate sequence of dates
=====================================================

.. module:: earthkit.time.sequence

Sequence API
------------

Sequences are described by subclasses of :class:`Sequence`.

.. autoclass:: Sequence
    :members:


Sequence creation shortcut
--------------------------

Besides the class constructors and factory methods, sequences can be created
using :func:`create_sequence`.

.. autofunction:: create_sequence


Built-in Sequences
------------------

.. autoclass:: DailySequence

.. autoclass:: WeeklySequence

.. autoclass:: MonthlySequence

.. autoclass:: YearlySequence

