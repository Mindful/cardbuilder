from typing import Union, List, Iterable, Callable, Dict

from cardbuilder.resolution.field import Field
from cardbuilder.common.util import loading_bar
from cardbuilder.lookup import DataSource
from cardbuilder.lookup.lookup_data import LookupData
from cardbuilder.exceptions import CardResolutionException, WordLookupException, CardBuilderUsageException
from cardbuilder.input.word import Word
from cardbuilder.input.word_list import WordList
from cardbuilder.resolution.card_data import CardData


class ResolutionEngine:

    def __init__(self, fields: List[Field],
                 mutator: Callable[[Dict[DataSource, LookupData]], Dict[DataSource, LookupData]] = None):
        self.mutator = self.default_mutator if mutator is None else mutator
        self.fields = fields
        if len(set(x.target_field_name for x in self.fields)) != len(self.fields):
            raise CardBuilderUsageException('Duplicate target field name in fields list')

        self.datasource_by_name = {}
        for field in fields:
            for data_source in field.data_sources:
                name = type(data_source).__name__
                if name in self.datasource_by_name:
                    if data_source != self.datasource_by_name[name]:
                        raise CardBuilderUsageException('Attempting to construct a resolver with duplicate '
                                                        'data sources of type {}'.format(name))
                else:
                    self.datasource_by_name[name] = data_source

        self.failed_resolutions = []

    @staticmethod
    def default_mutator(data_by_source: Dict[DataSource, LookupData]) -> Dict[DataSource, LookupData]:
        return data_by_source

    def cards(self, words: Union[List[str], WordList]) -> Iterable[CardData]:
        self.failed_resolutions = []
        for word in loading_bar(words, 'populating cards'):
            try:
                yield self._resolve_fieldlist(word)
            except CardResolutionException as ex:
                self.failed_resolutions.append((word, ex))

    def _resolve_fieldlist(self, word: Word) -> CardData:
        data_by_source = {}
        failures_by_source = {}
        for datasource in self.datasource_by_name.values():
            for form in word:
                try:
                    data_by_source[datasource] = datasource.lookup_word(word, form)
                    break  # if we find something, we're done
                except WordLookupException as ex:
                    if datasource not in failures_by_source:  # record the first failure
                        failures_by_source[datasource] = ex

        data_by_source = self.mutator(data_by_source)
        resolved_fields = []

        for field in self.fields:
            field_data = [data_by_source[source] for source in field.data_sources if source in data_by_source]
            resolved_field = field.resolve(field_data)
            if resolved_field is None:
                raise CardResolutionException('Failed to resolve non-optional field {} due to {}'.format(
                    field.target_field_name, ', '.join(['{}:{}'.format(type(source).__name__, failure) for source, failure
                                              in failures_by_source.items() if source in field.data_sources])))
            else:
                resolved_fields.append(resolved_field)

        return CardData(resolved_fields)
