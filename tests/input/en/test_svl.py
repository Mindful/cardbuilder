from cardbuilder.common import Fieldname, Language
from cardbuilder.input.en.svl import SvlWords
from cardbuilder.input.word import Word
from cardbuilder.input.word_list import WordList
from cardbuilder.lookup.data_source import DataSource
from tests.input.word_list_test import WordListTest
from tests.lookup.data_source_test import DataSourceTest


class TestSvl(WordListTest, DataSourceTest):

    def get_word_list(self) -> WordList:
        return SvlWords()

    def get_data_source(self) -> DataSource:
        return SvlWords()

    def test_ordering(self):
        freq_sorted = SvlWords(order_by_wordfreq=True)
        non_sorted = SvlWords(order_by_wordfreq=False)

        assert(list(freq_sorted) != list(non_sorted))
        assert(sorted(w.input_form for w in freq_sorted) == sorted(w.input_form for w in non_sorted))

        assert(freq_sorted[0].input_form == 'the')

    def test_level_retrieval(self):
        wordlist = self.get_word_list()

        w1 = Word('sure', Language.ENGLISH)
        w2 = Word('incorrect', Language.ENGLISH)
        w3 = Word('aviary', Language.ENGLISH)
        assert(wordlist.lookup_word(w1, w1.input_form)[Fieldname.SUPPLEMENTAL].get_data() == '1')
        assert(wordlist.lookup_word(w2, w2.input_form)[Fieldname.SUPPLEMENTAL].get_data() == '6')
        assert(wordlist.lookup_word(w3, w3.input_form)[Fieldname.SUPPLEMENTAL].get_data() == '12')
