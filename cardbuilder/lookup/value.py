from abc import ABC, abstractmethod
from copy import copy
from enum import Enum
from typing import List, Tuple, Optional, Sequence, Any, Union

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


def to_value(input_data: Any) -> Value:
    if isinstance(input_data, Value):
        return input_data
    if isinstance(input_data, SingleValue.input_type):
        return SingleValue(input_data)
    else:
        raise CardBuilderUsageException(f'Cannot convert given input data {input_data} into a Value class')
    #TODO: extend to other value types and in effect have an AutoValue method?


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


value_unit_type = Union[SingleValue.input_type, str]


class PitchAccentValue(SingleValue):
    """Represents pitch value for an associated word"""

    class PitchAccent(Enum):
        HIGH = 'h'
        LOW = 'l'
        DROP = 'd'

    def __init__(self, pitch_accent: Union[str, List[PitchAccent]], word: str):
        if isinstance(pitch_accent, list):
            super(PitchAccentValue, self).__init__(''.join(p.value for p in pitch_accent))
        else:
            super(PitchAccentValue, self).__init__(pitch_accent)
        self.word = word

        if not isinstance(word, str) or len(pitch_accent) != len(word):
            raise CardBuilderUsageException('PitchAccentValue word value must be a string of the same length as the'
                                            'pitch accent list')


class MultiValue(Value):
    """Represents multiple values, each optionally paired with a header value. Useful for capturing pairs or mappings
    of values, such as words where pronunciation is different based on the part of speech. For straightforward lists
    of values, use ListValue"""
    def __init__(self, list_header_tuples: List[Tuple[value_unit_type, Optional[value_unit_type]]]):
        super(MultiValue, self).__init__()

        value_data = [
            (to_value(data), to_value(header_data) if header_data is not None else None)
            for data, header_data in list_header_tuples
        ]

        self._data = [(content, header) for content, header in value_data if not content.is_empty()]

    def get_data(self) -> List[Tuple[SingleValue, Optional[SingleValue]]]:
        return copy(self._data)


class ListValue(Value):
    """
    Represents a list of values, such as multiple possible parts of speech or multiple definitions.
    """
    input_type = List[value_unit_type]

    def __init__(self, value_list: input_type):
        super(ListValue, self).__init__()

        value_data = [to_value(x) for x in value_list]
        self._data = [v for v in value_data if not v.is_empty()]

    def get_data(self) -> List[SingleValue]:
        return copy(self._data)


class MultiListValue(Value):
    """
    Represents multiple lists of values, each optionally paired with a header value. Most commonly used in cases where
    a word has multiple possible parts of speech, and there is a list of values (such as definitions) associated with
    each part of speech.
    """
    def __init__(self, list_header_tuples: List[Tuple[ListValue.input_type, Optional[value_unit_type]]]):
        super(MultiListValue, self).__init__()

        value_data = [
            (ListValue(list_data), to_value(header_data) if header_data is not None else None)
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






