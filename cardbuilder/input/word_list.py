from abc import ABC
from copy import copy
from typing import List, Iterable, Optional, Union

from cardbuilder.common import Language
from cardbuilder.input.word import Word, WordForm


class WordList(ABC):

    """The base class for all word lists; all word lists inherit from this class. Behaves like a Python list by
    implementing iteration, length, item retrieval by index and slicing."""

    def __init__(self, word_input_forms: Iterable[str], language: Language, additional_forms: Optional[List[WordForm]]):
        """

        Args:
            word_input_forms: Strings representing the raw input forms of each word in the word list.
            language: The language of words in the word list.
            additional_forms: Any additional forms, such as conjugations, which these words can be retrieved as.
        """
        self.words = [Word(input_form, language, additional_forms)
                      for input_form in word_input_forms]

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

