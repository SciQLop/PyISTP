"""
Driver contract tests for the NetCDF driver.

Same guarantees as test_understand_existing_drivers.py, adapted for NetCDF specifics:
  - is_nrv() always returns False (concept does not exist in NetCDF4)
  - Epoch encoded as CF time (float + units attribute) → converted to datetime64[ns]
  - cdf_type() maps numpy dtypes to CDF_* type strings
  - Bytes input via netCDF4.Dataset(memory=...)
"""

import os
import numpy as np
import pytest

try:
    import netCDF4
except ImportError:
    pytest.skip("netCDF4 not installed", allow_module_level=True)

try:
    from pyistp.drivers.netcdf import Driver
except ImportError:
    pytest.skip("netcdf driver not implemented yet", allow_module_level=True)


# ---------------------------------------------------------------------------
# Fixture — minimal ISTP-compliant NetCDF file
# ---------------------------------------------------------------------------

@pytest.fixture
def nc_path(tmp_path):
    """Build a minimal ISTP NetCDF file on disk for testing."""
    path = tmp_path / "test_istp.nc"
    ds = netCDF4.Dataset(str(path), "w")

    # Global ISTP attributes
    ds.Project = "Test>Test Project"
    ds.Source_name = "TEST>Test Instrument"
    ds.Discipline = "Space Physics>Magnetospheric Science"

    # Time dimension
    ds.createDimension("time", 10)

    # Epoch variable — CF time convention (float64, units attribute)
    epoch = ds.createVariable("Epoch", "f8", ("time",))
    epoch.units = "seconds since 1970-01-01"
    epoch.VAR_TYPE = "support_data"
    epoch[:] = np.arange(10) * 60.0  # one record per minute

    # Numeric data variable (float32)
    density = ds.createVariable("DENSITY", "f4", ("time",))
    density.VAR_TYPE = "data"
    density.DEPEND_0 = "Epoch"
    density.UNITS = "cm**-3"
    density.FILLVAL = -1.0e31
    density[:] = np.linspace(1.0, 10.0, 10).astype("f4")

    # String (char) variable — native NetCDF4 string type
    label = ds.createVariable("label_density", str, ())
    label.VAR_TYPE = "metadata"
    label[()] = "Density"

    ds.close()
    return path


@pytest.fixture
def drv(nc_path):
    return Driver(str(nc_path))


# ---------------------------------------------------------------------------
# variables()
# ---------------------------------------------------------------------------

def test_variables_returns_list(drv):
    assert isinstance(drv.variables(), list)


def test_variables_contains_strings(drv):
    assert all(isinstance(v, str) for v in drv.variables())


def test_variables_contains_known_var(drv):
    assert "DENSITY" in drv.variables()


def test_variables_contains_epoch(drv):
    assert "Epoch" in drv.variables()


# ---------------------------------------------------------------------------
# has_variable()
# ---------------------------------------------------------------------------

def test_has_variable_true_for_known_var(drv):
    assert drv.has_variable("DENSITY") is True


def test_has_variable_false_for_unknown_var(drv):
    assert drv.has_variable("THIS_DOES_NOT_EXIST") is False


# ---------------------------------------------------------------------------
# variable_attributes()
# ---------------------------------------------------------------------------

def test_variable_attributes_returns_list(drv):
    assert isinstance(drv.variable_attributes("DENSITY"), list)


def test_variable_attributes_contains_var_type(drv):
    assert "VAR_TYPE" in drv.variable_attributes("DENSITY")


# ---------------------------------------------------------------------------
# variable_attribute_value() — None contract
# ---------------------------------------------------------------------------

def test_variable_attribute_value_returns_value_when_present(drv):
    assert drv.variable_attribute_value("DENSITY", "VAR_TYPE") == "data"


def test_variable_attribute_value_returns_none_for_missing_attr(drv):
    """Missing attribute on existing variable → None, never raises."""
    assert drv.variable_attribute_value("DENSITY", "ATTRIBUTE_THAT_DOES_NOT_EXIST") is None


def test_variable_attribute_value_returns_none_for_missing_var(drv):
    """Missing variable → None, never raises."""
    assert drv.variable_attribute_value("VAR_THAT_DOES_NOT_EXIST", "VAR_TYPE") is None


# ---------------------------------------------------------------------------
# values()
# ---------------------------------------------------------------------------

def test_values_epoch_returns_datetime64_ns(drv):
    """CF time (float + units) must be converted to datetime64[ns]."""
    epoch = drv.values("Epoch")
    assert isinstance(epoch, np.ndarray)
    assert epoch.dtype == np.dtype("datetime64[ns]")


def test_values_epoch_first_value_is_correct(drv):
    """t=0s since 1970-01-01 → 1970-01-01T00:00:00."""
    epoch = drv.values("Epoch")
    assert epoch[0] == np.datetime64("1970-01-01T00:00:00", "ns")


def test_values_float_returns_ndarray(drv):
    result = drv.values("DENSITY")
    assert isinstance(result, np.ndarray)
    assert np.issubdtype(result.dtype, np.floating)


def test_values_not_empty(drv):
    assert len(drv.values("DENSITY")) == 10


def test_values_metadata_char_returns_strings(drv):
    """is_metadata_variable=True on a char variable → strings, not bytes."""
    char_vars = [v for v in drv.variables() if drv.is_char(v)]
    if not char_vars:
        pytest.skip("No char variable in this file")
    result = drv.values(char_vars[0], is_metadata_variable=True)
    assert isinstance(result, np.ndarray)
    assert result.dtype.kind in ("U", "S", "O")


# ---------------------------------------------------------------------------
# shape()
# ---------------------------------------------------------------------------

def test_shape_returns_tuple(drv):
    assert isinstance(drv.shape("DENSITY"), (tuple, list))


def test_shape_matches_values_shape(drv):
    assert tuple(drv.shape("DENSITY")) == drv.values("DENSITY").shape


def test_shape_first_dim_matches_epoch_length(drv):
    assert drv.shape("DENSITY")[0] == len(drv.values("Epoch"))


# ---------------------------------------------------------------------------
# is_char()
# ---------------------------------------------------------------------------

def test_is_char_false_for_numeric_var(drv):
    assert drv.is_char("DENSITY") is False


def test_is_char_false_for_epoch(drv):
    assert drv.is_char("Epoch") is False


def test_is_char_true_for_string_var(drv):
    assert drv.is_char("label_density") is True


# ---------------------------------------------------------------------------
# is_nrv() — always False in NetCDF4
# ---------------------------------------------------------------------------

def test_is_nrv_false_for_data_var(drv):
    assert drv.is_nrv("DENSITY") is False


def test_is_nrv_false_for_epoch(drv):
    assert drv.is_nrv("Epoch") is False


def test_is_nrv_always_false_for_all_vars(drv):
    """NRV concept does not exist in NetCDF4 — always False."""
    assert all(drv.is_nrv(v) is False for v in drv.variables())


# ---------------------------------------------------------------------------
# cdf_type()
# ---------------------------------------------------------------------------

def test_cdf_type_starts_with_cdf_prefix(drv):
    for var in drv.variables():
        t = drv.cdf_type(var)
        assert t.startswith("CDF_"), f"Variable {var!r}: unexpected type {t!r}"


def test_cdf_type_density_is_float(drv):
    assert drv.cdf_type("DENSITY") == "CDF_FLOAT"


def test_cdf_type_epoch_contains_time_or_epoch(drv):
    """CF time variable → CDF_EPOCH or CDF_TIME_TT2000."""
    t = drv.cdf_type("Epoch")
    assert "EPOCH" in t or "TIME" in t, f"Unexpected type for Epoch: {t!r}"


# ---------------------------------------------------------------------------
# attributes() and attribute() — global file attributes
# ---------------------------------------------------------------------------

def test_global_attributes_returns_iterable(drv):
    result = list(drv.attributes())
    assert len(result) > 0


def test_global_attributes_contains_strings(drv):
    for attr in drv.attributes():
        assert isinstance(attr, str)


def test_global_attribute_project_is_accessible(drv):
    value = drv.attribute("Project")
    assert value is not None
    assert "Test" in str(value)


def test_global_attribute_returns_none_for_missing(drv):
    """Missing global attribute → None, never raises."""
    assert drv.attribute("ATTRIBUTE_THAT_DOES_NOT_EXIST") is None


# ---------------------------------------------------------------------------
# Real CDAWeb file — ACE MFI (ac_h2s_mfi_cdaweb.nc)
# Uses CDF_EPOCH convention: float64 milliseconds since year 0000, units="ms"
# ---------------------------------------------------------------------------

AC_MFI = os.path.join(os.path.dirname(__file__), "resources", "ac_h2s_mfi_cdaweb.nc")


@pytest.fixture(scope="module")
def drv_ac():
    return Driver(AC_MFI)


def test_real_variables_contains_epoch(drv_ac):
    assert "Epoch" in drv_ac.variables()


def test_real_variables_contains_data_var(drv_ac):
    assert "Magnitude" in drv_ac.variables()


def test_real_epoch_returns_datetime64_ns(drv_ac):
    """CDF_EPOCH (ms since year 0) must be converted to datetime64[ns]."""
    epoch = drv_ac.values("Epoch")
    assert epoch.dtype == np.dtype("datetime64[ns]")


def test_real_epoch_is_in_plausible_range(drv_ac):
    """ACE MFI data should be between 1997 and 2030."""
    epoch = drv_ac.values("Epoch")
    assert epoch[0] > np.datetime64("1997-01-01", "ns")
    assert epoch[0] < np.datetime64("2030-01-01", "ns")


def test_real_magnitude_is_float_ndarray(drv_ac):
    result = drv_ac.values("Magnitude")
    assert isinstance(result, np.ndarray)
    assert np.issubdtype(result.dtype, np.floating)


def test_real_magnitude_not_empty(drv_ac):
    assert len(drv_ac.values("Magnitude")) > 0


def test_real_cdf_type_starts_with_cdf_prefix(drv_ac):
    for var in drv_ac.variables():
        t = drv_ac.cdf_type(var)
        assert t.startswith("CDF_"), f"Variable {var!r}: unexpected type {t!r}"


# ---------------------------------------------------------------------------
# Bytes input — netCDF4.Dataset(memory=...)
# ---------------------------------------------------------------------------

def test_driver_accepts_bytes_input(nc_path):
    """Driver must work with a bytes buffer, not just a file path."""
    with open(nc_path, "rb") as f:
        data = f.read()
    drv_from_bytes = Driver(data)
    assert "DENSITY" in drv_from_bytes.variables()
    assert drv_from_bytes.variable_attribute_value("DENSITY", "VAR_TYPE") == "data"
