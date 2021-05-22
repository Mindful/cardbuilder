import csv
import sqlite3
from typing import Iterable, Tuple

from cardbuilder.common import Fieldname
from cardbuilder.common.util import fast_linecount, InDataDir, loading_bar, log, DATABASE_NAME, retry_with_logging
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import ExternalDataDataSource
from cardbuilder.lookup.lookup_data import LookupData, outputs
from cardbuilder.lookup.value import SingleValue


@outputs({
    Fieldname.SUPPLEMENTAL: SingleValue
})
class WordFrequency(ExternalDataDataSource):
    # https://norvig.com/ngrams/
    url = 'http://norvig.com/ngrams/count_1w.txt'
    filename = 'count_1w.txt'

    content_type = 'INT'

    def __init__(self):
        super(WordFrequency, self).__init__()

        log(self, 'Loading word frequency data from table...')
        c = self.conn.execute('''SELECT * FROM {}'''.format(self.default_table))
        self.frequency = dict(c.fetchall())

    def lookup_word(self, word: Word, form: str, following_link: bool = False) -> LookupData:
        if form not in self.frequency:
            raise WordLookupException('No frequency information for {}'.format(form))

        content = str(self[form])
        return self.lookup_data_type(word, form, content, {
            Fieldname.SUPPLEMENTAL: SingleValue(content),
        })

    def _read_and_convert_data(self) -> Iterable[Tuple[str, int]]:
        frequency = {}
        with InDataDir():
            line_count = fast_linecount(self.filename)
            with open(self.filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                for word, freq in loading_bar(reader, 'reading {}'.format(self.filename), line_count):
                    frequency[word] = int(freq)

        return frequency.items()

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        pass

    def __getitem__(self, word: str) -> int:
        return self.frequency.get(word.lower(), 0)

