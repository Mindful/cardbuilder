import pytest

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.languages import JAPANESE, ENGLISH, HEBREW
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.tatoeba import TatoebaExampleSentences
from tests.lookup.data_source_test import DataSourceTest


class TestTatoeba(DataSourceTest):
    def get_data_source(self) -> DataSource:
        return TatoebaExampleSentences(ENGLISH, JAPANESE)

    def test_lookup(self):
        data_source = self.get_data_source()

        hot_data = data_source.lookup_word(Word('hot', ENGLISH), 'hot')
        dog_data = data_source.lookup_word(Word('dog', ENGLISH), 'dog')

        hot_sents = hot_data[Fieldname.EXAMPLE_SENTENCES].get_data()
        dog_sents = dog_data[Fieldname.EXAMPLE_SENTENCES].get_data()

        assert(all('dog' in source_sent.get_data().lower() for source_sent, _ in dog_sents))
        assert(any('犬' in target_sent.get_data().lower() for _, target_sent in dog_sents))
        assert(all('hot' in source_sent.get_data().lower() for source_sent, _ in hot_sents))
        assert(any('暑い' in target_sent.get_data().lower() for _, target_sent in hot_sents))

        with pytest.raises(WordLookupException):
            data_source.lookup_word(Word('עברית', HEBREW), 'עברית')
