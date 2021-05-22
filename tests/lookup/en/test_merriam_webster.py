import pytest

from cardbuilder.common import Language
from cardbuilder.common.config import Config
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import DataSource
from cardbuilder.lookup.en import MerriamWebster
from tests.lookup.data_source_test import DataSourceTest


@pytest.mark.skipif(not Config.has(MerriamWebster.thesaurus_api_conf_name)
                    or not Config.has(MerriamWebster.learners_api_conf_name),
                    reason="Requires MerriamWebster API Keys")
class TestMerriamWebster(DataSourceTest):
    def get_data_source(self) -> DataSource:
        return MerriamWebster()

    def test_lookup(self):
        data_source = self.get_data_source()

        society_data = data_source.lookup_word(Word('society', Language.ENGLISH), 'society')  # MW returns no audio
        dog_data = data_source.lookup_word(Word('dog', Language.ENGLISH), 'dog')
        later_data = data_source.lookup_word(Word('later', Language.ENGLISH), 'later')
        lead_data = data_source.lookup_word(Word('lead', Language.ENGLISH), 'lead')

        # only found in extra form, not main results
        perpetrator_data = data_source.lookup_word(Word('perpetrator', Language.ENGLISH), 'perpetrator')


        #TODO: flesh out test, add a test for words the thesaurus fails on (previously caused problems)