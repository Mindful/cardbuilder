from collections import defaultdict
from json import dumps, loads

from cardbuilder.common import Fieldname, Language
from cardbuilder.exceptions import WordLookupException
from cardbuilder.lookup.data_source import WebApiDataSource
from cardbuilder.lookup.lookup_data import LookupData, outputs
from cardbuilder.input.word import Word
from cardbuilder.lookup.value import ListValue, MultiListValue, MultiValue

from reverso_api.context import ReversoContextAPI


@outputs({
    Fieldname.EXAMPLE_SENTENCES: MultiValue,
    Fieldname.DEFINITIONS: MultiListValue
})
class Reverso(WebApiDataSource):

    def __init__(self, source_lang: Language, target_lang: Language, enable_cache_retrieval: bool = True):
        super(Reverso, self).__init__(enable_cache_retrieval=enable_cache_retrieval)
        self.source_language = source_lang
        self.target_language = target_lang
        self.max_examples = 5

    def _query_api(self, form: str) -> str:
        reverso_api = ReversoContextAPI(source_text=form, source_lang=self.source_language.get_iso2(),
                                        target_lang=self.target_language.get_iso2())

        example_getter = reverso_api.get_examples()
        examples = []
        # just get 5 examples max, this takes way too long for common words
        for i in range(self.max_examples):
            try:
                target_example, src_example = next(example_getter)
                examples.append(target_example.text)
            except StopIteration:
                break

        definitions = defaultdict(list)
        for _, translation, _, pos, _ in reverso_api.get_translations():
            cleaned_pos = pos.strip('.')
            definitions[cleaned_pos].append(translation)

        return dumps({
            Fieldname.EXAMPLE_SENTENCES: [(ex.text, ex.highlighted) for ex in examples],
            Fieldname.DEFINITIONS: definitions
        })

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        #TODO: finish rewriting this
        """
        So for every word we'll have a list of possible translations, and then examples sentences.
        I'm guessing for the anki card output we'll just want: all possible translations followed by all examples
        """
        translation_values = []
        pos_values = []
        example_sentence_values = []
        for translation, pos, example_sentences in loads(content):
            translation_values.append(translation)
            pos_values.append((pos, translation))
            example_sentence_values.append((example_sentences, translation))

        return self.lookup_data_type(word, form, content,
                                     {
                                         Fieldname.DEFINITIONS: ListValue(translation_values),
                                         Fieldname.PART_OF_SPEECH: MultiValue(pos_values),
                                         Fieldname.EXAMPLE_SENTENCES: MultiListValue(example_sentence_values)
                                     })
