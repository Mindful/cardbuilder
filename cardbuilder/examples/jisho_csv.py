# Takes a raw input list of Japanese words and outputs a flashcard csv
from argparse import ArgumentParser
from time import time
import csv

from cardbuilder.card_resolvers import CsvResolver, Field
from cardbuilder.common.fieldnames import WORD, DEFINITIONS, EXAMPLE_SENTENCES, DETAILED_READING
from cardbuilder.common.languages import JAPANESE, ENGLISH
from cardbuilder.common.util import enable_console_reporting, log
from cardbuilder.data_sources.ja_to_en import Jisho
from cardbuilder.data_sources.tatoeba import TatoebaExampleSentences
from cardbuilder.word_lists import InputList


def main():
    enable_console_reporting()
    parser = ArgumentParser()
    parser.add_argument('--input_file', required=True, help='Input file of words, one word per line')
    args = parser.parse_args()
    run_time = int(time())
    output_filename = 'cardlist_additions_{}'.format(run_time)

    words = InputList(args.input_file)
    dictionary = Jisho()
    example_sentences = TatoebaExampleSentences(source_lang=JAPANESE, target_lang=ENGLISH)

    fields = [
        Field(dictionary, WORD, 'word'),
        Field(dictionary, DEFINITIONS, 'definitions'),
        Field(dictionary, DETAILED_READING, 'readding'),
        Field(example_sentences, EXAMPLE_SENTENCES, 'example sentence')
    ]

    resolver = CsvResolver(fields)
    failed_resolutions = resolver.resolve_to_file(words, output_filename)
    if len(failed_resolutions) > 0:
        res_failures_filename = 'resolution_failures_{}.tsv'.format(run_time)
        with open(res_failures_filename, 'w+') as error_file:
            log(None, 'Resolution failures written to file {}'.format(res_failures_filename))
            writer = csv.writer(error_file, delimiter='\t')
            writer.writerows(failed_resolutions)


if __name__ == '__main__':
    main()



