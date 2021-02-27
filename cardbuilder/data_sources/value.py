from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Tuple, Optional, Any

from cardbuilder import CardBuilderException


def _format_string_list(strings: List[str], value_format_string: str, number: bool, number_format_string: str) -> str:
    return ''.join([
        number_format_string.format(index, value_format_string.format(val)) if number
        else value_format_string.format(val) for
        index, val in enumerate(strings)
    ])


class Value(ABC):
    @abstractmethod
    def to_output_string(self):
        raise NotImplementedError()

    def __repr__(self):
        return str(self.__dict__)


class StringValue(Value):
    def __init__(self, val: str):
        self.val = val

    def to_output_string(self) -> str:
        return self.val


class StringListValue(Value):
    def __init__(self, val_list: List[str]):
        self.val_list = val_list

    def to_output_string(self, value_format_string: str = '{}\n', number: bool = False,
                         number_format_string: str = '{}. {}') -> str:
        return _format_string_list(self.val_list, value_format_string, number, number_format_string)


# This class holds lists of values with associated parts of speech. Lists of tuples were chosen over a dictionary
# because there are sometimes duplicates
class StringListsWithPOSValue(Value):
    def __init__(self, values_with_pos: List[Tuple[List[str], Optional[str]]]):
        seen_values = set()
        # simple dedupe
        self.values_with_pos = []
        for values, pos in values_with_pos:
            deduped_values = [val for val in values if
                              not (any(val.lower() in seen_val for seen_val in seen_values) or
                                   seen_values.add(val.lower()))]

            if len(deduped_values) > 0:
                self.values_with_pos.append((deduped_values, pos))

    def to_output_string(self, group_by_pos: bool = True, number: bool = True, value_format_string: str = '{}\n',
                         pos_group_format_string: str = '({})\n{}', number_format_string: str = '{}. {}') -> str:

        if group_by_pos:
            values_by_pos = defaultdict(list)
            for values, pos in self.values_with_pos:
                values_by_pos[pos].extend(values)

            return ''.join([
                pos_group_format_string.format(pos, _format_string_list(values_by_pos[pos], value_format_string,
                                                    number, number_format_string)) for pos in values_by_pos.keys()
            ])
        else:
            all_values = []
            for values in self.values_with_pos:
                all_values.extend(values)

            return _format_string_list(all_values, value_format_string, number, number_format_string)


# This class holds data for more than one part of speech, but by default only outputs for its primary part of speech
class StringListsWithPrimaryPOSValue(StringListsWithPOSValue):
    def __init__(self, values_with_pos: List[Tuple[List[str], Optional[str]]], primary_pos: str):
        super().__init__(values_with_pos)
        self.primary_pos = primary_pos
        if not any(pos == self.primary_pos for defs, pos in self.values_with_pos):
            raise CardBuilderException("Cannot cannot a value whose primary part of speech "
                                       "is not present in values")

    def to_output_string(self, number: bool = True, value_format_string: str = '{}\n',
                         number_format_string: str = '{}. {}') -> str:
        primary_list = next(values for values, pos in self.values_with_pos
                            if pos == self.primary_pos)

        return _format_string_list(primary_list, value_format_string, number, number_format_string)

# Class for making raw data (such as API call responses) available. No gaurantees are made about the structure of
# this data
class RawDataValue(Value):
    def __init__(self, data: Any):
        self.data = data

    def to_output_string(self):
        raise CardBuilderException('Raw data cannot be used directly for output')

