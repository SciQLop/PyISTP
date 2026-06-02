# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

PyISTP is a loader for ISTP-compliant scientific data files (NASA/space-physics
CDF and NetCDF). It reads data variables together with their support/axis
variables and attributes, following the ISTP metadata conventions (`VAR_TYPE`,
`DEPEND_n`, `*_PTR`, `LABLAXIS`, etc.). It is a dependency of SciQLop/speasy.

## Commands

The project uses `flit` for packaging — there is **no `setup.py`**, so the
`python setup.py test` targets in `Makefile`/`tox.ini` are stale. Use pytest:

```bash
pip install -e . && pip install -r requirements_dev.txt   # dev setup
pytest                                                     # run all tests
pytest tests/test_netcdf.py                                # one file
pytest tests/test_pyistp.py::TestPyIstp::test_is_nrv       # one test
pytest --cov=./ --cov-report=xml                           # with coverage (as CI runs)
flake8 pyistp tests                                        # lint
make doctest                                               # run doc doctests
```

Note `tests/test_pyistp.py` uses `unittest` + `ddt` (data-driven cases over a
`test_data` tuple of `(file, expected_data_vars)`), while `tests/test_netcdf.py`
uses plain `pytest`. Test fixtures live in `tests/resources/` (real `.cdf`/`.nc`
files); add a new resource file and a row to `test_data` to cover a new case.

## Architecture

The public API is tiny: `pyistp.load(file=, buffer=, master_file=, master_buffer=)`
returns an `ISTPLoader` exposing `attributes()`, `attribute(key)`,
`data_variables()` (list of names), and `data_variable(name)` (a `DataVariable`).

Three layers:

1. **Facade** — `loader.py` (`ISTPLoader`) is a thin pass-through to
   `_impl.py` (`ISTPLoaderImpl`), which holds the ISTP interpretation logic.
   The split keeps `import pyistp` cheap: the heavy driver import only happens
   inside `ISTPLoader.__init__`.

2. **ISTP logic** — `_impl.py` is where the conventions are applied, all driver-agnostic:
   - `_driver_factory` sniffs the first 4 magic bytes to pick NetCDF
     (`\x89HDF` / `CDF`) vs. the configured CDF driver.
   - `_update_data_vars_lis` selects data variables: `VAR_TYPE == 'data'`
     (case-insensitive) or Cluster-CSA's `PARAMETER_TYPE == 'data'`, excluding
     char variables.
   - `_get_axes` / `_get_axis` resolve `DEPEND_n` attributes into
     `SupportDataVariable` axes, falling back from the data file to the master
     file, with special handling for `DEPEND_TIME` and Cluster-CSA `sig_digits`.
   - `_get_attributes` dereferences `*_PTR` attributes to their pointed-to
     variable's values.
   - A **master CDF** (skeleton file holding the metadata) can be supplied
     separately from the data file; when present, attributes/axis definitions
     are read from `master_cdf` and values from `cdf`. Many CDAWeb/AMDA files
     are non-ISTP-compliant — the code logs warnings (`ISTP_NOT_COMPLIANT_W`)
     and applies vendor-specific workarounds rather than failing.

3. **Drivers** — `drivers/` adapts a backend CDF/NetCDF library to the
   `Driver` Protocol in `drivers/_driver.py`. `pycdfpp` is the default CDF
   backend; `spacepy` is the fallback. `_load_cdf_lib` (in `drivers/__init__.py`)
   picks one at import time, overridable via the `PYISTP_CDFLIB` env var.
   `drivers/netcdf.py` (netCDF4) is selected by magic bytes, not by that list.
   To support a new backend, implement every method of the `Driver` Protocol.

### Key conventions a driver must honor

- **Time conversion** happens in the driver's `values()`: CDF epoch types and
  NetCDF CF-time / `units='ms'` / `units='milliseconds'` are all converted to
  `numpy.datetime64[ns]`. `cdf_type()` reports a normalized `CDF_*` type string
  (NetCDF dtypes are mapped to `CDF_*` names) so downstream code is uniform.
- **NRV** (non-record-variant) variables: `is_nrv()` plus the
  `_drop_first_dim_if_nrv` helper collapse the leading record dimension. NetCDF
  has no NRV concept, so its driver returns `False`.
- `DataVariable.values` is **lazy** — `_load_data_var` passes a thunk and the
  array is materialized only on first `.values` access.
