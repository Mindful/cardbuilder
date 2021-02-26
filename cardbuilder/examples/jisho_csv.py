# Takes a raw input list of Japanese words and outputs a flashcard csv
from argparse import ArgumentParser
from time import time

from card_resolution import CsvResolver, Field
from card_resolution.preprocessing import default_preprocessing
from common.fieldnames import WORD, DEFINITIONS, EXAMPLE_SENTENCES, DETAILED_READING
from common.languages import JAPANESE, ENGLISH
from common.util import enable_console_reporting
from data_sources.ja_to_en import Jisho
from data_sources.tatoeba import TatoebaExampleSentences
from word_sources import InputWords


def main():
    enable_console_reporting()
    parser = ArgumentParser()
    parser.add_argument('--input_file', required=True, help='Input file of words, one word per line')
    args = parser.parse_args()
    output_filename = 'cardlist_additions_{}'.format(int(time()))

    dictionary = Jisho()
    example_sentences = TatoebaExampleSentences(source_lang=JAPANESE, target_lang=ENGLISH)
    words = InputWords(args.input_file)

    fields = [
        Field(dictionary, WORD, 'word'),
        Field(dictionary, DEFINITIONS, 'definitions'),
        Field(dictionary, DETAILED_READING, 'readding'),
        Field(example_sentences, EXAMPLE_SENTENCES, 'example sentence',
              preproc_func=lambda x: default_preprocessing(x[:2]), optional=True)
    ]

    resolver = CsvResolver(fields)
    resolver.resolve_to_file(words, output_filename)


if __name__ == '__main__':
    main()



