import csv
import sqlite3
from typing import Iterable, Tuple

from cardbuilder.common.fieldnames import Fieldname
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

    def __init__(self):
        # deliberately don't call super().__init__() because we have a custom table schema
        with InDataDir():
            self.conn = sqlite3.connect(DATABASE_NAME)
            retry_with_logging(self._fetch_remote_files_if_necessary, tries=2, delay=1)

        self.default_table = type(self).__name__.lower()
        self.conn.execute('''CREATE TABLE IF NOT EXISTS {}(
            word TEXT PRIMARY KEY,
            freq INT
        );'''.format(self.default_table))
        self.conn.commit()

        self._load_data_into_database()

        log(self, 'Loading word frequency data from table...')
        c = self.conn.execute('''SELECT * FROM {}'''.format(self.default_table))
        self.frequency = dict(c.fetchall())

    def lookup_word(self, word: Word, form: str) -> LookupData:
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
            with open(self.filename, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                for word, freq in loading_bar(reader, 'reading {}'.format(self.filename), line_count):
                    frequency[word] = int(freq)

        return frequency.items()

    def parse_word_content(self, word: Word, form: str, content: str) -> LookupData:
        pass

    def __getitem__(self, word: str) -> int:
        return self.frequency.get(word.lower(), 0)

