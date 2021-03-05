from collections import defaultdict
from os.path import abspath
from typing import Any, Dict, List, Tuple, Optional, Iterable

from cardbuilder import CardBuilderException
from cardbuilder.common import fieldnames
from cardbuilder.data_sources import Value
from cardbuilder.common.util import fast_linecount, loading_bar
import re
from string import digits

from cardbuilder.data_sources.data_source import ExternalDataDataSource

digitset = set(digits)


class Eijiro(ExternalDataDataSource):
    # https://www.eijiro.jp/spec.htm

    line_head_symbol = '■'
    entry_delimiter = ' : ' #TODO: : also splits JP/Eng example sentences, but not sure if that case has spaces

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

    header_data_delimiter = '⦀'
    line_data_delimiter = '⚬'

    def _read_and_convert_data(self) -> Iterable[Tuple[str, str]]:
        lines = fast_linecount(self.file_loc)
        prev_word = None
        prev_content = None
        for line in loading_bar(open(self.file_loc, 'r'), 'reading eijiro', lines):
            header_end = line.index(Eijiro.entry_delimiter)
            header = line[1:header_end].strip()  # start at 1 to drop the ■
            content = line[header_end + 1:].strip()

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

            if pos is not None:
                content = self.header_data_delimiter.join((pos, content))

            if prev_word is not None and prev_content is not None:
                # the .lower() here is necessary because sometimes there are sequential entries that go back and forth
                # on case, like "the" -> "The" -> "the". As is, we end up using the case attached to the last entry
                if word.lower() == prev_word.lower():
                    content = self.line_data_delimiter.join((content, prev_content))
                else:
                    yield prev_word, prev_content

            prev_word = word
            prev_content = content

        yield prev_word, prev_content

    def _parse_word_content(self, word: str, content: str) -> Dict[str, Value]:
        results = defaultdict(list)
        if content.startswith(Eijiro.line_head_symbol):
            pass  # TODO: this is a link - just query for the linked word instead

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

        return results #TODO: this is strings, should be Values

    def _fetch_remote_files_if_necessary(self):
        pass  # No remote files to fetch, takes an explicit file location

    def __init__(self, eijiro_location: str):
        self.file_loc = abspath(eijiro_location)
        super().__init__()




