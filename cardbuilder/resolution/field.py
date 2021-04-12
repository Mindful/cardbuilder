from typing import Union, List, Optional, get_type_hints

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.exceptions import CardBuilderUsageException
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.lookup_data import LookupData
from cardbuilder.resolution.printer import Printer, DefaultPrinter


class ResolvedField:
    __slots__ = ['name', 'source_name', 'value']

    def __init__(self, name: str, source_name: Fieldname, value: str):
        self.name = name
        self.source_name = source_name
        self.value = value


class Field:
    def __init__(self, data_source: Union[DataSource, List[DataSource]], source_field_name: Fieldname,
                 target_field: str, printer: Printer = DefaultPrinter(), optional=False):

        if isinstance(data_source, DataSource):
            self.data_sources = [data_source]
        else:
            self.data_sources = data_source

        for data_source in self.data_sources:
            returned_fields = data_source.lookup_data_type.fields()
            if source_field_name not in returned_fields and source_field_name not in LookupData.standard_fields():
                raise CardBuilderUsageException('field {} cannot be returned by data source {}'.format(
                    source_field_name, type(data_source).__name__))

            #TODO: validate the type of the printer somehow (I.E. that it takes the type of value returned by the
            # data source)

        self.source_field_name = source_field_name
        self.target_field_name = target_field
        self.printer = printer
        self.value = None
        self.optional = optional

    def resolve(self, data_list: List[LookupData]) -> Optional[ResolvedField]:
        for data in data_list:
            if self.source_field_name in data:
                result = data[self.source_field_name]
                result = self.printer(result)
                return ResolvedField(self.target_field_name, self.source_field_name, result)

        # we couldn't find the data we were looking for; return a blank card if it's optional otherwise fail
        if self.optional:
            return self.blank()
        else:
            return None

    def blank(self) -> ResolvedField:
        return ResolvedField(self.target_field_name, self.source_field_name, '')
