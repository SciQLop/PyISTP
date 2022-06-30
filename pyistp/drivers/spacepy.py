from spacepy import pycdf


class Driver:
    def __init__(self, file):
        self.cdf = pycdf.CDF(file)

    def attributes(self):
        if self.cdf:
            return self.cdf.attrs.keys()
        return []

    def variables(self):
        if self.cdf:
            return self.cdf.keys()
        return []

    def variable_attributes(self, var):
        if self.cdf:
            return self.cdf[var].attrs.keys()
        return []

    def variable_attribute_value(self, var, attr):
        if self.cdf and var in self.cdf and attr in self.cdf[var].attrs:
            return self.cdf[var].attrs[attr][0]
        return None

    def values(self, var):
        return self.cdf[var][:]
