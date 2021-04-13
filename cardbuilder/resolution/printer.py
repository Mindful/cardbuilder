from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Optional, Callable, get_type_hints


from cardbuilder.common.util import dedup_by
from cardbuilder.exceptions import CardBuilderUsageException
from cardbuilder.lookup.value import SingleValue, ListValue, MultiListValue, MultiValue, Value


class Printer(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    def get_input_type(self) -> type:
        return next(val for key, val in get_type_hints(self.__call__).items() if key != 'return')


class WrappingPrinter(Printer, ABC):
    def __init__(self, printer: Printer):
        self._printer = printer

    def get_input_type(self) -> type:
        return self._printer.get_input_type()


class SingleValuePrinter(Printer):
    """The printer class for single values, like a word, part of speech, or single sentence definition."""

    value_format = '{value}'

    def __init__(self, format_string=value_format):
        if self.value_format not in format_string:
            raise CardBuilderUsageException('Format string {} does not include '.
                                            format(format_string) + self.value_format)
        self.format_string = format_string

    def __call__(self, value: SingleValue) -> str:
        return self.format_string.format(value=value.get_data())


class MultiValuePrinter(Printer):
    def __init__(self, value_printer: SingleValuePrinter = SingleValuePrinter(),
                 header_printer: SingleValuePrinter = SingleValuePrinter('{value}: '), join_string: str = ', ',
                 max_length: int = 10):
        self.value_printer = value_printer
        self.header_printer = header_printer
        self.join_string = join_string
        self.max_length = max_length

    def __call__(self, value: MultiValue) -> str:
        return self.join_string.join([
                                         (self.header_printer(
                                             header) if header is not None else '') + self.value_printer(value)
                                         for value, header in value.get_data()
                                     ][:self.max_length])


class ListValuePrinter(Printer):
    def __init__(self, single_value_printer: SingleValuePrinter = SingleValuePrinter(), join_string: str = ', ',
                 number_format_string: Optional[str] = None, sort_key: Optional[Callable[[SingleValue], int]] = None,
                 max_length: int = 10):

        self.single_value_printer = single_value_printer
        self.join_string = join_string
        self.num_fstring = number_format_string
        self.sort_key = sort_key
        self.max_length = max_length

        if self.num_fstring is not None:
            if '{number}' not in self.num_fstring:
                raise CardBuilderUsageException('Number format string must include "{number}"')

    def __call__(self, value: ListValue) -> str:
        data = (value.get_data() if self.sort_key is None else sorted(value.get_data(),
                                                                      key=self.sort_key))[:self.max_length]

        return self.join_string.join([
            (self.num_fstring.format(number=idx) if self.num_fstring is not None else '') + self.single_value_printer(
                val)
            for idx, val in enumerate(data)
        ])


class MultiListValuePrinter(Printer):
    def __init__(self, list_printer: ListValuePrinter = ListValuePrinter(number_format_string='{number}. ',
                                                            single_value_printer=SingleValuePrinter('{value}\n')),
                 header_printer: Optional[SingleValuePrinter] = SingleValuePrinter('{value}\n'),
                 join_string: str = '\n\n', group_by_header: bool = True, max_length: int = 10):
        self.list_printer = list_printer
        self.header_printer = header_printer
        self.join_string = join_string
        self.group_by_header = group_by_header
        self.max_length = max_length

    def __call__(self, value: MultiListValue) -> str:
        data = value.get_data()

        if self.group_by_header:
            grouped_data = OrderedDict()
            for data_list, header in data:
                if header not in grouped_data:
                    grouped_data[header] = list()
                grouped_data[header].extend(x.get_data() for x in data_list.get_data())

            data = list((ListValue(val), key) for key, val in grouped_data.items())

        data = data[:self.max_length]

        return self.join_string.join([
            (self.header_printer(header) if header is not None else '') + self.list_printer(data_list)
            for data_list, header in data
        ])


class TatoebaPrinter(MultiValuePrinter):

    def __init__(self, **kwargs):
        if 'header_printer' not in kwargs:
            kwargs['header_printer'] = SingleValuePrinter('{value}\n')
        if 'join_string' not in kwargs:
            kwargs['join_string'] = '\n\n'
        super(TatoebaPrinter, self).__init__(**kwargs)

    def __call__(self, value: MultiValue):
        deduped_value = MultiValue([(x.get_data(), y.get_data()) for x, y in
                                   dedup_by(dedup_by(value.get_data(), lambda x: x[0]), lambda x: x[1])])
        return super().__call__(deduped_value)


class DefaultPrinter(Printer):
    def __call__(self, value: Value):
        return {
            SingleValue: SingleValuePrinter(),
            MultiValue: MultiValuePrinter(),
            ListValue: ListValuePrinter(),
            MultiListValue: MultiListValuePrinter()
        }[type(value)](value)
