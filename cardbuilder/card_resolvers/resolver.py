import logging
from abc import ABC, abstractmethod
from typing import List, Union, Tuple, Dict, Callable

from cardbuilder.card_resolvers.field import Field, ResolvedField
from cardbuilder.common.util import loading_bar, log, build_instantiable_decorator
from cardbuilder.data_sources import DataSource, Value
from cardbuilder.exceptions import CardResolutionException, CardBuilderException, WordLookupException
from cardbuilder.word_lists import WordList


class Resolver(ABC):
    def __init__(self, fields: List[Field],
                mutator: Callable[[Dict[DataSource, Dict[str, Value]], Dict[str, DataSource]], None] = None):
        self.mutator = self.default_mutator if mutator is None else mutator
        self.fields = fields
        if len(set(x.target_field_name for x in self.fields)) != len(self.fields):
            raise CardBuilderException('Duplicate target field name in fields list')

        self.datasource_by_name = {}
        for field in fields:
            for data_source in field.data_sources:
                name = type(data_source).__name__
                if name in self.datasource_by_name:
                    if data_source != self.datasource_by_name[name]:
                        raise CardBuilderException('Attempting to construct a resolver with duplicate '
                                                   'data sources of type {}'.format(name))
                else:
                    self.datasource_by_name[name] = data_source

        self.field_order_by_target_name = {}
        self.set_field_order(fields)
        self.failed_resolutions = []

    def set_field_order(self, ordered_fields: List[Field]):
        for index, field in enumerate(ordered_fields):
            self.field_order_by_target_name[field.target_field_name] = index

    def _get_order_by_resolved_fieldname(self, fieldname: str):
        return self.field_order_by_target_name.get(fieldname, 100), fieldname

    def _wordlist_to_rows(self, words: Union[List[str], WordList]) -> List[List[ResolvedField]]:
        self.failed_resolutions = []
        results = []
        for word in loading_bar(words, 'populating rows'):
            try:
                results.append(self._resolve_fieldlist(word))
            except CardResolutionException as ex:
                self.failed_resolutions.append((word, ex))

        return results

    @staticmethod
    def default_mutator(data_by_source: Dict[DataSource, Dict[str, Value]],
                        datasource_by_name: Dict[str, DataSource]) -> None:
        pass

    def _resolve_fieldlist(self, word: str) -> List[ResolvedField]:
        data_by_source = {}
        failures_by_source = {}
        for datasource in self.datasource_by_name.values():
            try:
                data_by_source[datasource] = datasource.lookup_word(word)
            except WordLookupException as ex:
                failures_by_source[datasource] = ex

        self.mutator(data_by_source, self.datasource_by_name.copy())
        result = []

        for field in self.fields:
            field_data = [data_by_source[source] for source in field.data_sources if source in data_by_source]
            resolved_field = field.resolve(field_data)
            if resolved_field is None:
                raise CardResolutionException('Failed to resolve non-optional field {} due to {}'.format(
                    field.target_field_name, ', '.join(['{}:{}'.format(type(source).__name__, failure) for source, failure
                                              in failures_by_source.items() if source in field.data_sources])))
            else:
                result.append(resolved_field)

        return sorted(result, key=lambda x: (self.field_order_by_target_name.get(x.name, 100), x.name))

    @abstractmethod
    def _output_file(self, rows: List[List[ResolvedField]], filename: str) -> str:
        raise NotImplementedError('Resolver classes must define _output_file')

    def resolve_to_file(self, words: Union[List[str], WordList], name: str) -> List[Tuple[str, CardResolutionException]]:
        if len(words) == 0:
            raise CardBuilderException('Cannot resolve an empty wordlist')
        rows = self._wordlist_to_rows(words)
        final_out_name = self._output_file(rows, name)
        log(self, 'Resolved card data written to file {}'.format(final_out_name))
        if len(self.failed_resolutions) > 0:
            log(self, 'Failed to resolve {} cards'.format(len(self.failed_resolutions)), level=logging.WARNING)

        return self.failed_resolutions


instantiable_resovler = build_instantiable_decorator(Resolver)

