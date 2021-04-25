from cardbuilder.common.languages import ENGLISH
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.en.merriam_webster import ScrapingMerriamWebster
from tests.lookup.data_source_test import DataSourceTest


class TestScrapingMerriamWebster(DataSourceTest):
    def get_data_source(self) -> DataSource:
        return ScrapingMerriamWebster()

    def test_lookup(self):
        data_source = self.get_data_source()

        dog_data = data_source.lookup_word(Word('dog', ENGLISH), 'dog')
        later_data = data_source.lookup_word(Word('later', ENGLISH), 'later')
        lead_data = data_source.lookup_word(Word('lead', ENGLISH), 'lead')

        # only found in extra form, not main results
        perpetrator_data = data_source.lookup_word(Word('perpetrator', ENGLISH), 'perpetrator')

        #TODO: flesh out test