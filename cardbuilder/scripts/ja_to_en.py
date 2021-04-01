from typing import Dict

from cardbuilder.resolution.instantiable import instantiable_resolvers
from cardbuilder.input.word import Word
from cardbuilder.lookup.lookup_data import LookupData
from cardbuilder.resolution.field import Field
from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.languages import JAPANESE, ENGLISH
from cardbuilder.common.util import log, Shared
from cardbuilder.lookup import DataSource
from cardbuilder.lookup.value import StringValue
from cardbuilder.lookup.ja_to_en import Jisho
from cardbuilder.lookup.ja_to_ja import NhkPitchAccent
from cardbuilder.lookup.tatoeba import TatoebaExampleSentences
from cardbuilder.scripts.helpers import build_parser_with_common_args, get_args_and_input_from_parser, \
    log_failed_resolutions
from cardbuilder.scripts.router import command


@command('ja_to_en')
def main():
    parser = build_parser_with_common_args()
    args, input_words = get_args_and_input_from_parser(parser, JAPANESE)

    dictionary = Jisho()
    nhk = NhkPitchAccent()
    example_sentences = TatoebaExampleSentences(source_lang=JAPANESE, target_lang=ENGLISH)

    fields = [
        Field(dictionary, Fieldname.WORD, 'word'),
        Field(dictionary, Fieldname.DEFINITIONS, 'definitions', lambda v: v.to_output_string(number=True)),
        Field(dictionary, Fieldname.DETAILED_READING, 'reading'),
        Field(nhk, Fieldname.PITCH_ACCENT, 'pitch_accent', optional=True),
        Field(example_sentences, Fieldname.EXAMPLE_SENTENCES, 'example sentence', optional=True)
    ]

    # an example of how to use arbitrary mutators with resolvers
    # this one in particular accomplishes two things:
    # 1. it saves us from failing when someone tries to look up raw kana in the NHK accent database, like ひらく
    # 2. in cases where someone provides kana, we can disambiguate the pitch accent, like for 開く (ひらく・あく)
    # for the vast majority of words though, it should have no effect
    #TODO: verify this still does what it's supposed to do
    def disambiguate_pitch_accent(data_by_source: Dict[DataSource, LookupData]) -> Dict[DataSource, LookupData]:
        try:
            reading = data_by_source[dictionary][Fieldname.DETAILED_READING].to_output_string()
            writing = data_by_source[dictionary][Fieldname.WRITINGS].to_list()[0]
            if nhk in data_by_source:
                accents_val = data_by_source[nhk][Fieldname.PITCH_ACCENT]
                if len(accents_val.pitch_accent_by_reading) == 1:
                    return data_by_source  # No ambiguities to resolve here
            else:
                accents_val = nhk.lookup_word(Word(writing, JAPANESE), writing)[Fieldname.PITCH_ACCENT]
            reading_katakana = Shared.get_kakasi().convert(reading)[0]['kana']

            data_by_source[nhk] = nhk.lookup_data_type(Word(writing, JAPANESE), writing, {
                Fieldname.PITCH_ACCENT: StringValue(accents_val.pitch_accent_by_reading[reading_katakana])
            })
            return data_by_source
        except KeyError:
            return data_by_source

    resolver = instantiable_resolvers[args.output_format](fields)
    if args.output_format == 'anki':
        resolver.set_note_name(args.output, None, css=nhk.default_css)
        #TODO: add proper default cards like in the SVL deck so people don't have to make their own

    resolver.mutator = disambiguate_pitch_accent
    failed_resolutions = resolver.resolve_to_file(input_words, args.output)
    log_failed_resolutions(failed_resolutions)

    if args.output_format != 'anki':
        log(None, 'If you are importing a CSV to Anki, remember to enable HTML imports')
        log(None, 'Also, the below CSS is required to display the NHK pitch accent data')
        print(nhk.default_css)


if __name__ == '__main__':
    main()



