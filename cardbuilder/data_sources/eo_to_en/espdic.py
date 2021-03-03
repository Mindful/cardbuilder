from typing import Any, Dict, Iterable, Tuple
from collections import defaultdict

from cardbuilder.data_sources import Value, StringValue, StringListValue
from cardbuilder.common.fieldnames import DEFINITIONS, PART_OF_SPEECH
from cardbuilder.data_sources.data_source import ExternalDataDataSource


class ESPDIC(ExternalDataDataSource):

    filename = 'espdic.txt'
    url = 'http://www.denisowski.org/Esperanto/ESPDIC/espdic.txt'
    delimiter = ':'
    backup_delimiter = ';'  # I wish this wasn't necessary, but there's at least one line that uses ;
    definition_delimiter = '|||'

    def _read_and_convert_data(self) -> Iterable[Tuple[str, str]]:
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

        return ((word, self.definition_delimiter.join(defs)) for word, defs in definitions.items())

    def _parse_word_content(self, word: str, content: str) -> Dict[str, Value]:
        return {
            DEFINITIONS: StringListValue(content.split(self.definition_delimiter)),
            PART_OF_SPEECH: StringValue(self._infer_pos(word))
        }


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




