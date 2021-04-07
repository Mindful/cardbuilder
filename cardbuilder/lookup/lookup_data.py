from abc import ABC, abstractmethod
from copy import copy
from typing import List, Dict, Optional, Set, FrozenSet

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.lookup.value import Value, StringValue
from cardbuilder.exceptions import CardBuilderUsageException
from cardbuilder.input.word import Word


class LookupData(ABC):
    """An empty base class for all word data so that a common type exists"""

    @classmethod
    def fields(cls) -> Set[Fieldname]:
        raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, fieldname: Fieldname) -> Optional[Value]:
        raise NotImplementedError()

    @abstractmethod
    def __init__(self, word: Word, found_form: str, data: Dict[Fieldname, Value]):
        # setting these in the base class makes IDE code completion aware of them
        self.word = word
        self.found_form = found_form
        self._data = data

        raise NotImplementedError()

    @abstractmethod
    def get_data(self) -> Dict[Fieldname, Value]:
        raise NotImplementedError()

    @abstractmethod
    def __setitem__(self, key: Fieldname, value: Value):
        raise NotImplementedError()

    @abstractmethod
    def __contains__(self, key: Fieldname):
        raise NotImplementedError()

    def __repr__(self):
        repr_dict = {
            key.name: val for key, val in self._data.items()
        }
        return '<Word: {}, form: {}, data: {}>'.format(self.word, self.found_form, self._data)


def lookup_data_type_factory(name: str, input_fields: Set[Fieldname]) -> type:

    class GeneratedLookupData(LookupData):
        _fields = frozenset(input_fields)

        @classmethod
        def fields(cls) -> FrozenSet[Fieldname]:
            return cls._fields

        def get_data(self) -> Dict[Fieldname, Value]:
            return copy(self._data)

        def __setitem__(self, key: Fieldname, value: Value):
            if key not in self._fields:
                raise CardBuilderUsageException('{} can only set its designated fields, not {}'.format(
                    type(self).__name__, key.name
                ))
            else:
                self._data[key] = value

        def __getitem__(self, key: Fieldname) -> Optional[Value]:
            if key == Fieldname.WORD:
                return StringValue(self.word.input_form)
            elif key == Fieldname.FOUND_FORM:
                return StringValue(self.found_form)

            if key not in self.fields():
                raise CardBuilderUsageException('{} cannot contain the field {}'.format(type(self).__name__, key.name))

            return self._data.get(key, None)

        def __contains__(self, fieldname: Fieldname):
            if fieldname in {Fieldname.WORD, Fieldname.FOUND_FORM}:
                return True
            else:
                return fieldname in self._data

        def __init__(self, word: Word, found_form: str, data: Dict[Fieldname, Value]):
            self.word = word
            self.found_form = found_form
            self._data = data

            for fieldname in data.keys():
                if fieldname not in self.fields():
                    raise CardBuilderUsageException('{} cannot contain the field {}'.format(type(self).__name__,
                                                                                            fieldname.name))

    GeneratedLookupData.__name__ = name

    return GeneratedLookupData
