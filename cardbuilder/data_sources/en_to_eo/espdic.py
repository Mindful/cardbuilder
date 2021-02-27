from typing import Any, Dict, Union, List
from collections import defaultdict

from cardbuilder.common import ExternalDataDependent
from cardbuilder.data_sources import DataSource, Value, StringValue
from cardbuilder.common.fieldnames import DEFINITIONS, PART_OF_SPEECH


class ESPDIC(DataSource, ExternalDataDependent):

    filename = 'espdic.txt'
    url = 'http://www.denisowski.org/Esperanto/ESPDIC/espdic.txt'
    delimiter = ':'
    backup_delimiter = ';'  # I wish this wasn't necessary, but there's at least one line that uses ;

    def __init__(self):
        self.definitions = self.get_data()

    def _infer_pos(self, word: str):
        #TODO: this probably needs to be smarter than it is
        last_char = word[-1]

        if word in {"mi", "vi", "li", "ŝi", "ĝi", "si", "ni", "vi", "ili", "oni"}:
            return 'pronoun'

        return {
            'o': 'noun',
            'a': 'adjective',
            'e': 'adverb',
            's': 'verb',
            'u': 'verb',
            'i': 'verb,',
            't': 'verb',
            'ŭ': 'adverb'
        }[last_char]

    def lookup_word(self, word: str) -> Dict[str, Value]:
        return {
            DEFINITIONS: StringValue(self.definitions[word]),
            PART_OF_SPEECH: StringValue(self._infer_pos(word))
        }

    def _read_data(self) -> Any:
        definitions = defaultdict(list)
        for line in open(self.filename):
            content = line.strip()
            if not content or '#' in content[:2]:
                continue

            if self.delimiter in content:
                word, definition = content.split(self.delimiter)
            elif self.backup_delimiter in content:
                word, definition = content.split(self.backup_delimiter)
            else:
                continue

            definitions[word.strip()].append(definition.strip())

        return definitions


