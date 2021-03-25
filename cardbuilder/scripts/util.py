from argparse import ArgumentParser, Namespace
from typing import Iterable, Tuple
from datetime import datetime

from cardbuilder.common.util import enable_console_reporting
from cardbuilder.word_lists import WordList, InputList
from cardbuilder import CardBuilderException


def get_parser_with_common_args() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('--start', help='Index of first word to include', type=int)
    parser.add_argument('--stop', help='Index of last word to include',  type=int)
    parser.add_argument('--input', help='The location of a file to use for raw input or a reference to a wordlist',
                        type=str, required=True)
    parser.add_argument('--console', help='Whether or not to output progress to the console', type=bool, default=True)
    parser.add_argument('--output', help='The name of the output file. Defaults to cards_{time}', type=str,
                        default='cards_{}'.format(datetime.now().strftime('%d_%H_%M')))
    return parser


def get_args_and_input_from_parser(parser: ArgumentParser) -> Tuple[Namespace, Iterable]:
    args = parser.parse_args()
    if sum(1 for argument in [args.start, args.stop] if argument is not None) % 2 != 0:
        raise CardBuilderException('Must provide either both --start and --stop arguments or neither')

    if args.console:
        enable_console_reporting()

    if args.input in WordList.instantiable:
        input_wordlist = WordList.instantiable[args.input]
    else:
        input_wordlist = InputList(args.input)

    if args.start is not None and args.stop is not None:
        return args, input_wordlist[args.start:args.stop-1]
    else:
        return args, input_wordlist





