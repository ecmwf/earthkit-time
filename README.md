<p align="center">
  <picture>
    <source srcset="https://github.com/ecmwf/logos/raw/refs/heads/main/logos/earthkit/earthkit-time-dark.svg" media="(prefers-color-scheme: dark)">
    <img src="https://github.com/ecmwf/logos/raw/refs/heads/main/logos/earthkit/earthkit-time-light.svg" height="120">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/ecmwf/codex/raw/refs/heads/main/ESEE">
    <img src="https://github.com/ecmwf/codex/raw/refs/heads/main/ESEE/foundation_badge.svg" alt="ECMWF Software EnginE">
  </a>
  <a href="https://github.com/ecmwf/codex/raw/refs/heads/main/Project Maturity">
    <img src="https://github.com/ecmwf/codex/raw/refs/heads/main/Project Maturity/emerging_badge.svg" alt="Maturity Level">
  </a>
  <!-- <a href="https://codecov.io/gh/ecmwf/earthkit-hydro">
    <img src="https://codecov.io/gh/ecmwf/earthkit-hydro/branch/develop/graph/badge.svg" alt="Code Coverage">
  </a> -->
  <a href="https://opensource.org/licenses/apache-2-0">
    <img src="https://img.shields.io/badge/Licence-Apache 2.0-blue.svg" alt="Licence">
  </a>
  <a href="https://github.com/ecmwf/earthkit-time/tags">
    <img src="https://img.shields.io/github/v/tag/ecmwf/earthkit-time?color=purple&label=Release" alt="Latest Release">
  </a>
</p>

<p align="center">
  <!-- <a href="#quick-start">Quick Start</a>
  • -->
  <a href="#installation">Installation</a>
  •
  <a href="https://earthkit-time.readthedocs.io">Documentation</a>
</p>

> \[!IMPORTANT\]
> This software is **Emerging** and subject to ECMWF's guidelines on [Software Maturity](https://github.com/ecmwf/codex/raw/refs/heads/main/Project%20Maturity).

Date and time manipulation routines for the use of weather data

## Documentation

The documentation can be found at https://earthkit-time.readthedocs.io.

## Installation
Install from PyPI:

```
pip install earthkit-time
```

## Quick Start

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

## Licence

```
Copyright 2024, European Centre for Medium Range Weather Forecasts.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

In applying this licence, ECMWF does not waive the privileges and immunities
granted to it by virtue of its status as an intergovernmental organisation
nor does it submit to any jurisdiction.
```
