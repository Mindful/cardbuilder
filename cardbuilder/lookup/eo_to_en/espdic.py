from typing import Iterable, Tuple
from collections import defaultdict

from cardbuilder.input.word import Word
from cardbuilder.lookup.lookup_data import lookup_data_type_factory, LookupData
from cardbuilder.lookup.value import StringValue, StringListValue
from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.lookup.data_source import ExternalDataDataSource


class ESPDIC(ExternalDataDataSource):

    filename = 'espdic.txt'
    url = 'http://www.denisowski.org/Esperanto/ESPDIC/espdic.txt'
    delimiter = ':'
    backup_delimiter = ';'  # I wish this wasn't necessary, but there's at least one line that uses ;
    definition_delimiter = '|||'

    lookup_data_type = lookup_data_type_factory('ESPDICLookupData', {Fieldname.DEFINITIONS, Fieldname.PART_OF_SPEECH})

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

    def parse_word_content(self, word: Word, form: str, content: str) -> LookupData:
        return self.lookup_data_type(word, form, {
            Fieldname.DEFINITIONS: StringListValue(content.split(self.definition_delimiter)),
            Fieldname.PART_OF_SPEECH: StringValue(self._infer_pos(form))
        })

    def _infer_pos(self, word: str):
        #TODO: this probably needs to be smarter than it is
        # possibly look at https://github.com/fidelisrafael/esperanto-analyzer ?
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




