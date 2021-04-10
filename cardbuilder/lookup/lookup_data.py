from abc import ABC, abstractmethod
from copy import copy
from typing import Dict, Optional

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.lookup.value import Value, SingleValue
from cardbuilder.exceptions import CardBuilderUsageException
from cardbuilder.input.word import Word


class LookupData(ABC):
    """An empty base class for all word data so that a common type exists"""

    @classmethod
    def fields(cls) -> Dict[Fieldname, type]:
        raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, fieldname: Fieldname) -> Optional[Value]:
        raise NotImplementedError()

    @abstractmethod
    def __init__(self, word: Word, found_form: str, raw_data: str, data: Dict[Fieldname, Value]):
        # setting these in the base class makes IDE code completion aware of them
        self.word = word
        self.found_form = found_form
        self._data = data
        self._raw_data = raw_data

        raise NotImplementedError()

    def get_raw_content(self) -> str:
        return copy(self._raw_data)

    def get_data(self) -> Dict[Fieldname, Value]:
        return copy(self._data)

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


def outputs(output_spec: Dict[Fieldname, type]):
    def decorator(clazz):
        for key in output_spec:
            if not isinstance(key, Fieldname):
                raise CardBuilderUsageException('output spec for data source must be dict of Fieldname -> Value type')

        for value in output_spec.values():
            if not isinstance(value, type) and issubclass(value, Value):
                raise CardBuilderUsageException('output spec for data source must be dict of Fieldname -> Value type')

        class GeneratedLookupData(LookupData):
            _fields = output_spec

            @classmethod
            def fields(cls) -> Dict[Fieldname, type]:
                return cls._fields

            def __setitem__(self, key: Fieldname, value: Value):
                if key not in self._fields:
                    raise CardBuilderUsageException('{} can only set its designated fields, not {}'.format(
                        type(self).__name__, key.name
                    ))
                else:
                    self._data[key] = value

            def __getitem__(self, key: Fieldname) -> Optional[Value]:
                if key == Fieldname.WORD:
                    return SingleValue(self.word.input_form)
                elif key == Fieldname.FOUND_FORM:
                    return SingleValue(self.found_form)

                if key not in self.fields():
                    raise CardBuilderUsageException(
                        '{} cannot contain the field {}'.format(type(self).__name__, key.name))

                return self._data.get(key, None)

            def __contains__(self, fieldname: Fieldname):
                if fieldname in {Fieldname.WORD, Fieldname.FOUND_FORM}:
                    return True
                else:
                    return fieldname in self._data

            def __init__(self, word: Word, found_form: str, raw_data: str, data: Dict[Fieldname, Value]):
                self.word = word
                self.found_form = found_form
                self._data = data
                self._raw_data = raw_data

                for fieldname, value in data.items():
                    if fieldname not in self._fields:
                        raise CardBuilderUsageException('{} cannot contain the field {}'.format(type(self).__name__,
                                                                                                fieldname.name))
                    if not isinstance(value, self._fields[fieldname]):
                        raise CardBuilderUsageException('input for field {} did was not of the promised type {}'.format(
                            fieldname, self._fields[fieldname].__name__
                        ))

        GeneratedLookupData.__name__ = clazz.__name__ + 'LookupData'

        clazz.lookup_data_type = GeneratedLookupData

        return clazz
    return decorator


