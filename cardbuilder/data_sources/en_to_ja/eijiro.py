from collections import defaultdict
from typing import Any, Dict, List, Tuple, Optional

from cardbuilder import CardBuilderException
from cardbuilder.common import ExternalDataDependent, fieldnames
from cardbuilder.data_sources import DataSource, Value
from cardbuilder.common.util import fast_linecount, loading_bar
import re
from string import digits
digitset = set(digits)


class Eijiro(DataSource, ExternalDataDependent):

    uses_data_dir = False

    # https://www.eijiro.jp/spec.htm

    line_head_symbol = '■'
    entry_delimiter = ':'  # also splits english/japanese in example sentences

    example_sentence_symbol = '■・'
    additional_explanation_symbol = '◆'
    pronunciation_symbol = '【発音】'
    pronunciation_important_symbol = '【発音！】'
    katakana_reading_symbol = '【＠】'
    inflections_symbol = '【変化】'
    level_symbol = '【レベル】'
    word_split_symbol = '【分節】'

    content_sectioning_symbol_map = {
        example_sentence_symbol: fieldnames.EXAMPLE_SENTENCES,
        additional_explanation_symbol: fieldnames.SUPPLEMENTAL,
        pronunciation_symbol: fieldnames.PRONUNCIATION_IPA,
        pronunciation_important_symbol: fieldnames.PRONUNCIATION_IPA,
        katakana_reading_symbol: fieldnames.KATAKANA,
        inflections_symbol: fieldnames.INFLECTIONS,
        level_symbol: 'level',
        word_split_symbol: 'split'
    }

    content_sectioning_symbols = set(content_sectioning_symbol_map.keys())

    content_sectioning_regex = re.compile(r'({})'.format('|'.join(re.escape(x) for x in content_sectioning_symbols)))

    link_symbol = '<→'
    blank_indirect_obj = '__'
    blank_direct_obj = '‾'

    header_pos_regex = re.compile(r'\{.+\}')

    pos_dictionary = {key[1:-1]: value for key, value in {
        '{名}': '名詞',
        '{代}': '代名詞',
        '{形}': '形容詞',
        '{動}': '動詞',
        '{他動}': '他動詞',
        '{自動}': '自動詞',
        '{助}': '助動詞',
        '{句動}': '句動詞',
        '{副}': '副詞',
        '{接}': '接続詞',
        '{間}': '間投詞',
        '{前}': '前置詞',
        '{略}': '略語',
        '{組織}': '組織名（会社名、団体名など）',
        '【反】': '反意語',
        '【対】': '対語',
        '【名】': '名詞形',
        '【類】': '類語',
        '【動】': '動詞形',
        '【同】': '同意語',
        '《イ》': 'インターネット',
        '《コ》': 'コンピュータ',
        '《レ》': 'レターやEメールの文例',
        '《医》': '医学',
        '《薬》': '薬学',
        '《化》': '化学',
        '〈米〉': 'アメリカ英語',
        '〈英〉': 'イギリス英語',
        '〈豪〉': 'オーストラリア英語',
        '〈NZ〉': 'ニュージーランド英語',
        '〈アイル〉': 'アイルランド方言',
        '〈スコ〉': 'スコットランド方言',
        '〈俗〉': '俗語',
        '〈米俗〉': 'アメリカの俗語',
        '〈話〉': '話し言葉（口語表現）',
        '〈文〉': '文語（書き言葉）',
        '〈米話〉': 'アメリカの話し言葉（口語表現）',
        '〈野球俗〉': '野球で使われる俗語',
        '〈米海軍俗〉': '米海軍で使われる俗語'
    }.items()}

    def _fetch_remote_files_if_necessary(self):
        pass  # No remote files to fetch, takes an explicit file location

    def __init__(self, eijiro_location: str):
        self.file_loc = eijiro_location
        self.dict_data = self.get_data()

    def lookup_word(self, word: str) -> Dict[str, Value]:
        return self.dict_data[word]

    @staticmethod
    def parse_line(line: str) -> Tuple[str, Optional[str], Dict[str, List[str]]]:
        results = defaultdict(list)
        header_end = line.index(Eijiro.entry_delimiter)
        header = line[1:header_end].strip()  # start at 1 to drop the ■
        content = line[header_end+1:].strip()

        if content.startswith(Eijiro.line_head_symbol):
            pass #TODO: this is a link to another entry - use it?

        pos_marking_match = next(Eijiro.header_pos_regex.finditer(header), None)
        if pos_marking_match is not None:
            pos_content = pos_marking_match.group(0)[1:-1]
            word = header[:pos_marking_match.start()].strip()
            if '-' in pos_content:
                pos = next(x.strip() for x in pos_content.split('-') if x.strip() not in digitset)
                pos = Eijiro.pos_dictionary.get(pos, pos)
            else:
                pos = pos_content.strip()
        else:
            word = header.strip()
            pos = None

        content_sections = Eijiro.content_sectioning_regex.split(content)
        if content_sections[0] not in Eijiro.content_sectioning_symbols:
            results[fieldnames.DEFINITIONS].append(content_sections.pop(0))

        section_header = None
        for section in content_sections:
            if section_header is None and section in Eijiro.content_sectioning_symbols:
                section_header = section
            elif section_header is not None and section not in Eijiro.content_sectioning_symbols:
                key = Eijiro.content_sectioning_symbol_map[section_header]
                results[key].append(section)
                section_header = None
            else:
                raise CardBuilderException('Unexpected sectioning sequence in Eijiro dictionary')

        return word, pos, results

    def _read_data(self) -> Any:
        results = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        lines = fast_linecount(self.file_loc)
        for line in loading_bar(open(self.file_loc, 'r'), 'parsing eijiro', lines):
            word, pos, data_dict = self.parse_line(line)
            for key, value in data_dict.items():
                results[word][pos][key].extend(value)

        return results





