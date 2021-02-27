from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Tuple, Optional


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

    def to_output_string(self, value_format_string: str = '{}\n') -> str:
        return ''.join([value_format_string.format(val) for val in self.val_list])


class DefinitionsWithPOSValue(Value):
    def __init__(self, definitions_with_pos: List[Tuple[List[str], Optional[str]]]):
        seen_definitions = set()
        # simple dedupe
        self.definitions_with_pos = []
        for definitions, pos in definitions_with_pos:
            deduped_definitions = [dfn for dfn in definitions if
                                   not (any(dfn.lower() in seen_def for seen_def in seen_definitions) or
                                        seen_definitions.add(dfn.lower()))]

            if len(deduped_definitions) > 0:
                self.definitions_with_pos.append((deduped_definitions, pos))

    def to_output_string(self, group_by_pos: bool = True, number: bool = True, definition_format_string: str = '{}\n',
                         pos_group_format_string: str = '({})\n{}', number_format_string: str = '{}. {}') -> str:

        if group_by_pos:
            definitions_by_pos = defaultdict(list)
            for definitions, pos in self.definitions_with_pos:
                definitions_by_pos[pos].extend(definitions)

            return ''.join([
                pos_group_format_string.format(pos, ''.join(
                    [number_format_string.format(index, definition_format_string.format(definition)) if number
                     else definition_format_string.format(definition)
                     for index, definition in enumerate(definitions_by_pos[pos])]))
                for pos in definitions_by_pos.keys()
            ])
        else:
            all_definitions = []
            for definitions in self.definitions_with_pos:
                all_definitions.extend(definitions)

            return ''.join(number_format_string.format(index, definition_format_string.format(definition)) if number
                           else definition_format_string.format(definition)
                           for index, definition in enumerate(all_definitions))
