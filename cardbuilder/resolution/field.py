from typing import Callable, Dict, Union, List, Optional

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.lookup import DataSource
from cardbuilder.lookup.value import Value
from cardbuilder.lookup.lookup_data import LookupData


def default_stringify(value: Value) -> str:
    return value.to_output_string()


class ResolvedField:
    __slots__ = ['name', 'source_name', 'value']

    def __init__(self, name: str, source_name: Fieldname, value: str):
        self.name = name
        self.source_name = source_name
        self.value = value


class Field:
    def __init__(self, data_source: Union[DataSource, List[DataSource]], source_field_name: Fieldname,
                 target_field: str, stringifier: Callable[[Value], str] = default_stringify, optional=False):

        if isinstance(data_source, DataSource):
            self.data_sources = [data_source]
        else:
            self.data_sources = data_source

        self.source_field_name = source_field_name
        self.target_field_name = target_field
        self.stringifier = stringifier
        self.value = None
        self.optional = optional

    def resolve(self, data_list: List[LookupData]) -> Optional[ResolvedField]:
        for data in data_list:
            if self.source_field_name in data:
                result = data[self.source_field_name]
                result = self.stringifier(result)
                return ResolvedField(self.target_field_name, self.source_field_name, result)

        # we couldn't find the data we were looking for; return a blank card if it's optional otherwise fail
        if self.optional:
            return self.blank()
        else:
            return None

    def blank(self) -> ResolvedField:
        return ResolvedField(self.target_field_name, self.source_field_name, '')
