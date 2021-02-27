from typing import Callable, Dict

from cardbuilder.data_sources import DataSource, Value


def default_stringify(value: Value) -> str:
    return value.to_output_string()


class ResolvedField:
    __slots__ = ['name', 'source_name', 'value']

    def __init__(self, name: str, source_name: str, value: str):
        self.name = name
        self.source_name = source_name
        self.value = value


class Field:
    def __init__(self, data_source: DataSource, source_field_name: str, target_field: str,
                 stringifier: Callable[[Value], str] = default_stringify,
                 optional=False):
        self.data_source = data_source
        self.source_field_name = source_field_name
        self.target_field_name = target_field
        self.stringifier = stringifier
        self.value = None
        self.optional = optional

    def resolve(self, data: Dict[str, Value]):
        result = data[self.source_field_name]
        result = self.stringifier(result)

        return ResolvedField(self.target_field_name, self.source_field_name, result)

    def blank(self):
        return ResolvedField(self.target_field_name, self.source_field_name, '')