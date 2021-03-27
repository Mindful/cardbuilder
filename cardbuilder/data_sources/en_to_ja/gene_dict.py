import tarfile
from os.path import exists
from typing import Dict, Iterable, Tuple
from json import dumps, loads

from cardbuilder.common.util import log, download_to_stream_with_loading_bar
from cardbuilder.common.fieldnames import DEFINITIONS, SUPPLEMENTAL, EXAMPLE_SENTENCES
from cardbuilder.data_sources.value import Value, StringValue
from cardbuilder.data_sources.data_source import ExternalDataDataSource


class GeneDict(ExternalDataDataSource):
    supplemental_data_delim = '     '
    example_sentence_delim = ' / '
    expected_first_element = '!'
    filename = 'gene_dict.txt'
    url = 'http://www.namazu.org/~tsuchiya/sdic/data/gene95.tar.gz'

    def _read_and_convert_data(self) -> Iterable[Tuple[str, str]]:
        definitions = {}
        supplemental = {}
        examples = {}

        found_first_valid_line = False
        reading_word = True
        for line in open(self.filename):
            if not found_first_valid_line:
                if line[0] == self.expected_first_element:
                    found_first_valid_line = True
                else:
                    continue

            if reading_word:
                word_line_content = line.split(self.supplemental_data_delim)
                word = word_line_content[0].strip()
                if len(word_line_content) > 1:
                    supplemental[word] = word_line_content[1].strip()
                reading_word = False
            else:  # we're reading a definition line
                definition_line_list = line.strip().split(self.example_sentence_delim)
                definitions[word] = definition_line_list[0]
                if len(definition_line_list) > 1:
                    examples[word] = definition_line_list[1]
                reading_word = True

        for word in definitions:
            data = {DEFINITIONS: definitions[word]}
            if word in supplemental:
                data[SUPPLEMENTAL] = supplemental[word]
            if word in examples:
                data[EXAMPLE_SENTENCES] = examples[word]
            yield word, dumps(data)

    def _parse_word_content(self, word: str, content: str) -> Dict[str, Value]:
        return {key: StringValue(val) for key, val in loads(content).items()}

    def _fetch_remote_files_if_necessary(self):
        if not exists(self.filename):
            log(self, '{} not found - downloading and extracting...'.format(self.filename))
            stream = download_to_stream_with_loading_bar(self.url)
            tar = tarfile.open(fileobj=stream, mode='r:gz')
            gene_data = tar.extractfile('gene.txt').read().decode('shift_jisx0213')
            with open(self.filename, 'w+') as f:
                f.write(gene_data)


