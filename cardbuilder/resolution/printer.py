# - StringValuePrinter takes a format string into which the value is placed
# 	- validate there's something formattable in the format string (somewhere to put the value)
# - ListValuePrinter takes a StringValuePrinter for each element, and
# 	- number_format_string: if provided, every StringValue is preceded by this formatted with a number
# 	- join_string: defaults to \n or ',', used to join the StringValue outputs
# 	- sort_key: callable from StringValue to int (for ordering)
# 	- truncate: int for max length
# - MultiListValuePrinter takes a ListvaluePrinter and a SingleValuePrinter for headers
# 	- show header: bool, whether to show headers or not
# 	- group_by_header: bool, whether to group by the headers
# 	- group_format_string: format string that includes a section for the header and each list, requiring at least the list to be present
from abc import ABC, abstractmethod
from typing import Optional, Callable

from cardbuilder.exceptions import CardBuilderUsageException
from cardbuilder.lookup.new_value import SingleValue, ListValue


class Printer(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError()


class SingleValuePrinter(Printer):

    value_format = '{value}'

    def __init__(self, format_string=value_format):
        if self.value_format not in format_string:
            raise CardBuilderUsageException('Format string {} does not include '.
                                            format(format_string)+self.value_format)
        self.format_string = format_string

    def __call__(self, value: SingleValue):
        return self.format_string.format(value=value.get_data())


class ListValuePrinter(Printer):
    def __init__(self, single_value_printer: SingleValuePrinter, join_string: str = ',',
                 number_format_string: Optional[str] = None, sort_key: Optional[Callable[[SingleValue], int]] = None,
                 max_length: int = 10):

        self.single_value_printer = single_value_printer
        self.join_string = join_string
        self.number_format_string = number_format_string
        self.sort_key = sort_key
        self.max_length = max_length

    def __call__(self, value: ListValue):
        pass #TODO