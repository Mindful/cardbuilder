import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Union, Tuple, Dict, Callable

from cardbuilder.card_resolution import Field, ResolvedField
from cardbuilder.common.util import loading_bar, log
from cardbuilder.data_sources import DataSource
from cardbuilder.exceptions import CardResolutionException, CardBuilderException, WordLookupException
from cardbuilder.word_sources import WordSource


class Resolver(ABC):
    def __init__(self, fields: List[Field],
                mutator: Callable[[Dict[DataSource, Dict[str, Union[str, List]]], Dict[str, DataSource]], None] = None):
        self.mutator = self.default_mutator if mutator is None else mutator
        self.fields = fields
        if len(set(x.target_field_name for x in self.fields)) != len(self.fields):
            raise RuntimeError('Duplicate target field name in fields list')

        self.fields_by_datasource = defaultdict(list)
        self.datasource_by_name = {}
        for field in fields:
            name = type(field.data_source).__name__
            if name in self.datasource_by_name:
                if field.data_source != self.datasource_by_name[name]:
                    raise CardBuilderException('Attempting to construct a resolver with duplicate '
                                               'data sources of type {}'.format(name))
            else:
                self.datasource_by_name[name] = field.data_source
            self.fields_by_datasource[field.data_source].append(field)

        self.field_order_by_target_name = {}
        self.set_field_order(fields)
        self.failed_resolutions = []

    def set_field_order(self, ordered_fields: List[Field]):
        for index, field in enumerate(ordered_fields):
            self.field_order_by_target_name[field.target_field_name] = index

    def _get_order_by_resolved_fieldname(self, fieldname: str):
        return self.field_order_by_target_name.get(fieldname, 100), fieldname

    def _wordlist_to_rows(self, words: Union[List[str], WordSource]) -> List[List[ResolvedField]]:
        self.failed_resolutions = []
        results = []
        for word in loading_bar(words, 'populating rows'):
            try:
                results.append(self._resolve_fieldlist(word))
            except CardResolutionException as ex:
                self.failed_resolutions.append((word, ex))

        return results

    @staticmethod
    def default_mutator(data_by_source: Dict[DataSource, Dict[str, Union[str, List]]],
                        datasource_by_name: Dict[str, DataSource]) -> None:
        pass

    def _resolve_fieldlist(self, word: str) -> List[ResolvedField]:
        data_by_source = {}
        for datasource, fields in self.fields_by_datasource.items():
            try:
                data = datasource.lookup_word(word)
                data_by_source[datasource] = data
            except WordLookupException as ex:
                for field in fields:
                    if not field.optional:
                        raise CardResolutionException('Could not look up word "{}" from {} due to lookup excetion: {}'.
                                                      format(word, type(datasource).__name__, ex))

        self.mutator(data_by_source, self.datasource_by_name.copy())
        result = []
        for datasource, fields in self.fields_by_datasource.items():
            for field in fields:
                if datasource in data_by_source:
                    result.append(field.resolve(data_by_source[datasource]))
                elif field.optional:
                    result.append(field.blank())
                else:
                    raise CardBuilderException('Found no data for non-optional field, this should never happen')

        return sorted(result, key=lambda x: (self.field_order_by_target_name.get(x.name, 100), x.name))

    @abstractmethod
    def _output_file(self, rows: List[List[ResolvedField]], filename: str) -> str:
        raise NotImplementedError('Resolver classes must define _output_file')

    def resolve_to_file(self, words: Union[List[str], WordSource], name: str) -> List[Tuple[str, CardResolutionException]]:
        if len(words) == 0:
            raise RuntimeError('Cannot resolve an empty wordlist')
        rows = self._wordlist_to_rows(words)
        final_out_name = self._output_file(rows, name)
        log(self, 'Resolved card data written to file {}'.format(final_out_name))
        if len(self.failed_resolutions) > 0:
            log(self, 'Failed to resolve {} cards'.format(len(self.failed_resolutions)), level=logging.WARNING)

        return self.failed_resolutions
