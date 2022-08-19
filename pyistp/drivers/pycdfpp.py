import pycdfpp


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
        return self.cdf[var].type == pycdfpp.CDF_CHAR

    def variable_attributes(self, var):
        if self.cdf:
            return self.cdf[var].attributes.keys()
        return []

    def variable_attribute_value(self, var, attr):
        if self.cdf and var in self.cdf and attr in self.cdf[var].attributes:
            return self.cdf[var].attributes[attr][0]
        return None

    def values(self, var):
        v = self.cdf[var]
        if v.type in (pycdfpp.CDF_EPOCH, pycdfpp.CDF_EPOCH16, pycdfpp.CDF_TIME_TT2000):
            return pycdfpp.to_datetime64(v)
        return v.values
