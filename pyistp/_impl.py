from .drivers import current_driver
from .data_variable import DataVariable
from .support_data_variable import SupportDataVariable


def _get_attributes(cdf: object, var: str):
    attrs = {}
    for attr in cdf.variable_attributes(var):
        if attr.endswith("_PTR") or attr[:-1].endswith("_PTR_"):
            attrs[attr] = cdf.values(cdf.variable_attribute_value(var, attr))
        else:
            attrs[attr] = cdf.variable_attribute_value(var, attr)
    return attrs


def _get_axis(cdf: object, var: str):
    return SupportDataVariable(name=var, values=cdf.values(var), attributes=_get_attributes(cdf, var))


def _get_axes(cdf: object, var: str):
    attrs = sorted(filter(lambda attr: attr.startswith('DEPEND_'), cdf.variable_attributes(var)))
    axes = list(map(lambda attr: _get_axis(cdf, cdf.variable_attribute_value(var, attr)), attrs))
    return axes


def _load_data_var(cdf: object, var: str) -> DataVariable:
    return DataVariable(name=var, values=cdf.values(var), attributes=_get_attributes(cdf, var),
                        axes=_get_axes(cdf, var))


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
                if var_type == 'data':
                    self.data_variables.append(var)

    def data_variable(self, var_name):
        return _load_data_var(self.cdf, var_name)
