from json import dumps, loads

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.exceptions import WordLookupException
from cardbuilder.lookup.data_source import DataSource, WebApiDataSource
from cardbuilder.lookup.lookup_data import LookupData, outputs
from cardbuilder.input.word import Word
from cardbuilder.lookup.value import ListValue, MultiListValue, MultiValue

from reverso_api.context import ReversoContextAPI
endpoint = "https://context.reverso.net/translation/english-hebrew/"



@outputs({
    Fieldname.DEFINITIONS: ListValue,
    Fieldname.PART_OF_SPEECH: ListValue,
    Fieldname.EXAMPLE_SENTENCES: MultiListValue
})

class Reverso(WebApiDataSource):

    def __init__(self, source_lang: str, target_lang: str):
        self.source_language = source_lang
        self.target_language = target_lang
        self.max_examples = 5

    def _get_example_sentences(self, translation_form: str) -> [str]:

        # swap the src and target languages so we don't need thousands of calls to get one example for rarer translation
        reversed_api = ReversoContextAPI(source_text=translation_form, source_lang=self.target_language, target_lang=self.source_language)

        example_getter = reversed_api.get_examples()
        examples = []
        # just get 5 examples max, this takes way too long for common words
        for i in range(self.max_examples):
            try:
                target_example, src_example = next(example_getter)
                examples.append(target_example.text)
            except StopIteration:
                continue

        return examples

    def _query_api(self, form: str) -> str:
        api = ReversoContextAPI(source_text=form,
                                source_lang=self.source_language,
                                target_lang=self.target_language)
        """
        api.get_translations() look like:

        Translation(source_word='hello', 
        translation='שלום', frequency=15335, 
        part_of_speech='adv.', inflected_forms=[]), ...
        """
        data = {}
        examples = api.get_examples()  # generator for examples
        for _, translation, _, pos, _ in api.get_translations():
            examples = self._get_example_sentences(translation)
            data[translation] = {'part_of_speech': pos, 'examples': examples}
        return dumps(data)

    def parse_word_content(self, word: Word, form: str, content: str) -> LookupData:
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


