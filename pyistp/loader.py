from typing import List
from .data_variable import DataVariable


class ISTPLoader:

    def __init__(self, file=None, buffer=None, master_file=None, master_buffer=None):
        from ._impl import ISTPLoaderImpl
        self._impl = ISTPLoaderImpl(file=file, buffer=buffer, master_file=master_file, master_buffer=master_buffer)

    def attributes(self):
        return self._impl.attributes()

    def attribute(self, key):
        return self._impl.attribute(key)

    def data_variables(self) -> List[str]:
        return self._impl.data_variables

    def data_variable(self, var_name) -> DataVariable:
        return self._impl.data_variable(var_name)
