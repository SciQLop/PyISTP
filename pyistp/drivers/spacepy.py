from spacepy import pycdf
import numpy as np
from tempfile import NamedTemporaryFile


class Driver:
    def __init__(self, file):
        if type(file) is bytes:
            self._tmpfile = NamedTemporaryFile()
            self._tmpfile.write(file)
            self._tmpfile.flush()
            self.cdf = pycdf.CDF(self._tmpfile.name)
        else:
            self.cdf = pycdf.CDF(file)

    def attributes(self):
        if self.cdf:
            return self.cdf.attrs.keys()
        return []

    def attribute(self, key):
        if self.cdf:
            return self.cdf.attrs[key]
        return None

    def variables(self):
        if self.cdf:
            return self.cdf.keys()
        return []

    def has_variable(self, name):
        return name in self.cdf

    def variable_attributes(self, var):
        if self.cdf:
            return self.cdf[var].attrs.keys()
        return []

    def is_char(self, var):
        return self.cdf[var].type() == pycdf.const.CDF_CHAR

    def variable_attribute_value(self, var, attr):
        if self.cdf and var in self.cdf and attr in self.cdf[var].attrs:
            return self.cdf[var].attrs[attr]
        return None

    def values(self, var, is_metadata_variable=False):
        v = self.cdf[var]
        if v.type() in (pycdf.const.CDF_EPOCH, pycdf.const.CDF_EPOCH16, pycdf.const.CDF_TIME_TT2000):
            return np.vectorize(np.datetime64)(v[:])
        return v[:]

    def is_nrv(self, var):
        return not self.cdf[var].rv()

    def shape(self, var):
        return self.cdf[var].shape
