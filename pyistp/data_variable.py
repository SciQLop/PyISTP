from typing import Collection, Callable, Any, Union


class DataVariable:
    __slots__ = ("name", "_values", 'attributes', 'axes', 'labels', 'cdf_type')

    def __init__(self, name: str, values: Union[Collection[Any], Callable], attributes, axes, cdf_type, labels=None):
        self.name = name
        self._values = values
        self.attributes = attributes
        self.axes = axes or []
        self.labels = labels
        self.cdf_type = cdf_type

    @property
    def values(self):
        if callable(self._values):
            self._values = self._values()
        return self._values

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return f"""DataVariable: {self.name}
Attributes:
{self.attributes}
Axes:
{self.axes}\n"""
