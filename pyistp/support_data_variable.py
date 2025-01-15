import numpy as np


class SupportDataVariable:
    __slots__ = ("name", "values", 'attributes', 'is_nrv', 'cdf_type')

    def __init__(self, name, values, attributes, is_nrv, cdf_type):
        self.name = name
        self.values = values
        if type(self.values) is list:
            self.values = np.array(self.values)
        self.attributes = attributes
        self.is_nrv = is_nrv
        self.cdf_type = cdf_type

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return f"""SupportDataVariable: {self.name}
Attributes:
{self.attributes}\n"""
