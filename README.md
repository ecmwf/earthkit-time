# earthkit.time

:warning: This project is BETA and will be experimental for the foreseeable
future. Interfaces and functionality are likely to change, and the project
itself may be scrapped. DO NOT use this software in any project/software that is
operational.

Date and time manipulation routines for the use of weather data

## Python API

### When is the next Tuesday?

```python
import datetime
from earthkit.time import WeeklySequence
from earthkit.time.calendar import TUESDAY
sequence = WeeklySequence(TUESDAY)
next_tue = sequence.next(datetime.date.today())
print(f"Next Tuesday: {next_tue:%Y%m%d}")
```

### Pre-defined sequences

```python
import datetime
from earthkit.time import Sequence
sequence = Sequence.from_resource("ecmwf-4days")
dates = sequence.range(datetime.date(2024, 2, 1), datetime.date(2024, 3, 1), include_end=False)
print("February dates:", ", ".join(date.strftime("%Y%m%d") for date in dates))
```

### Model climate dates

```python
import datetime
from earthkit.time import Sequence, model_climate_dates
sequence = Sequence.from_resource("ecmwf-2days")
dates = model_climate_dates(datetime.date(2024, 2, 12), 2020, 2023, 7, 7, sequence)
print("Model climate dates:", ", ".join(date.strftime("%Y%m%d") for date in dates))
```

## Command-line interface

### Give me the two previous prime-numbered days and the next

```bash
earthkit-dateseq bracket --monthly 2/3/5/7/11/13/17/19/23/29/31 20240510 2 1
```

### Model climate dates

```bash
earthkit-climdates mclim --from-year 2015 --to-year 2020 --before 7 --after 7 --preset ecmwf-mon-thu 20230806
```

## License
[Apache License 2.0](LICENSE) In applying this licence, ECMWF does not waive the privileges and immunities
granted to it by virtue of its status as an intergovernmental organisation nor does it submit to any jurisdiction.