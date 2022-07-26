class DataVariable:
    __slots__ = ("name", "values", 'attributes', 'axes', 'labels')

    def __init__(self, name, values, attributes, axes, labels=None):
        self.name = name
        self.values = values
        self.attributes = attributes
        self.axes = axes or []
        self.labels = labels

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return f"""DataVariable: {self.name}
Attributes:
{self.attributes}
Axes:
{self.axes}\n"""
