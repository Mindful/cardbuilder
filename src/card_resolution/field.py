from typing import Callable, Union, List, Dict

from card_resolution.preprocessing import default_preprocessing
from data_sources import DataSource


class ResolvedField:
    __slots__ = ['name', 'source_name', 'value']

    def __init__(self, name: str, source_name: str, value: str):
        self.name = name
        self.source_name = source_name
        self.value = value


class Field:
    def __init__(self, data_source: DataSource, source_field_name: str, target_field: str,
                 preproc_func: Callable[[Union[str, List[str]]], str] = default_preprocessing,
                 optional=False):
        self.data_source = data_source
        self.source_field_name = source_field_name
        self.target_field_name = target_field
        self.preproc_func = preproc_func
        self.value = None
        self.optional = optional

    def resolve(self, data: Dict[str, Union[str, List[str]]]):
        result = data[self.source_field_name]
        if self.preproc_func is not None:
            result = self.preproc_func(result)

        return ResolvedField(self.target_field_name, self.source_field_name, result)

    def blank(self):
        return ResolvedField(self.target_field_name, self.source_field_name, '')