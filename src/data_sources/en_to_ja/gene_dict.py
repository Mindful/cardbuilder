import os
from typing import Any, Dict, Union, List
from common import DATA_DIR, ExternalDataDependent, WordLookupException, WORD, DEFINITIONS, log
from os.path import exists
import requests
from data_sources import DataSource
import tarfile
from io import BytesIO

GENE_DICT = os.path.join(DATA_DIR, 'gene_dict.txt')


class GeneDict(DataSource, ExternalDataDependent):
    supplemental_data_delim = '     '
    expected_first_element = '!'
    filename = 'gene_dict.txt'
    url = 'http://www.namazu.org/~tsuchiya/sdic/data/gene95.tar.gz'

    def _fetch_remote_files_if_necessary(self):
        if not exists(self.filename):
            log(self, '{} not found - downloading and extracting...'.format(self.filename))
            data = requests.get(self.url)
            filelike = BytesIO(data.content)
            tar = tarfile.open(fileobj=filelike, mode='r:gz')
            gene_data = tar.extractfile('gene.txt').read().decode('shift_jisx0213')
            with open(self.filename, 'w+') as f:
                f.write(gene_data)

    @staticmethod
    def _read_data() -> Any:
        definitions = {}
        supplemental = {}

        found_first_valid_line = False
        reading_word = True
        for line in open(GENE_DICT):
            if not found_first_valid_line:
                if line[0] == GeneDict.expected_first_element:
                    found_first_valid_line = True
                else:
                    continue

            if reading_word:
                word_line_content = line.split(GeneDict.supplemental_data_delim)
                word = word_line_content[0].strip()
                if len(word_line_content) > 1:
                    supplemental[word] = word_line_content[1].strip()
                reading_word = False
            else:  # we're reading a definition line
                definitions[word] = line.strip()
                reading_word = True

        return definitions, supplemental

    def __init__(self):
        self.definitions, self.supplemental = self.get_data()

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
