from .drivers import current_driver
from .data_variable import DataVariable


def _get_axes(cdf: object, var: str):
    attrs = sorted(filter(lambda attr: attr.startswith('DEPEND_'), cdf.variable_attributes(var)))
    axes = list(map(lambda attr: cdf.values(cdf.variable_attribute_value(var, attr)), attrs))
    return axes


def _get_attributes(cdf: object, var: str):
    pass


def _load_data_var(cdf: object, var: str) -> DataVariable:
    return DataVariable(values=cdf.values(var), attributes=_get_attributes(cdf, var), axes=_get_axes(cdf, var))


class ISTPLoaderImpl:
    cdf = None

    def __init__(self, file=None, buffer=None):
        self.cdf = current_driver(file or buffer)
        self.data_variables = []
        self._update_data_vars_lis()

    def _update_data_vars_lis(self):
        if self.cdf:
            self.data_variables = []
            for var in self.cdf.variables():
                var_attrs = self.cdf.variable_attributes(var)
                var_type = self.cdf.variable_attribute_value(var, 'VAR_TYPE')
                if var_type == 'data':
                    self.data_variables.append(var)
