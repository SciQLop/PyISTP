from spacepy import pycdf


class Driver:
    def __init__(self, file):
        self.cdf = pycdf.CDF(file)
