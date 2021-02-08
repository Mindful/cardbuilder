from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Callable, Union, List, Dict

from tqdm import tqdm

from data_sources import DataSource


def default_preprocessing(value: Union[str, List[str]]) -> str:
    if isinstance(value, list):
        return '\n'.join(value)
    elif isinstance(value, str):
        return value
    else:
        raise RuntimeError('Field value must be list of strings or string')


class ResolvedField:
    __slots__ = ['name', 'source_name', 'value']

    def __init__(self, name: str, source_name: str, value: str):
        self.name = name
        self.source_name = source_name
        self.value = value


class Field:
    def __init__(self, data_source: DataSource, source_field_name: str, target_field: str,
                 preproc_func: Callable[[Union[str, List[str]]], str] = default_preprocessing):
        self.data_source = data_source
        self.source_field_name = source_field_name
        self.target_field_name = target_field
        self.preproc_func = preproc_func
        self.value = None

    def resolve(self, data: Dict[str, Union[str, List[str]]]):
        result = data[self.source_field_name]
        if self.preproc_func is not None:
            result = self.preproc_func(result)

        return ResolvedField(self.target_field_name, self.source_field_name, result)


class Resolver(ABC):
    def __init__(self, fields: List[Field]):
        self.fields = fields
        if len(set(x.target_field_name for x in self.fields)) != len(self.fields):
            raise RuntimeError('Duplicate target field name in fields list')

        self.field_order_by_target_name = {}
        self.set_field_order(fields)

    def set_field_order(self, ordered_fields: List[Field]):
        for index, field in enumerate(ordered_fields):
            self.field_order_by_target_name[field.target_field_name] = index

    def _get_order_by_resolved_fieldname(self, fieldname:str):
        return self.field_order_by_target_name.get(fieldname, 100), fieldname

    def _wordlist_to_rows(self, words: List[str]) -> List[List[ResolvedField]]:
        return [self._resolve_fieldlist(word, self.fields) for word in tqdm(words, desc='populating rows')]

    def _resolve_fieldlist(self, word: str, fields: List[Field]) -> List[ResolvedField]:
        fields_by_datasource = defaultdict(list)
        for field in fields:
            fields_by_datasource[field.data_source].append(field)

        result = []
        for datasource, fields in fields_by_datasource.items():
            data = datasource.lookup_word(word)
            for field in fields:
                result.append(field.resolve(data))

        return sorted(result, key=lambda x:  (self.field_order_by_target_name.get(x.name, 100), x.name))

    @abstractmethod
    def _output_file(self, rows: List[List[ResolvedField]], filename: str) -> str:
        raise NotImplementedError('Resolver classes must define _output_file')

    def resolve_to_file(self, words: List[str], name: str):
        if len(words) == 0:
            raise RuntimeError('Cannot resolve an empty wordlist')
        rows = self._wordlist_to_rows(words)
        final_out_name = self._output_file(rows, name)
        print('Resolved card data written to file {}'.format(final_out_name))