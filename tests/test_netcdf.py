"""
Tests for NetCDF support in PyISTP.

Two test classes:
  - TestNetCDFDriver  : contract tests for pyistp.drivers.netcdf.Driver
  - TestLoadNetCDF    : integration tests for pyistp.load()
"""

import os

import netCDF4
import numpy as np
import pytest

import pyistp
from pyistp.drivers.netcdf import Driver

AC_MFI = os.path.join(
    os.path.dirname(__file__), "resources", "ac_h2s_mfi_cdaweb.nc"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def nc_path(tmp_path):
    """Build a minimal ISTP NetCDF file on disk for testing."""
    path = tmp_path / "test_istp.nc"
    ds = netCDF4.Dataset(str(path), "w")

    ds.Project = "Test>Test Project"
    ds.Source_name = "TEST>Test Instrument"
    ds.Discipline = "Space Physics>Magnetospheric Science"

    ds.createDimension("time", 10)

    epoch = ds.createVariable("Epoch", "f8", ("time",))
    epoch.units = "seconds since 1970-01-01"
    epoch.VAR_TYPE = "support_data"
    epoch[:] = np.arange(10) * 60.0

    density = ds.createVariable("DENSITY", "f4", ("time",))
    density.VAR_TYPE = "data"
    density.DEPEND_0 = "Epoch"
    density.UNITS = "cm**-3"
    density.FILLVAL = -1.0e31
    density[:] = np.linspace(1.0, 10.0, 10).astype("f4")

    label = ds.createVariable("label_density", str, ())
    label.VAR_TYPE = "metadata"
    label[()] = "Density"

    ds.close()
    return path


@pytest.fixture
def drv(nc_path):
    return Driver(str(nc_path))


@pytest.fixture(scope="module")
def drv_ac():
    return Driver(AC_MFI)


# ---------------------------------------------------------------------------
# TestNetCDFDriver — driver contract tests
# ---------------------------------------------------------------------------


class TestNetCDFDriver:
    # variables()

    def test_variables_returns_list(self, drv):
        assert isinstance(drv.variables(), list)

    def test_variables_contains_strings(self, drv):
        assert all(isinstance(v, str) for v in drv.variables())

    def test_variables_contains_known_var(self, drv):
        assert "DENSITY" in drv.variables()

    def test_variables_contains_epoch(self, drv):
        assert "Epoch" in drv.variables()

    # has_variable()

    def test_has_variable_true_for_known_var(self, drv):
        assert drv.has_variable("DENSITY") is True

    def test_has_variable_false_for_unknown_var(self, drv):
        assert drv.has_variable("THIS_DOES_NOT_EXIST") is False

    # variable_attributes()

    def test_variable_attributes_returns_list(self, drv):
        assert isinstance(drv.variable_attributes("DENSITY"), list)

    def test_variable_attributes_contains_var_type(self, drv):
        assert "VAR_TYPE" in drv.variable_attributes("DENSITY")

    # variable_attribute_value() — None contract

    def test_variable_attribute_value_returns_value_when_present(self, drv):
        assert drv.variable_attribute_value("DENSITY", "VAR_TYPE") == "data"

    def test_variable_attribute_value_returns_none_for_missing_attr(self, drv):
        """Missing attribute on existing variable → None, never raises."""
        assert (
            drv.variable_attribute_value(
                "DENSITY", "ATTRIBUTE_THAT_DOES_NOT_EXIST"
            )
            is None
        )

    def test_variable_attribute_value_returns_none_for_missing_var(self, drv):
        """Missing variable → None, never raises."""
        assert (
            drv.variable_attribute_value("VAR_THAT_DOES_NOT_EXIST", "VAR_TYPE")
            is None
        )

    # values()

    def test_values_epoch_returns_datetime64_ns(self, drv):
        """CF time (float + units) must be converted to datetime64[ns]."""
        epoch = drv.values("Epoch")
        assert isinstance(epoch, np.ndarray)
        assert epoch.dtype == np.dtype("datetime64[ns]")

    def test_values_epoch_first_value_is_correct(self, drv):
        """t=0s since 1970-01-01 → 1970-01-01T00:00:00."""
        assert drv.values("Epoch")[0] == np.datetime64(
            "1970-01-01T00:00:00", "ns"
        )

    def test_values_float_returns_ndarray(self, drv):
        result = drv.values("DENSITY")
        assert isinstance(result, np.ndarray)
        assert np.issubdtype(result.dtype, np.floating)

    def test_values_not_empty(self, drv):
        assert len(drv.values("DENSITY")) == 10

    def test_values_metadata_char_returns_strings(self, drv):
        """is_metadata_variable=True on a char variable → strings, not bytes."""
        char_vars = [v for v in drv.variables() if drv.is_char(v)]
        if not char_vars:
            pytest.skip("No char variable in this file")
        result = drv.values(char_vars[0], is_metadata_variable=True)
        assert isinstance(result, np.ndarray)
        assert result.dtype.kind in ("U", "S", "O")

    # shape()

    def test_shape_returns_tuple(self, drv):
        assert isinstance(drv.shape("DENSITY"), (tuple, list))

    def test_shape_matches_values_shape(self, drv):
        assert tuple(drv.shape("DENSITY")) == drv.values("DENSITY").shape

    def test_shape_first_dim_matches_epoch_length(self, drv):
        assert drv.shape("DENSITY")[0] == len(drv.values("Epoch"))

    # is_char()

    def test_is_char_false_for_numeric_var(self, drv):
        assert drv.is_char("DENSITY") is False

    def test_is_char_false_for_epoch(self, drv):
        assert drv.is_char("Epoch") is False

    def test_is_char_true_for_string_var(self, drv):
        assert drv.is_char("label_density") is True

    # is_nrv() — always False in NetCDF4

    def test_is_nrv_false_for_data_var(self, drv):
        assert drv.is_nrv("DENSITY") is False

    def test_is_nrv_false_for_epoch(self, drv):
        assert drv.is_nrv("Epoch") is False

    def test_is_nrv_always_false_for_all_vars(self, drv):
        """NRV concept does not exist in NetCDF4 — always False."""
        assert all(drv.is_nrv(v) is False for v in drv.variables())

    # cdf_type()

    def test_cdf_type_starts_with_cdf_prefix(self, drv):
        for var in drv.variables():
            t = drv.cdf_type(var)
            assert t.startswith("CDF_"), (
                f"Variable {var!r}: unexpected type {t!r}"
            )

    def test_cdf_type_density_is_float(self, drv):
        assert drv.cdf_type("DENSITY") == "CDF_FLOAT"

    def test_cdf_type_epoch_contains_time_or_epoch(self, drv):
        """CF time variable → CDF_EPOCH or CDF_TIME_TT2000."""
        t = drv.cdf_type("Epoch")
        assert "EPOCH" in t or "TIME" in t, f"Unexpected type for Epoch: {t!r}"

    # attributes() / attribute() — global

    def test_global_attributes_returns_iterable(self, drv):
        assert len(list(drv.attributes())) > 0

    def test_global_attributes_contains_strings(self, drv):
        assert all(isinstance(a, str) for a in drv.attributes())

    def test_global_attribute_project_is_accessible(self, drv):
        value = drv.attribute("Project")
        assert value is not None
        assert "Test" in str(value)

    def test_global_attribute_returns_none_for_missing(self, drv):
        """Missing global attribute → None, never raises."""
        assert drv.attribute("ATTRIBUTE_THAT_DOES_NOT_EXIST") is None

    # Real CDAWeb file — ACE MFI

    def test_real_variables_contains_epoch(self, drv_ac):
        assert "Epoch" in drv_ac.variables()

    def test_real_variables_contains_data_var(self, drv_ac):
        assert "Magnitude" in drv_ac.variables()

    def test_real_epoch_returns_datetime64_ns(self, drv_ac):
        """CDF_EPOCH (ms since year 0) must be converted to datetime64[ns]."""
        assert drv_ac.values("Epoch").dtype == np.dtype("datetime64[ns]")

    def test_real_epoch_is_in_plausible_range(self, drv_ac):
        epoch = drv_ac.values("Epoch")
        assert epoch[0] > np.datetime64("1997-01-01", "ns")
        assert epoch[0] < np.datetime64("2030-01-01", "ns")

    def test_real_magnitude_is_float_ndarray(self, drv_ac):
        result = drv_ac.values("Magnitude")
        assert isinstance(result, np.ndarray)
        assert np.issubdtype(result.dtype, np.floating)

    def test_real_magnitude_not_empty(self, drv_ac):
        assert len(drv_ac.values("Magnitude")) > 0

    def test_real_cdf_type_starts_with_cdf_prefix(self, drv_ac):
        for var in drv_ac.variables():
            t = drv_ac.cdf_type(var)
            assert t.startswith("CDF_"), (
                f"Variable {var!r}: unexpected type {t!r}"
            )

    def test_real_epoch_cdf_type_is_cdf_epoch(self, drv_ac):
        """Epoch in the CDAWeb file has UNITS='ms' (uppercase, no 'since').
        cdf_type() must return 'CDF_EPOCH', consistent with values() which
        returns datetime64[ns] via _is_cdf_epoch()."""
        assert drv_ac.cdf_type("Epoch") == "CDF_EPOCH"

    # Bytes input

    def test_driver_accepts_bytes_input(self, nc_path):
        """Driver must work with a bytes buffer, not just a file path."""
        with open(nc_path, "rb") as f:
            raw = f.read()
        drv_from_bytes = Driver(raw)
        assert "DENSITY" in drv_from_bytes.variables()
        assert (
            drv_from_bytes.variable_attribute_value("DENSITY", "VAR_TYPE")
            == "data"
        )


# ---------------------------------------------------------------------------
# TestLoadNetCDF — pyistp.load() integration tests
# ---------------------------------------------------------------------------


class TestLoadNetCDF:
    def test_returns_loader(self, nc_path):
        assert pyistp.load(file=str(nc_path)) is not None

    def test_finds_data_variables(self, nc_path):
        loader = pyistp.load(file=str(nc_path))
        assert "DENSITY" in loader.data_variables()

    def test_loads_variable(self, nc_path):
        loader = pyistp.load(file=str(nc_path))
        assert loader.data_variable("DENSITY") is not None

    def test_variable_has_time_axis(self, nc_path):
        loader = pyistp.load(file=str(nc_path))
        var = loader.data_variable("DENSITY")
        assert len(var.axes) >= 1
        assert var.axes[0].values.dtype == np.dtype("datetime64[ns]")

    def test_variable_values_shape_matches_time(self, nc_path):
        loader = pyistp.load(file=str(nc_path))
        var = loader.data_variable("DENSITY")
        assert var.values.shape[0] == var.axes[0].values.shape[0]

    def test_real_file_returns_loader(self):
        assert pyistp.load(file=AC_MFI) is not None

    def test_real_file_has_data_variables(self):
        loader = pyistp.load(file=AC_MFI)
        assert len(loader.data_variables()) > 0
