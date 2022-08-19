import numpy as np


class SupportDataVariable:
    __slots__ = ("name", "values", 'attributes')

    def __init__(self, name, values, attributes):
        self.name = name
        self.values = values
        if type(self.values) is list:
            self.values = np.array(self.values)
        self.attributes = attributes

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return f"""SupportDataVariable: {self.name}
Attributes:
{self.attributes}\n"""
