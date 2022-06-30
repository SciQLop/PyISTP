class DataVariable:
    __slots__ = ("values", 'attributes', 'axes')

    def __init__(self, values, attributes, axes):
        self.values = values
        self.attributes = attributes
        self.axes = axes or []
