import os
from typing import Any, Dict, Union, List

from common import DATA_DIR, ExternalDataDependent, WordLookupException, WORD, DEFINITIONS
from data_sources import DataSource

GENE_DICT = os.path.join(DATA_DIR, 'gene_dict.txt')


class GeneDict(DataSource, ExternalDataDependent):
    supplemental_data_delim = '     '
    expected_first_element = '!'

    def _fetch_remote_files_if_necessary(self):
        pass #TODO

    @staticmethod
    def _read_data() -> Any:
        pass #TODO

    def __init__(self):
        self.definitions = {}
        self.supplemental = {}

        found_first_valid_line = False
        reading_word = True
        for line in open(GENE_DICT):
            if not found_first_valid_line:
                if line[0] == self.expected_first_element:
                    found_first_valid_line = True
                else:
                    continue

            if reading_word:
                word_line_content = line.split(self.supplemental_data_delim)
                word = word_line_content[0].strip()
                if len(word_line_content) > 1:
                    self.supplemental[word] = word_line_content[1].strip()
                reading_word = False
            else:  # we're reading a definition line
                self.definitions[word] = line.strip()
                reading_word = True

    def lookup_word(self, word: str) -> Dict[str, Union[str, List[str]]]:
        if word not in self.definitions:
            raise WordLookupException("Could not find {} in Gene dictionary".format(word))
        result = {
            WORD: word,
            DEFINITIONS: [self.definitions[word]]
        }
        if word in self.supplemental:
            result['supplemental'] = self.supplemental[word]

        return result