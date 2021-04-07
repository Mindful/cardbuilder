from abc import ABC, abstractmethod
from copy import copy
from typing import List, Any, Tuple, Optional

from cardbuilder.exceptions import CardBuilderUsageException


class Value(ABC):
    def __init__(self):
        self._data = None

    @abstractmethod
    def get_data(self) -> Any:
        return copy(self._data)


class SingleValue(Value):

    input_type = str

    def __init__(self, val: input_type):
        super(SingleValue, self).__init__()
        if not isinstance(val, self.input_type):
            raise CardBuilderUsageException('SingleValue received input of incorrect type')

        self._data = val

    def get_data(self) -> str:
        return copy(self._data)


class ListValue(Value):

    input_type = List[SingleValue.input_type]

    def __init__(self, value_list: input_type):
        super(ListValue, self).__init__()

        self._data = [SingleValue(x) for x in value_list]

    def get_data(self) -> List[SingleValue]:
        return copy(self._data)


class MultiListValue(Value):
    def __init__(self, list_header_tuples: List[Tuple[ListValue.input_type, Optional[SingleValue.input_type]]]):
        super(MultiListValue, self).__init__()

        self.data = [
            (ListValue(list_data), SingleValue(header_data) if header_data is not None else None)
            for list_data, header_data in list_header_tuples
        ]

    def get_data(self) -> List[Tuple[ListValue, Optional[SingleValue]]]:
        return copy(self._data)


