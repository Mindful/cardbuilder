from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import WebApiDataSource
from cardbuilder.lookup.lookup_data import LookupData, outputs


@outputs({

})
class TatoebaExampleSentences(WebApiDataSource):
    def _query_api(self, form: str) -> str:
        pass

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        pass