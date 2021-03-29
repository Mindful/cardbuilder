from abc import ABC, abstractmethod
from copy import copy
from typing import List, Iterable, Optional, Union

from cardbuilder.word_lists.word import Word, WordForm


class WordList(ABC):

    def __init__(self, word_input_forms: Iterable[str], language: str, additional_forms: Optional[List[WordForm]]):
        self.words = [Word(input_form, language, additional_forms) for input_form in word_input_forms]

    def __getitem__(self, index: Union[int, slice]) -> Union[Word, 'WordList']:
        if isinstance(index, int):
            return self.words[index]
        elif isinstance(index, slice):
            list_copy = copy(self)
            list_copy.words = self.words[index]
            return list_copy
        else:
            raise TypeError('WordList indices must be either integers or slices')

    def __iter__(self):
        return iter(self.words)

    def __len__(self):
        return len(self.words)

    def __repr__(self):
        return repr(self.words)

