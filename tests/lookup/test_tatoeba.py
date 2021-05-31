import pytest

from cardbuilder.common import Fieldname, Language
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.tatoeba import TatoebaExampleSentences
from tests.lookup.data_source_test import DataSourceTest


class TestTatoeba(DataSourceTest):
    def get_data_source(self) -> DataSource:
        return TatoebaExampleSentences(Language.ENGLISH, Language.JAPANESE)

    def test_lookup(self):
        data_source = self.get_data_source()

        hot_data = data_source.lookup_word(Word('hot', Language.ENGLISH), 'hot')
        dog_data = data_source.lookup_word(Word('dog', Language.ENGLISH), 'dog')

        hot_sents = hot_data[Fieldname.EXAMPLE_SENTENCES].get_data()
        dog_sents = dog_data[Fieldname.EXAMPLE_SENTENCES].get_data()

        assert(all('dog' in source_sent.get_data().lower() for source_sent, _ in dog_sents))
        assert(any('犬' in target_sent.get_data().lower() for _, target_sent in dog_sents))
        assert(all('hot' in source_sent.get_data().lower() for source_sent, _ in hot_sents))
        assert(any('暑い' in target_sent.get_data().lower() for _, target_sent in hot_sents))

        with pytest.raises(WordLookupException):
            data_source.lookup_word(Word('עברית', Language.HEBREW), 'עברית')

        # no results for 日本語 because mecab splits it into 日本 and 語. very sad
        # jp_tatoeba = TatoebaExampleSentences(Language.JAPANESE, Language.ENGLISH)
        #
        # nihongo_data = jp_tatoeba.lookup_word(Word('日本語', Language.JAPANESE), '日本語')

