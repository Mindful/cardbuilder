from typing import Union, List, Optional

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
                 target_field: str, printer: Printer = DefaultPrinter(), required=False):

        if isinstance(data_source, DataSource):
            self.data_sources = [data_source]
        else:
            self.data_sources = data_source

        if source_field_name == Fieldname.WORD:
            required = True  # we always need to be able to find the word, at least

        for data_source in self.data_sources:
            if source_field_name not in LookupData.standard_fields():
                returned_fields = data_source.lookup_data_type.fields()
                if source_field_name not in returned_fields:
                    raise CardBuilderUsageException('field {} cannot be returned by data source {}'.format(
                        source_field_name, type(data_source).__name__))

                returned_value_type = returned_fields[source_field_name]
                if not issubclass(returned_value_type, printer.get_input_type()):
                    raise CardBuilderUsageException('printer {} cannot print {}, which {} returns for field {}'.format(
                        type(printer).__name__, returned_value_type.__name__, type(data_source).__name__, source_field_name
                    ))

        self.source_field_name = source_field_name
        self.target_field_name = target_field
        self.printer = printer
        self.value = None
        self.required = required

    def resolve(self, data_list: List[LookupData]) -> Optional[ResolvedField]:
        for data in data_list:
            if self.source_field_name in data:
                result = data[self.source_field_name]
                result = self.printer(result)
                return ResolvedField(self.target_field_name, self.source_field_name, result)

        # we couldn't find the data we were looking for; return a blank card if it's optional otherwise fail
        if not self.required:
            return self.blank()
        else:
            return None

    def blank(self) -> ResolvedField:
        return ResolvedField(self.target_field_name, self.source_field_name, '')
