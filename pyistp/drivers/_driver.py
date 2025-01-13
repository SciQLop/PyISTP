from typing import Protocol, runtime_checkable, List, AnyStr, Collection, Any


class Driver(Protocol):

    def attributes(self) -> List[AnyStr]:
        ...

    def attribute(self, key: AnyStr):
        ...

    def data_variables(self) -> List[AnyStr]:
        ...

    def data_variable(self, var_name: AnyStr):
        ...

    def variable_attribute_value(self, var: AnyStr, attr: AnyStr) -> Any:
        ...

    def variable_attributes(self, var: AnyStr) -> List[AnyStr]:
        ...

    def values(self, var: AnyStr, is_metadata_variable: bool = False) -> Collection:
        ...

    def shape(self, var: AnyStr) -> Collection[int]:
        ...

    def variables(self) -> List[AnyStr]:
        ...

    def has_variable(self, name: str) -> bool:
        ...

    def is_char(self, var: str) -> bool:
        ...

    def is_nrv(self, var: str) -> bool:
        ...
