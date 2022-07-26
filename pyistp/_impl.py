from .drivers import current_driver
from .data_variable import DataVariable
from .support_data_variable import SupportDataVariable
import re
from typing import List

DEPEND_REGEX = re.compile("DEPEND_\\d")


def _get_attributes(cdf: object, var: str):
    attrs = {}
    for attr in cdf.variable_attributes(var):
        if attr.endswith("_PTR") or attr[:-1].endswith("_PTR_"):
            value = cdf.values(cdf.variable_attribute_value(var, attr))
            if hasattr(value, 'tolist'):
                attrs[attr] = value.tolist()
            else:
                attrs[attr] = value
        else:
            attrs[attr] = cdf.variable_attribute_value(var, attr)
    return attrs


def _get_axis(cdf: object, var: str):
    if cdf.is_char(var):
        return None
    return SupportDataVariable(name=var, values=cdf.values(var), attributes=_get_attributes(cdf, var))


def _get_axes(cdf: object, var: str):
    attrs = sorted(filter(lambda attr: DEPEND_REGEX.match(attr), cdf.variable_attributes(var)))
    unix_time_name = cdf.variable_attribute_value(var, "DEPEND_TIME")
    axes = list(map(lambda attr: _get_axis(cdf, cdf.variable_attribute_value(var, attr)), attrs))
    if unix_time_name is not None:
        unix_time = _get_axis(cdf, unix_time_name)
        if len(unix_time) > len(axes[0]):
            unix_time.values = (unix_time.values * 1e9).astype('<M8[ns]')
            axes[0] = unix_time
            Warning(
                "Non compliant CDF file, swapping DEPEND_0 with DEPEND_TIME, if you think this is a bug report it here: https://github.com/SciQLop/PyISTP/issues")
    return axes


def _get_labels(attributes) -> List[str]:
    if 'LABL_PTR_1' in attributes:
        return attributes['LABL_PTR_1']
    if 'LABLAXIS' in attributes:
        return [attributes['LABLAXIS']]


def _load_data_var(cdf: object, var: str) -> DataVariable or None:
    axes = _get_axes(cdf, var)
    attributes = _get_attributes(cdf, var)
    labels = _get_labels(attributes)
    if None in axes:
        return None
    return DataVariable(name=var, values=cdf.values(var), attributes=attributes, axes=axes, labels=labels)


class ISTPLoaderImpl:
    cdf = None

    def __init__(self, file=None, buffer=None):
        self.cdf = current_driver(file or buffer)
        self.data_variables = []
        self._update_data_vars_lis()

    def attributes(self):
        return self.cdf.attributes()

    def attribute(self, key):
        return self.cdf.attribute(key)

    def _update_data_vars_lis(self):
        if self.cdf:
            self.data_variables = []
            for var in self.cdf.variables():
                var_attrs = self.cdf.variable_attributes(var)
                var_type = self.cdf.variable_attribute_value(var, 'VAR_TYPE')
                if var_type == 'data' and not self.cdf.is_char(var):
                    self.data_variables.append(var)

    def data_variable(self, var_name):
        return _load_data_var(self.cdf, var_name)
