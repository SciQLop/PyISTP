from xarray import DataArray


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

    def to_xarray(self) -> DataArray:
        axes = {ax.name: ax.values for ax in self.axes}
        dims = [ax.name for ax in self.axes]
        if len(self.values.shape) == 2 and len(axes) == 1:
            axes['components'] = self.labels
            dims.append('components')
        return DataArray(
            data=self.values,
            dims=dims,
            coords=axes,
            name=self.name,
            attrs=self.attributes
        )

    def __repr__(self):
        return f"""DataVariable: {self.name}
Attributes:
{self.attributes}
Axes:
{self.axes}\n"""
