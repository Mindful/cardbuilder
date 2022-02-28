import json

from cardbuilder.common import Language, Fieldname
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import WebApiDataSource
from cardbuilder.lookup.lookup_data import LookupData, outputs

from wiktionaryparser import WiktionaryParser

from cardbuilder.lookup.value import MultiListValue, SingleValue, ListValue


@outputs({
    Fieldname.DEFINITIONS: MultiListValue,
    Fieldname.SUPPLEMENTAL: SingleValue,  # Etymology
    Fieldname.PRONUNCIATION_IPA: ListValue,
    Fieldname.AUDIO: ListValue
})
class Wiktionary(WebApiDataSource):
    """
    A data source that retrives information from Wiktionary using https://github.com/Suyash458/WiktionaryParser
    The returned supplemental data is the word etymology.
    """

    def _query_api(self, form: str) -> str:
        return json.dumps(self.parser.fetch(form))

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        parsed_content = json.loads(content)

        if len(parsed_content) == 0:
            raise WordLookupException(f'Found no results for {form} in Wiktionary')

        # assuming these are all exact matches, no better way to choose. only other option is using all results
        target_content = parsed_content[0]

    def __init__(self, language: Language,  enable_cache_retrieval=True):
        super(Wiktionary, self).__init__(enable_cache_retrieval=enable_cache_retrieval)
        self.lang = language
        self.parser = WiktionaryParser()
        self.parser.set_default_language(language.get_name())
