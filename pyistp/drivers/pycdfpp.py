import pycdfpp


class Driver:
    def __init__(self, file):
        self.cdf = pycdfpp.load(file)

    def attributes(self):
        if self.cdf:
            return self.cdf.attributes.keys()
        return []

    def variables(self):
        if self.cdf:
            return list(self.cdf)
        return []

    def variable_attributes(self, var):
        if self.cdf:
            return self.cdf[var].attributes.keys()
        return []
