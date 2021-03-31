from abc import ABC, abstractmethod
from typing import List, FrozenSet, Dict, Optional

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.lookup.value import Value, StringValue
from cardbuilder.exceptions import CardBuilderUsageException
from cardbuilder.input.word import Word


class LookupData(ABC):
    """An empty base class for all word data so that a common type exists"""

    @classmethod
    def required_fields(cls) -> FrozenSet[Fieldname]:
        raise NotImplementedError()

    @classmethod
    def optional_fields(cls) -> FrozenSet[Fieldname]:
        raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, fieldname: Fieldname) -> Optional[Value]:
        raise NotImplementedError()

    @abstractmethod
    def __init__(self, word: Word, found_form: str, data: Dict[Fieldname, Value]):
        raise NotImplementedError()


def lookup_data_type_factory(name: str, input_required_fields: List[Fieldname],
                             input_optional_fields: List[Fieldname]) -> type:

    class GeneratedLookupData(LookupData):
        _required_fields = frozenset(input_required_fields)
        _optional_fields = frozenset(input_optional_fields)

        if len(_required_fields & _optional_fields) > 0:
            raise CardBuilderUsageException('{} WordData type cannot contain a field as both optional and required'.
                                            format(name))

        @classmethod
        def required_fields(cls) -> FrozenSet[Fieldname]:
            return cls._required_fields

        @classmethod
        def optional_fields(cls) -> FrozenSet[Fieldname]:
            return cls._optional_fields

        def __getitem__(self, fieldname: Fieldname) -> Optional[Value]:
            if fieldname == Fieldname.WORD:
                return StringValue(self.word.input_form)
            elif fieldname == Fieldname.FOUND_FORM:
                return StringValue(self.found_form)

            if fieldname not in (self._required_fields or self._optional_fields):
                raise CardBuilderUsageException('{} cannot contain the field {}'.format(type(self).__name__,
                                                                                        fieldname.name))

            return self.data.get(fieldname, None)

        def __init__(self, word: Word, found_form: str, data: Dict[Fieldname, Value]):
            self.word = word
            self.found_form = found_form
            for fieldname in self._required_fields:
                if fieldname not in data:
                    raise CardBuilderUsageException('{} must contain the field {}'.format(type(self).__name__,
                                                                                          fieldname.name))

            for fieldname in data.keys():
                if fieldname not in (self._required_fields or self._optional_fields):
                    raise CardBuilderUsageException('{} cannot contain the field {}'.format(type(self).__name__,
                                                                                            fieldname.name))

            self.data = data

    GeneratedLookupData.__name__ = name

    return GeneratedLookupData
