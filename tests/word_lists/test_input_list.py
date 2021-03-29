import pathlib

import pytest

from cardbuilder.common.languages import ENGLISH
from cardbuilder.word_lists import WordList, InputList
from tests.word_lists.test_wordlist import WordListTest


class TestInputList(WordListTest):

    def get_word_list(self) -> WordList:
        return InputList(str(pathlib.Path(__file__).parent.absolute().joinpath('input_list.txt')), ENGLISH)

    def test_list(self):
        wordlist = self.get_word_list()

        assert(wordlist[0].input_form == 'flashcard')
        assert(wordlist[2].input_form == 'glory')





