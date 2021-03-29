import sqlite3
from glob import glob
from os.path import exists
from typing import Dict, Iterable, Tuple, List, Optional

import requests
from lxml import html

from cardbuilder.common.fieldnames import SUPPLEMENTAL
from cardbuilder.common.languages import ENGLISH
from cardbuilder.common.util import log, InDataDir, loading_bar, DATABASE_NAME
from cardbuilder.data_sources.value import Value, StringValue
from cardbuilder.data_sources.data_source import ExternalDataDataSource
from cardbuilder.data_sources.en_to_en import WordFrequency
from cardbuilder.word_lists import WordList
from cardbuilder.word_lists.word import WordForm


class SvlWords(WordList, ExternalDataDataSource):
    def _read_and_convert_data(self) -> Iterable[Tuple[str, str]]:
        filenames_with_level = sorted(((fname, int(fname.split('.')[0].split('_')[-1:][0])) for fname in glob('svl_*')),
                                      key=lambda x: x[1])
        for name, level in filenames_with_level:
            with open(name, 'r') as f:
                words = [x.strip() for x in f.readlines()]

                for word in words:
                    yield word, level

    def _parse_word_content(self, word: str, content: int) -> Dict[int, Value]:
        return {
            SUPPLEMENTAL: StringValue(str(content))
        }

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
                    with open(filename, 'w+') as f:
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
        super().__init__(ordered_input_forms, ENGLISH, additional_forms)










