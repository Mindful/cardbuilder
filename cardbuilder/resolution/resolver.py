import logging
from abc import ABC, abstractmethod
from typing import List, Union, Tuple, Dict, Callable

from cardbuilder.common.util import log
from cardbuilder.exceptions import CardResolutionException, CardBuilderUsageException
from cardbuilder.input.word import Word
from cardbuilder.input.word_list import WordList
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.lookup_data import LookupData
from cardbuilder.resolution.card_data import CardData
from cardbuilder.resolution.field import Field
from cardbuilder.resolution.resolution_engine import ResolutionEngine


class Resolver(ABC):
    """The base class for all resolvers, responsible for taking lookup data and transforming it into an output format
    that can be used as flashcards. """
    def __init__(self, fields: List[Field],
                 mutator: Callable[[Dict[DataSource, LookupData]], Dict[DataSource, LookupData]] = None):
        self.engine = ResolutionEngine(fields, mutator)

    @abstractmethod
    def _output_file(self, rows: List[CardData], filename: str) -> str:
        raise NotImplementedError('Resolver classes must define _output_file')

    def resolve_to_file(self, words: Union[List[Word], WordList], name: str) -> List[Tuple[str, CardResolutionException]]:
        if len(words) == 0:
            raise CardBuilderUsageException('Cannot resolve an empty wordlist')
        cards = list(self.engine.cards(words))
        final_out_name = self._output_file(cards, name)
        log(self, 'Resolved card data written to file {}'.format(final_out_name))
        failed_resolutions = self.engine.failed_resolutions
        if len(failed_resolutions) > 0:
            log(self, 'Failed to resolve {} cards'.format(len(failed_resolutions)), level=logging.WARNING)

        return failed_resolutions
