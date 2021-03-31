import logging
from abc import ABC, abstractmethod
from typing import List, Union, Tuple, Dict, Callable

from cardbuilder.resolution.card_data import CardData
from cardbuilder.resolution.field import Field
from cardbuilder.resolution.resolution_engine import ResolutionEngine
from cardbuilder.common.util import log
from cardbuilder.lookup import DataSource
from cardbuilder.lookup.lookup_data import LookupData
from cardbuilder.exceptions import CardResolutionException, CardBuilderException
from cardbuilder.input.word_list import WordList
from cardbuilder.input.word import Word


class Resolver(ABC):
    def __init__(self, fields: List[Field],
                 mutator: Callable[[Dict[DataSource, LookupData]], Dict[DataSource, LookupData]] = None):
        self.engine = ResolutionEngine(fields, mutator)

    @abstractmethod
    def _output_file(self, rows: List[CardData], filename: str) -> str:
        raise NotImplementedError('Resolver classes must define _output_file')

    def resolve_to_file(self, words: Union[List[Word], WordList], name: str) -> List[Tuple[str, CardResolutionException]]:
        if len(words) == 0:
            raise CardBuilderException('Cannot resolve an empty wordlist')
        cards = list(self.engine.cards(words))
        final_out_name = self._output_file(cards, name)
        log(self, 'Resolved card data written to file {}'.format(final_out_name))
        failed_resolutions = self.engine.failed_resolutions
        if len(failed_resolutions) > 0:
            log(self, 'Failed to resolve {} cards'.format(len(failed_resolutions)), level=logging.WARNING)

        return failed_resolutions
