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
