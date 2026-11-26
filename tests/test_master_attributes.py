"""Which file a variable's attributes come from when a master CDF is given.

Values come from the data file when it has the variable; the attributes that give those values their meaning
(UNITS, SI_CONVERSION, FILLVAL, VALIDMIN, VALIDMAX) come from that same file. The master overrides the descriptive
attributes, as CDAWeb does: https://cdaweb.gsfc.nasa.gov/pub/software/cdawlib/0MASTERS/00readme.txt
"""
import numpy as np
import pycdfpp
import pytest

import pyistp

_EPOCH = np.arange('2015-10-16T12:00', '2015-10-16T12:01', np.timedelta64(10, 's'), dtype='datetime64[ns]')


def _cdf(delta_value, delta_type, delta_attributes, global_attributes=None, with_delta=True, data_records=True,
         density_attributes=None):
    cdf = pycdfpp.CDF()
    for name, value in (global_attributes or {}).items():
        cdf.add_attribute(name, [value])
    epoch = _EPOCH if data_records else _EPOCH[:0]
    cdf.add_variable("Epoch", values=epoch, data_type=pycdfpp.DataType.CDF_TIME_TT2000,
                     attributes={"VAR_TYPE": "support_data", "UNITS": "ns", "DELTA_PLUS_VAR": "Epoch_plus_var",
                                 "DELTA_MINUS_VAR": "Epoch_plus_var"})
    if with_delta:
        cdf.add_variable("Epoch_plus_var", values=np.array([delta_value]), data_type=delta_type, is_nrv=True,
                         attributes={"VAR_TYPE": "support_data", **delta_attributes})
    values = np.ones(len(epoch), dtype=np.float32)
    cdf.add_variable("density", values=values,
                     attributes={"VAR_TYPE": "data", "DEPEND_0": "Epoch", "CATDESC": "density from the file",
                                 "UNITS": "cm^-3", "FILLVAL": np.float32(-1e31), "DISPLAY_TYPE": "time_series",
                                 **(density_attributes or {})})
    return bytes(pycdfpp.save(cdf))


_DATA = dict(delta_value=4.5, delta_type=pycdfpp.DataType.CDF_REAL4,
             delta_attributes={"UNITS": "s", "SI_CONVERSION": "1.0>s", "VALIDMIN": 0.0, "VALIDMAX": 10.0,
                               "FILLVAL": -1e31, "CATDESC": "data file description", "LABLAXIS": "dt"})
_MASTER = dict(delta_value=150, delta_type=pycdfpp.DataType.CDF_UINT2,
               delta_attributes={"UNITS": "ms", "SI_CONVERSION": "1.0e-3>s", "VALIDMIN": 0, "VALIDMAX": 1000,
                                 "FILLVAL": 65535, "CATDESC": "master description"})


def _load(data=_DATA, master=_MASTER, **kwargs):
    return pyistp.load(buffer=_cdf(**data, **kwargs.get('data_kwargs', {})),
                       master_buffer=_cdf(**master, data_records=False, **kwargs.get('master_kwargs', {})))


def _delta(loader):
    return loader.support_data_variable("Epoch_plus_var")


def test_values_and_their_units_come_from_the_same_file():
    delta = _delta(_load())
    assert float(delta.values) == 4.5
    assert delta.attributes["UNITS"] == "s"
    assert delta.attributes["SI_CONVERSION"] == "1.0>s"


@pytest.mark.parametrize("name, expected", [("VALIDMIN", 0.0), ("VALIDMAX", 10.0), ("FILLVAL", -1e31)])
def test_every_value_attribute_comes_from_the_file_holding_the_values(name, expected):
    assert float(np.asarray(_delta(_load()).attributes[name]).ravel()[0]) == pytest.approx(expected)


def test_the_master_still_overrides_descriptive_attributes():
    assert _delta(_load()).attributes["CATDESC"] == "master description"


def test_attributes_only_the_data_file_has_are_kept():
    assert _delta(_load()).attributes["LABLAXIS"] == "dt"


def test_a_value_attribute_only_the_master_has_does_not_describe_the_data_file_values():
    data = dict(_DATA, delta_attributes={"CATDESC": "data file description"})
    attributes = _delta(_load(data=data)).attributes
    assert "UNITS" not in attributes
    assert attributes["CATDESC"] == "master description"


def test_a_variable_only_in_the_master_takes_everything_from_it():
    delta = _delta(_load(data_kwargs={"with_delta": False}))
    assert float(delta.values) == 150
    assert delta.attributes["UNITS"] == "ms"
    assert delta.attributes["CATDESC"] == "master description"


def test_data_variables_follow_the_same_rule():
    loader = _load(master_kwargs={"density_attributes": {"UNITS": "m^-3", "CATDESC": "density patched by the master"}})
    density = loader.data_variable("density")
    assert density.attributes["UNITS"] == "cm^-3"
    assert density.attributes["CATDESC"] == "density patched by the master"


def test_without_a_master_everything_comes_from_the_file():
    delta = pyistp.load(buffer=_cdf(**_DATA)).support_data_variable("Epoch_plus_var")
    assert delta.attributes["UNITS"] == "s"
    assert delta.attributes["CATDESC"] == "data file description"


def test_a_global_attribute_set_to_a_space_in_the_master_is_the_data_file_s():
    loader = _load(data_kwargs={"global_attributes": {"Data_version": "3.4.0", "Mission_group": "MMS"}},
                   master_kwargs={"global_attributes": {"Data_version": " ", "Mission_group": "MMS master"}})
    assert loader.attribute("Data_version")[0] == "3.4.0"
    assert loader.attribute("Mission_group")[0] == "MMS master"
