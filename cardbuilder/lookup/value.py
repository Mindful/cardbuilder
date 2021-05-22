from abc import ABC, abstractmethod
from copy import copy
from typing import List, Tuple, Optional, Sequence

from cardbuilder.exceptions import CardBuilderUsageException


class Value(ABC):
    """Abstract base class for all values."""
    def __init__(self):
        self._data = None

    @abstractmethod
    def get_data(self) -> Sequence:
        raise NotImplementedError()

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def __eq__(self, other):
        return isinstance(other, type(self)) and self._data == other._data

    def __hash__(self):
        return hash(self._data)

    def __repr__(self):
        return type(self).__name__ + ':' + repr(self.get_data())


class SingleValue(Value):
    """Represents a single value, such as a part of speech, IPA for a word, or a word itself."""

    input_type = str

    def __init__(self, val: input_type):
        super(SingleValue, self).__init__()
        if not isinstance(val, self.input_type):
            raise CardBuilderUsageException('SingleValue received input of incorrect type ({})'.format(
                type(val).__name__))

        self._data = val

    def get_data(self) -> str:
        return copy(self._data)


class MultiValue(Value):
    """Represents multiple values, each optionally paired with a header value. Useful for capturing pairs or mappings
    of values, such as words where pronunciation is different based on the part of speech. For straightforward lists
    of values, use ListValue"""
    def __init__(self, list_header_tuples: List[Tuple[SingleValue.input_type, Optional[SingleValue.input_type]]]):
        super(MultiValue, self).__init__()

        value_data = [
            (SingleValue(data), SingleValue(header_data) if header_data is not None else None)
            for data, header_data in list_header_tuples
        ]

        self._data = [(content, header) for content, header in value_data if not content.is_empty()]

    def get_data(self) -> List[Tuple[SingleValue, Optional[SingleValue]]]:
        return copy(self._data)


class ListValue(Value):
    """
    Represents a list of values, such as multiple possible parts of speech or multiple definitions.
    """
    input_type = List[SingleValue.input_type]

    def __init__(self, value_list: input_type):
        super(ListValue, self).__init__()

        value_data = [SingleValue(x) for x in value_list]
        self._data = [v for v in value_data if not v.is_empty()]

    def get_data(self) -> List[SingleValue]:
        return copy(self._data)


class MultiListValue(Value):
    """
    Represents multiple lists of values, each optionally paired with a header value. Most commonly used in cases where
    a word has multiple possible parts of speech, and there is a list of values (such as definitions) associated with
    each part of speech.
    """
    def __init__(self, list_header_tuples: List[Tuple[ListValue.input_type, Optional[SingleValue.input_type]]]):
        super(MultiListValue, self).__init__()

        value_data = [
            (ListValue(list_data), SingleValue(header_data) if header_data is not None else None)
            for list_data, header_data in list_header_tuples
        ]

        self._data = [(content, header) for content, header in value_data if not content.is_empty()]

    def get_data(self) -> List[Tuple[ListValue, Optional[SingleValue]]]:
        return copy(self._data)


class LinksValue(Value):
    """
    Represents a link in a dictionary to another word. Useful only in very specific cases.
    """
    def __init__(self, link_data: List['LookupData']):
        self._data = link_data

    def get_data(self) -> List['LookupData']:
        return self._data






