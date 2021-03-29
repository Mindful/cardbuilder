from abc import ABC, abstractmethod

from cardbuilder.word_lists import WordList
from cardbuilder.word_lists.word import Word


class WordListTest(ABC):

    @abstractmethod
    def get_word_list(self) -> WordList:
        raise NotImplementedError()

    def test_get_item(self):
        wordlist = self.get_word_list()

        sample_word = wordlist[0]
        assert(isinstance(sample_word, Word))

        list_slice = wordlist[0:10]
        assert(isinstance(list_slice, type(wordlist)))
        assert(list_slice[0] == sample_word)


