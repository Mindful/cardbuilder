import tarfile
from json import dumps, loads
from os.path import exists
from typing import Iterable, Tuple

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.util import log, download_to_stream_with_loading_bar
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import ExternalDataDataSource
from cardbuilder.lookup.lookup_data import outputs, LookupData
from cardbuilder.lookup.value import SingleValue


@outputs({
    Fieldname.DEFINITIONS: SingleValue,
    Fieldname.SUPPLEMENTAL: SingleValue,
    Fieldname.EXAMPLE_SENTENCES: SingleValue
})
class GeneDict(ExternalDataDataSource):
    """The DataSource for the GENE95 dictionary (http://www.namazu.org/~tsuchiya/sdic/data/gene.html)
    Definitions are returned as a single line of text, because while definitions are usually delimited with a comma,
    this does not hold true all the time."""

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
        for line in open(self.filename, encoding='utf-8'):
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
            data = {Fieldname.DEFINITIONS: definitions[word]}
            if word in supplemental:
                data[Fieldname.SUPPLEMENTAL] = supplemental[word]
            if word in examples:
                data[Fieldname.EXAMPLE_SENTENCES] = examples[word]
            yield word, dumps({key.name: val for key, val in data.items()})

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        return self.lookup_data_type(word, form, content, {
            Fieldname[key]: SingleValue(val) for key, val in loads(content).items()
        })

    def _fetch_remote_files_if_necessary(self):
        if not exists(self.filename):
            log(self, '{} not found - downloading and extracting...'.format(self.filename))
            stream = download_to_stream_with_loading_bar(self.url)
            tar = tarfile.open(fileobj=stream, mode='r:gz')
            gene_data = tar.extractfile('gene.txt').read().decode('shift_jisx0213')
            with open(self.filename, 'w+', encoding='utf-8') as f:
                f.write(gene_data)


