import sqlite3
from glob import glob
from os.path import exists
from typing import Iterable, Tuple, List, Optional

import requests
from lxml import html

from cardbuilder.common import Fieldname, Language
from cardbuilder.common.util import log, InDataDir, loading_bar, DATABASE_NAME
from cardbuilder.input.word import WordForm, Word
from cardbuilder.input.word_list import WordList
from cardbuilder.lookup.data_source import ExternalDataDataSource
from cardbuilder.lookup.en import WordFrequency
from cardbuilder.lookup.lookup_data import outputs, LookupData
from cardbuilder.lookup.value import SingleValue


@outputs({
    Fieldname.SUPPLEMENTAL: SingleValue
})
class SvlWords(WordList, ExternalDataDataSource):
    """A wordlist which provides the 12000 word long Standard Vocabulary List words. Words are ordered by level, and
    then by word frequency within level (by default). If word frequency ordering is disabled, word order within levels
    is as retrieved - effectively random. Unusually, this class can also be used as a data source (for word level)
    """

    def _read_and_convert_data(self) -> Iterable[Tuple[str, str]]:
        filenames_with_level = sorted(((fname, int(fname.split('.')[0].split('_')[-1:][0])) for fname in glob('svl_*')),
                                      key=lambda x: x[1])
        for name, level in filenames_with_level:
            with open(name, 'r', encoding='utf-8') as f:
                words = [x.strip() for x in f.readlines()]

                for word in words:
                    yield word, level

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        return self.lookup_data_type(word, form, str(content), {
            Fieldname.SUPPLEMENTAL: SingleValue(str(content))
        })

    def _fetch_remote_files_if_necessary(self):
        files_with_index = [('svl_lvl_{}.txt'.format(i), i) for i in range(1, 13)]
        download_targets = [(filename, index) for filename, index in files_with_index if not exists(filename)]
        if len(download_targets) > 0:
            log(self, 'Some SVL files not found - downloading...')
            for filename, index in loading_bar(download_targets, 'downloading svl files'):
                if not exists(filename):
                    numstring = '0{}'.format(index) if index < 10 else str(index)
                    url = 'http://web.archive.org/web/20081219085635/http://www.alc.co.jp/goi/svl_l{}_list.htm'.format(
                        numstring)
                    page = requests.get(url)
                    tree = html.fromstring(page.content)
                    containing_element = next(x for x in tree.xpath('//font') if len(x) > 900)
                    entries = {x.tail.strip() for x in containing_element if x.tag == 'br'}
                    if containing_element.text is not None:
                        entries.add(containing_element.text.strip())
                    assert (len(entries) == 1000)
                    with open(filename, 'w+', encoding='utf-8') as f:
                        f.writelines(x + '\n' for x in entries)

    def __init__(self, order_by_wordfreq: bool = True, additional_forms: Optional[List[WordForm]] = None):
        with InDataDir():
            self.conn = sqlite3.connect(DATABASE_NAME)

            self.default_table = type(self).__name__.lower()
            self.conn.execute('''CREATE TABLE IF NOT EXISTS {}(
                word TEXT PRIMARY KEY,
                content INT
            );'''.format(self.default_table))
            self.conn.commit()

            self._fetch_remote_files_if_necessary()
            self._load_data_into_database()

        c = self.conn.execute('SELECT word, content from {}'.format(self.default_table))

        all_words_with_level = list(c.fetchall())
        if order_by_wordfreq:
            word_freq = WordFrequency()
            all_words_with_level = sorted(all_words_with_level, key=lambda tpl: (tpl[1], -word_freq[tpl[0]]))
        ordered_input_forms = [word for word, level in all_words_with_level]
        super().__init__(ordered_input_forms, Language.ENGLISH, additional_forms)










