from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Tuple, Optional, Any, Callable

from cardbuilder.exceptions import CardBuilderException
from cardbuilder.common.fieldnames import Fieldname


def _format_string_list(strings: List[str], value_format_string: str, join_values_with: str, number: bool,
                        number_format_string: str, sort_key: Callable[[str], int], max_vals: int) -> str:
    if sort_key is not None:
        strings = sorted(strings, key=sort_key)
    return join_values_with.join([
        number_format_string.format(index + 1, value_format_string.format(val)) if number
        else value_format_string.format(val) for
        index, val in enumerate(strings[:max_vals])
    ])


class Value(ABC):
    @abstractmethod
    def to_output_string(self) -> str:
        raise NotImplementedError()

    def __repr__(self):
        return str(self.__dict__)


class ExternalMediaValue(Value):
    #TODO: use this for MerriamWebster, and potentially give it its own sqlite3 db table for caching
    # have special logic in resolvers to handle media - also potentially include media type (image vs sound, etc.)
    def __init__(self, val: str):
        self.val = val

    def to_output_string(self, **kwargs) -> str:
        return self.val


class StringValue(Value):
    def __init__(self, val: str):
        self.val = val

    def to_output_string(self, **kwargs) -> str:
        return self.val


class ListConvertibleValue(Value, ABC):
    @abstractmethod
    def to_list(self) -> List[str]:
        raise NotImplementedError()

    def __iter__(self):
        return self.to_list()


class StringListValue(ListConvertibleValue):
    def __init__(self, val_list: List[str]):
        # TODO: optional deuping
        self.val_list = val_list

    def to_output_string(self, value_format_string: str = '{}', join_vals_with: str = '\n', number: bool = False,
                         number_format_string: str = '{}. {}', sort_key: Callable[[str], int] = None,
                         max_vals: int = 100) -> str:
        return _format_string_list(self.val_list, value_format_string, join_vals_with,
                                   number, number_format_string, sort_key, max_vals)

    def to_list(self) -> List[str]:
        return self.val_list


class StringsWithPosValue(ListConvertibleValue):
    def __init__(self, values_with_pos: List[Tuple[str, str]]):
        self.values_with_pos = values_with_pos

    def to_list(self) -> List[str]:
        return [val for val, pos in self.values_with_pos]

    def to_output_string(self, group_by_pos: bool = True, value_format_string: str = '{}\n',
                         pos_group_format_string: str = '({}) {}') -> str:
        return ''.join([
            pos_group_format_string.format(pos, value_format_string.format(val)) if group_by_pos
            else value_format_string.format(val) for
            val, pos in self.values_with_pos
        ])


# This class holds lists of values with associated parts of speech. Lists of tuples were chosen over a dictionary
# because there are sometimes duplicates
class StringListsWithPOSValue(ListConvertibleValue):
    def __init__(self, values_with_pos: List[Tuple[List[str], Optional[str]]]):
        # TODO: move deduping logic into to_output_string() and make it optional
        seen_values = set()
        # simple dedupe
        self.values_with_pos = []
        for values, pos in values_with_pos:
            deduped_values = [val for val in values if
                              not (any(val.lower() in seen_val for seen_val in seen_values) or
                                   seen_values.add(val.lower()))]

            if len(deduped_values) > 0:
                self.values_with_pos.append((deduped_values, pos))

    def to_list(self) -> List[str]:
        return [val for val_list, pos in self.values_with_pos for val in val_list]

    def to_output_string(self, group_by_pos: bool = True, number: bool = False, value_format_string: str = '{}',
                         pos_group_format_string: str = '\n({})\n{}', number_format_string: str = '{}. {}',
                         sort_key: Callable[[str], int] = None, join_vals_with: str = '\n', max_vals: int = 100,
                         max_pos: int = 100) -> str:

        if group_by_pos:
            values_by_pos = defaultdict(list)
            for values, pos in self.values_with_pos:
                if len(values_by_pos) < max_pos or pos in values_by_pos:
                    values_by_pos[pos].extend(values)

            return ''.join([
                pos_group_format_string.format(pos, _format_string_list(values_by_pos[pos], value_format_string,
                                                                        join_vals_with, number, number_format_string,
                                                                        sort_key, max_vals))
                for pos in values_by_pos.keys()
            ])
        else:
            all_values = []
            for values in self.values_with_pos:
                all_values.extend(values)

            return _format_string_list(all_values, value_format_string, join_vals_with,
                                       number, number_format_string, sort_key, max_vals)


# This class holds data for more than one part of speech, but by default only outputs for its primary part of speech
class StringListsWithPrimaryPOSValue(StringListsWithPOSValue):
    def __init__(self, values_with_pos: List[Tuple[List[str], Optional[str]]], primary_pos: str):
        super().__init__(values_with_pos)
        self.primary_pos = primary_pos
        if not any(pos == self.primary_pos for defs, pos in self.values_with_pos):
            raise CardBuilderException("Cannot cannot a value whose primary part of speech "
                                       "is not present in values")

    def get_primary_list(self) -> List[str]:
        return next(vals for vals, pos in self.values_with_pos if pos == self.primary_pos)

    def to_list(self) -> List[str]:
        return self.get_primary_list()

    def to_output_string(self, number: bool = False, value_format_string: str = '{}', join_vals_with: str = '\n',
                         number_format_string: str = '{}. {}', sort_key: Callable[[str], int] = None,
                         max_vals: int = 100) -> str:
        return _format_string_list(self.get_primary_list(), value_format_string, join_vals_with,
                                   number, number_format_string, sort_key, max_vals)


# Class for making raw data (such as API call responses) available. No gaurantees are made about the structure of
# this data
class RawDataValue(Value):
    def __init__(self, data: Any):
        self.data = data

    def to_output_string(self):
        raise CardBuilderException('Raw data cannot be used directly for output')


class LinksValue(Value):
    def __init__(self, data_list: List['LookupData']):  # if we actually import LookupData it creates a cycle
        self.data_list = data_list

    def to_output_string(self, description_string: str = 'See also: ', join_words_with: str = ', ') -> str:
        return '{} {}'.format(description_string, join_words_with.join(data[Fieldname.WORD].to_output_string()
                                                                       for data in self.data_list))
