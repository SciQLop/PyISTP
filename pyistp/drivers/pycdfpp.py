import pycdfpp
import numpy as np


def _drop_first_dim_if_nrv(is_nrv: bool, values):
    if is_nrv:
        if values.shape[0] == 1:
            return values[0]
        else:
            return np.array([], dtype=values.dtype)
    else:
        return values


class Driver:
    def __init__(self, file):
        self.cdf = pycdfpp.load(file)

    def attributes(self):
        if self.cdf:
            return self.cdf.attributes.keys()
        return []

    def attribute(self, key):
        if self.cdf:
            return self.cdf.attributes[key]
        return None

    def variables(self):
        if self.cdf:
            return list(self.cdf)
        return []

    def has_variable(self, name):
        return name in self.cdf

    def is_char(self, var):
        return self.cdf[var].type == pycdfpp.DataType.CDF_CHAR

    def variable_attributes(self, var):
        if self.cdf:
            return self.cdf[var].attributes.keys()
        return []

    def variable_attribute_value(self, var, attr):
        if self.cdf and var in self.cdf and attr in self.cdf[var].attributes:
            return self.cdf[var].attributes[attr][0]
        return None

    def values(self, var, is_metadata_variable=False):
        v: pycdfpp.Variable = self.cdf[var]
        if v.type in (pycdfpp.DataType.CDF_EPOCH, pycdfpp.DataType.CDF_EPOCH16, pycdfpp.DataType.CDF_TIME_TT2000):
            return _drop_first_dim_if_nrv(v.is_nrv, pycdfpp.to_datetime64(v))
        if is_metadata_variable and self.is_char(var):
            return _drop_first_dim_if_nrv(v.is_nrv, v.values_encoded)
        return _drop_first_dim_if_nrv(v.is_nrv, v.values)

    def is_nrv(self, var):
        return self.cdf[var].is_nrv

    def shape(self, var):
        return self.cdf[var].shape
