import netCDF4
import numpy as np
from typing import Any


class Driver:
    """NetCDF4 driver implementing the PyISTP Driver protocol."""

    def __init__(self, file):
        # Accept either a file path (str) or a bytes buffer
        if isinstance(file, bytes):
            self._ds = netCDF4.Dataset("in_memory.nc", memory=file)
        else:
            self._ds = netCDF4.Dataset(str(file), "r")

    def variables(self):
        return list(self._ds.variables.keys())

    def has_variable(self, name):
        return name in self._ds.variables

    def variable_attributes(self, var):
        if var not in self._ds.variables:
            return []
        return list(self._ds[var].ncattrs())

    def variable_attribute_value(self, var, attr):
        if var not in self._ds.variables:
            return None
        try:
            return self._ds[var].getncattr(attr)
        except AttributeError:
            return None

    def is_char(self, var):
        if var not in self._ds.variables:
            return False
        return self._ds[var].dtype == str

    def is_nrv(self, var):
        # NRV concept does not exist in NetCDF4
        return False

    def shape(self, var):
        return tuple(self._ds[var].shape)

    def attributes(self):
        return list(self._ds.ncattrs())

    def attribute(self, key):
        try:
            return self._ds.getncattr(key)
        except AttributeError:
            return None

    # Mapping from numpy dtype kinds to CDF type strings
    _DTYPE_TO_CDF = {
        'f4': 'CDF_FLOAT',
        'f8': 'CDF_DOUBLE',
        'i1': 'CDF_INT1',
        'i2': 'CDF_INT2',
        'i4': 'CDF_INT4',
        'i8': 'CDF_INT8',
        'u1': 'CDF_UINT1',
        'u2': 'CDF_UINT2',
        'u4': 'CDF_UINT4',
        'S':  'CDF_CHAR',
    }

    # Milliseconds between CDF epoch (year 0000) and Unix epoch (1970-01-01)
    _CDF_EPOCH_OFFSET_MS = 62_167_219_200_000

    def _get_units(self, var):
        """Return the units attribute, checking 'units' and 'UNITS'."""
        v = self._ds[var]
        for key in ('units', 'UNITS'):
            try:
                return v.getncattr(key)
            except AttributeError:
                pass
        return None

    def _is_cf_time(self, var):
        """Return True if the variable uses CF time conventions
        (float + units attribute containing 'since')."""
        units = self._get_units(var)
        return isinstance(units, str) and 'since' in units

    def _is_cdf_epoch(self, var):
        """Return True if the variable uses CDF_EPOCH convention
        (float64, units='ms')."""
        units = self._get_units(var)
        return (isinstance(units, str)
                and units.strip().lower() == 'ms'
                and self._ds[var].dtype == np.float64)

    def _cf_time_to_datetime64(self, var):
        """Convert a CF time variable (units with 'since') to
        datetime64[ns]."""
        v = self._ds[var]
        units = v.getncattr('units')
        # netCDF4.num2date converts CF floats to cftime objects
        dates: Any = netCDF4.num2date(
            v[:], units, only_use_cftime_datetimes=False
        )
        # Convert to datetime64[ns] via ISO string representation
        return np.array([np.datetime64(str(d), 'ns') for d in dates])

    def _cdf_epoch_to_datetime64(self, var):
        """Convert CDF_EPOCH (ms since year 0000) to datetime64[ns]."""
        ms = np.array(self._ds[var][:], dtype=np.float64)
        unix_ms = ms - self._CDF_EPOCH_OFFSET_MS
        return (unix_ms * 1_000_000).astype('datetime64[ns]')

    def values(self, var, is_metadata_variable=False):
        v = self._ds[var]
        if self._is_cf_time(var):
            return self._cf_time_to_datetime64(var)
        if self._is_cdf_epoch(var):
            return self._cdf_epoch_to_datetime64(var)
        if v.dtype == str:
            # Native NetCDF4 string — return as numpy array of strings
            raw = v[()]
            if isinstance(raw, str):
                raw = [raw]
            return np.array(raw)
        return np.array(v[:])

    def cdf_type(self, var):
        v = self._ds[var]
        # CF time variable: float with a "units" attribute containing "since"
        try:
            units = v.getncattr('units')
            if isinstance(units, str) and 'since' in units:
                return 'CDF_TIME_TT2000'
        except AttributeError:
            pass
        if v.dtype == str:
            return 'CDF_CHAR'
        dtype_str = v.dtype.str.lstrip('<>=!')
        return self._DTYPE_TO_CDF.get(dtype_str, f'CDF_UNKNOWN_{dtype_str}')
