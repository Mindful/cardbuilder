# Takes a raw input list of Japanese words and outputs a flashcard csv
from argparse import ArgumentParser
from time import time
import csv
from typing import Dict, Union, List

from cardbuilder import CardBuilderException
from cardbuilder.card_resolvers import CsvResolver, Field
from cardbuilder.common.fieldnames import WORD, DEFINITIONS, EXAMPLE_SENTENCES, DETAILED_READING, PITCH_ACCENT, WRITINGS
from cardbuilder.common.languages import JAPANESE, ENGLISH
from cardbuilder.common.util import enable_console_reporting, log
from cardbuilder.data_sources import DataSource, StringValue, Value
from cardbuilder.data_sources.ja_to_en import Jisho
from cardbuilder.data_sources.ja_to_ja import NhkPitchAccent
from cardbuilder.data_sources.tatoeba import TatoebaExampleSentences
from cardbuilder.word_lists import InputList
from pykakasi import kakasi


def main():
    #TODO: support CSV or anki deck output
    # in the case of anki deck output, directly add the pitch accent css
    enable_console_reporting()
    parser = ArgumentParser()
    parser.add_argument('--input_file', required=True, help='Input file of words, one word per line')
    args = parser.parse_args()
    run_time = int(time())
    output_filename = 'cardlist_additions_{}'.format(run_time)

    words = InputList(args.input_file)
    dictionary = Jisho()
    nhk = NhkPitchAccent()
    example_sentences = TatoebaExampleSentences(source_lang=JAPANESE, target_lang=ENGLISH)

    fields = [
        Field(dictionary, WORD, 'word'),
        Field(dictionary, DEFINITIONS, 'definitions', lambda v: v.to_output_string(number=True)),
        Field(dictionary, DETAILED_READING, 'reading'),
        Field(nhk, PITCH_ACCENT, 'pitch_accent', optional=True),
        Field(example_sentences, EXAMPLE_SENTENCES, 'example sentence')
    ]

    converter = kakasi()

    # an example of how to use arbitrary mutators with resolvers
    # this one in particular accomplishes two things:
    # 1. it saves us from erroring out when someone tries to look up raw kana in the NHK accent database, like ひらく
    # 2. in cases where someone provides kana, we can disambiguate the pitch accent, like for 開く (ひらく・あく)
    # for the vast majority of words though, it should have no effect
    def disambiguate_pitch_accent(data_by_source: Dict[DataSource, Dict[str, Value]],
                                  datasource_by_name: Dict[str, DataSource]) -> None:
        try:
            reading = data_by_source[dictionary][DETAILED_READING].to_output_string()
            writing = data_by_source[dictionary][WRITINGS].to_list()[0]
            if nhk in data_by_source:
                accents_val = data_by_source[nhk][PITCH_ACCENT]
                if len(accents_val.pitch_accent_by_reading) == 1:
                    return  # No ambiguities to resolve here
            else:
                data_by_source[nhk] = {}
                accents_val = nhk.lookup_word(writing)[PITCH_ACCENT]
            reading_katakana = converter.convert(reading)[0]['kana']
            data_by_source[nhk][PITCH_ACCENT] = StringValue(accents_val.pitch_accent_by_reading[reading_katakana])
        except KeyError:
            pass

    resolver = CsvResolver(fields)
    resolver.mutator = disambiguate_pitch_accent
    failed_resolutions = resolver.resolve_to_file(words, output_filename)
    if len(failed_resolutions) > 0:
        res_failures_filename = 'resolution_failures_{}.tsv'.format(run_time)
        with open(res_failures_filename, 'w+') as error_file:
            log(None, 'Resolution failures written to file {}'.format(res_failures_filename))
            writer = csv.writer(error_file, delimiter='\t')
            writer.writerows(failed_resolutions)

    #TODO: in the case of CSV output, remind people that
    #1. they need to allow html imports for the pitch accent
    #2 they need to add css to cards for the pitch accent


if __name__ == '__main__':
    main()



