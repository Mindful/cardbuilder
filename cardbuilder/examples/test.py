from cardbuilder.card_resolvers import Field, CsvResolver
from cardbuilder.common.fieldnames import WORD, DEFINITIONS, DETAILED_READING
from cardbuilder.data_sources.ja_to_en import Jisho
from cardbuilder.word_lists import InputWords

dictionary = Jisho()
words = InputWords(input_file_name)

fields = [
    Field(dictionary, WORD, 'word'),
    Field(dictionary, DEFINITIONS, 'definitions'),
    Field(dictionary, DETAILED_READING, 'readding'),
]

resolver = CsvResolver(fields)
failed_resolutions = resolver.resolve_to_file(words, output_filename)