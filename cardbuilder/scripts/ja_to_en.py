from typing import Dict

from cardbuilder.card_resolvers import Field
from cardbuilder.card_resolvers.resolver import Resolver
from cardbuilder.common.fieldnames import WORD, DEFINITIONS, EXAMPLE_SENTENCES, DETAILED_READING, PITCH_ACCENT, WRITINGS
from cardbuilder.common.languages import JAPANESE, ENGLISH
from cardbuilder.common.util import log
from cardbuilder.data_sources import DataSource, StringValue, Value
from cardbuilder.data_sources.ja_to_en import Jisho
from cardbuilder.data_sources.ja_to_ja import NhkPitchAccent
from cardbuilder.data_sources.tatoeba import TatoebaExampleSentences
from cardbuilder.scripts.helpers import build_parser_with_common_args, get_args_and_input_from_parser, \
    log_failed_resolutions, trim_whitespace
from cardbuilder.scripts.router import command
from pykakasi import kakasi


default_css = trim_whitespace('''.overline {text-decoration:overline;}
                                .nopron {color: royalblue;}
                                .nasal{color: red;}''')


@command('ja_to_en')
def main():
    parser = build_parser_with_common_args()
    args, input_words = get_args_and_input_from_parser(parser)

    dictionary = Jisho()
    nhk = NhkPitchAccent()
    example_sentences = TatoebaExampleSentences(source_lang=JAPANESE, target_lang=ENGLISH)

    fields = [
        Field(dictionary, WORD, 'word'),
        Field(dictionary, DEFINITIONS, 'definitions', lambda v: v.to_output_string(number=True)),
        Field(dictionary, DETAILED_READING, 'reading'),
        Field(nhk, PITCH_ACCENT, 'pitch_accent', optional=True),
        Field(example_sentences, EXAMPLE_SENTENCES, 'example sentence', optional=True)
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

    resolver = Resolver.instantiable[args.output_format](fields)
    if args.output_format == 'anki':
        resolver.set_card_templates(None, css=default_css)
        #TODO: add proper default cards like in the SVL deck so people don't have to make their own

    resolver.mutator = disambiguate_pitch_accent
    failed_resolutions = resolver.resolve_to_file(input_words, args.output)
    log_failed_resolutions(failed_resolutions)

    if args.output_format != 'anki':
        log(None, 'If you are importing a CSV to Anki, remember to enable HTML imports')
        log(None, 'Also, the below CSS is required to display the NHK pitch accent data')
        print(default_css)


if __name__ == '__main__':
    main()



