import pycdfpp


class Driver:
    def __init__(self, file):
        self.cdf = pycdfpp.load(file)
