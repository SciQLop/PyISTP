from .drivers import current_driver, Driver
from .data_variable import DataVariable
from .support_data_variable import SupportDataVariable
import re
import numpy as np
from typing import List, Optional
import logging

DEPEND_REGEX = re.compile("DEPEND_\\d")

ISTP_NOT_COMPLIANT_W = "Non compliant ISTP file"

log = logging.getLogger(__name__)


def _get_attributes(master_cdf: Driver, cdf: Driver, var: str):
    attrs = {}
    for attr in master_cdf.variable_attributes(var):
        value = master_cdf.variable_attribute_value(var, attr)
        if attr.endswith("_PTR") or attr[:-1].endswith("_PTR_"):
            if master_cdf.has_variable(value):
                value = master_cdf.values(value, is_metadata_variable=True)
                if hasattr(value, 'tolist'):
                    attrs[attr] = value.tolist()
                else:
                    attrs[attr] = value
            else:
                log.warning(
                    f"{ISTP_NOT_COMPLIANT_W}: variable {var} has {attr} attribute which points to variable {value} which does not exist")
                attrs[attr] = value
        else:
            attrs[attr] = value
    return attrs


def _get_axis(master_cdf: Driver, cdf: Driver, axis_var: str, data_var: str):
    if cdf.has_variable(axis_var):
        if cdf.is_char(axis_var):
            if 'sig_digits' in master_cdf.variable_attributes(axis_var):  # cluster CSA trick :/
                return SupportDataVariable(name=axis_var, values=np.asarray(cdf.values(axis_var), dtype=float),
                                           attributes=_get_attributes(master_cdf, cdf, axis_var),
                                           is_nrv=cdf.is_nrv(axis_var)
                                           )
        return SupportDataVariable(name=axis_var, values=cdf.values(axis_var),
                                   attributes=_get_attributes(master_cdf, cdf, axis_var),
                                   is_nrv=cdf.is_nrv(axis_var)
                                   )
    else:
        log.warning(
            f"{ISTP_NOT_COMPLIANT_W}: trying to load {axis_var} as support data for {data_var} but it is absent from the file")
    return None


def _get_axes(master_cdf: Driver, cdf: Driver, var: str, data_shape):
    attrs = sorted(filter(lambda attr: DEPEND_REGEX.match(attr), master_cdf.variable_attributes(var)))
    unix_time_name = master_cdf.variable_attribute_value(var, "DEPEND_TIME")
    axes = list(
        map(lambda attr: _get_axis(master_cdf, cdf, master_cdf.variable_attribute_value(var, attr), var), attrs))
    if unix_time_name is not None and unix_time_name in master_cdf.variables():
        unix_time = _get_axis(master_cdf, cdf, unix_time_name, var)
        if len(unix_time) == data_shape[0] and len(axes[0].values) != data_shape[0]:
            unix_time.values = (unix_time.values * 1e9).astype('<M8[ns]')
            axes[0] = unix_time
            log.warning(
                f"{ISTP_NOT_COMPLIANT_W}: swapping DEPEND_0 with DEPEND_TIME for {var}, if you think this is a bug report it here: https://github.com/SciQLop/PyISTP/issues")
    return axes


def _get_labels(attributes) -> List[str]:
    if 'LABL_PTR_1' in attributes:
        return attributes['LABL_PTR_1']
    if 'LABLAXIS' in attributes:
        return [attributes['LABLAXIS']]


def _load_data_var(master_cdf: Driver, cdf: Driver, var: str) -> DataVariable or None:
    values = lambda: cdf.values(var)
    shape = cdf.shape(var)
    axes = _get_axes(master_cdf, cdf, var, shape)
    attributes = _get_attributes(master_cdf, cdf, var)
    labels = _get_labels(attributes)
    if len(axes) == 0:
        log.warning(f"{ISTP_NOT_COMPLIANT_W}: {var} was marked as data variable but it has 0 support variable")
        return None
    if None in axes or axes[0].values.shape[0] != shape[0]:
        return None
    return DataVariable(name=var, values=values, attributes=attributes, axes=axes, labels=labels)


class ISTPLoaderImpl:
    cdf: Optional[Driver] = None

    def __init__(self, file=None, buffer=None, master_file=None, master_buffer=None):
        if file is not None:
            log.debug(f"Loading {file}")
        self.cdf = current_driver(file or buffer)
        if master_file or master_buffer:
            self.master_cdf = current_driver(master_file or master_buffer)
        else:
            self.master_cdf = self.cdf
        self.data_variables = []
        self._update_data_vars_lis()

    def attributes(self):
        return self.master_cdf.attributes()

    def attribute(self, key):
        return self.master_cdf.attribute(key)

    def _update_data_vars_lis(self):
        if self.master_cdf:
            self.data_variables = []
            for var in self.master_cdf.variables():
                var_attrs = self.master_cdf.variable_attributes(var)
                var_type = self.master_cdf.variable_attribute_value(var, 'VAR_TYPE')
                param_type = (self.master_cdf.variable_attribute_value(var,
                                                                       'PARAMETER_TYPE') or "").lower()  # another cluster CSA crap
                if (var_type == 'data' or param_type == 'data') and not self.master_cdf.is_char(var):
                    self.data_variables.append(var)
            if len(self.data_variables) == 0:
                log.warning(f"{ISTP_NOT_COMPLIANT_W}: No data variable found, this is suspicious")

    def data_variable(self, var_name) -> DataVariable:
        return _load_data_var(self.master_cdf, self.cdf, var_name)
