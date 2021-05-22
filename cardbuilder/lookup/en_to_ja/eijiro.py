import re
from collections import defaultdict
from logging import WARNING
from os.path import abspath
from string import digits
from typing import Tuple, Iterable, Optional

from cardbuilder.common.config import Config
from cardbuilder.common import Fieldname
from cardbuilder.common.util import fast_linecount, loading_bar, log
from cardbuilder.exceptions import CardBuilderException, WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import ExternalDataDataSource
from cardbuilder.lookup.lookup_data import outputs, LookupData
from cardbuilder.lookup.value import LinksValue, MultiListValue

digitset = set(digits)

# these definitions live outside the eijiro class so they can be used in the @output definition
example_sentence_symbol = '■・'
additional_explanation_symbol = '◆'
pronunciation_symbol = '【発音】'
pronunciation_important_symbol = '【発音！】'
katakana_reading_symbol = '【＠】'
inflections_symbol = '【変化】'
level_symbol = '【レベル】'
word_split_symbol = '【分節】'
link_symbol = '＝<→'
second_link_symbol = '<→'  # links don't always start with =

content_sectioning_symbol_map = {
    example_sentence_symbol: Fieldname.EXAMPLE_SENTENCES,
    additional_explanation_symbol: Fieldname.SUPPLEMENTAL,
    pronunciation_symbol: Fieldname.PRONUNCIATION_IPA,
    pronunciation_important_symbol: Fieldname.PRONUNCIATION_IPA,
    katakana_reading_symbol: Fieldname.KATAKANA,
    inflections_symbol: Fieldname.INFLECTIONS,
    level_symbol: Fieldname.SUPPLEMENTAL,
    word_split_symbol: Fieldname.SUPPLEMENTAL,
    link_symbol: Fieldname.LINKS,
    second_link_symbol: Fieldname.LINKS
}


@outputs({**{Fieldname.LINKS: LinksValue, Fieldname.DEFINITIONS: MultiListValue},
          **{fname: MultiListValue for fname in content_sectioning_symbol_map.values() if fname != Fieldname.LINKS}})
class Eijiro(ExternalDataDataSource):
    # http://www.eijiro.jp/get-144.htm
    # https://www.eijiro.jp/spec.htm

    eijiro_conf_value = 'eijiro_loaded'

    line_head_symbol = '■'
    entry_delimiter = ' : '

    content_sectioning_symbols = set(content_sectioning_symbol_map.keys())

    content_sectioning_regex = re.compile(r'({})'.format('|'.join(re.escape(x) for x in content_sectioning_symbols)))

    # we don't currently use these two, but they're present in many headers
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
        if self.file_loc is None:
            raise FileNotFoundError('Must set Eijiro location the first time for data ingestion')
        lines = fast_linecount(self.file_loc)
        prev_word = None
        prev_content = None
        for line in loading_bar(open(self.file_loc, 'r', encoding='shift_jisx0213'), 'reading eijiro', lines):
            header_end = line.index(Eijiro.entry_delimiter)
            header = line[1:header_end].strip()  # start at 1 to drop the ■
            content = line[header_end + len(Eijiro.entry_delimiter):].strip()

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
                    content = self.line_data_delimiter.join((prev_content, content))
                    # if we've ever seen a lowercase form, hold onto it for lookup
                    prev_word = word if word.islower() else prev_word
                else:
                    yield prev_word, prev_content
                    prev_word = word
            else:
                prev_word = word

            prev_content = content

        yield prev_word, prev_content

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        lines = content.split(self.line_data_delimiter)
        line_parses = []
        for line in lines:
            line_attrs = defaultdict(list)

            if self.header_data_delimiter in line:
                header_data, line = line.split(self.header_data_delimiter)
                # only data in the header seems to be the POS
                line_attrs[Fieldname.PART_OF_SPEECH] = header_data

            content_sections = Eijiro.content_sectioning_regex.split(line)
            if content_sections[0] not in Eijiro.content_sectioning_symbols:
                leading_content = content_sections.pop(0)
                if leading_content:  # leading content is sometimes empty, don't want to add blank definitions
                    line_attrs[Fieldname.DEFINITIONS].append(leading_content)

            section_header = None
            for section in content_sections:
                if section_header is None and section in Eijiro.content_sectioning_symbols:
                    section_header = section
                elif section_header is not None and section not in Eijiro.content_sectioning_symbols:
                    key = content_sectioning_symbol_map[section_header]
                    if key == Fieldname.LINKS:
                        if not following_link:
                            linked_word = section[:section.index('>')]
                            try:
                                line_attrs[Fieldname.LINKS].append(self.lookup_word(word, linked_word,
                                                                                    following_link=True))
                            except WordLookupException:
                                log(self, 'Found link to apparently missing word "{}" in definition of word "{}"'.format(
                                    linked_word, form
                                ), WARNING)
                    else:
                        line_attrs[key].append(section.strip('、'))

                    section_header = None
                else:
                    raise CardBuilderException('Unexpected sectioning sequence in Eijiro dictionary')

            line_parses.append(line_attrs)

        aggregated_parse = defaultdict(lambda: defaultdict(list))
        links = []
        for val_map in line_parses:
            pos = val_map.get(Fieldname.PART_OF_SPEECH, None)
            if Fieldname.LINKS in val_map:
                links.extend(val_map[Fieldname.LINKS])
            for key, val in ((k, v) for k, v in val_map.items() if k != Fieldname.PART_OF_SPEECH
                                                                   and k != Fieldname.LINKS):
                aggregated_parse[key][pos].extend(val)

        output = {}
        if links:
            output[Fieldname.LINKS] = LinksValue(links)
        for val_key, val_dict in aggregated_parse.items():
            output[val_key] = MultiListValue([([val for val in vals if val], pos) for pos, vals in val_dict.items()])

        if Fieldname.LINKS in output:
            for linked_word_dict in output[Fieldname.LINKS].get_data():
                for key, value in linked_word_dict.get_data().items():
                    if (key not in output or not output[key].get_data()) and key in Fieldname.link_friendly_fields():
                        output[key] = value

        return self.lookup_data_type(word, form, content, output)

    def _fetch_remote_files_if_necessary(self):
        pass  # No remote files to fetch, takes an explicit file location

    def __init__(self, eijiro_location: Optional[str] = None):
        if eijiro_location is not None:
            self.file_loc = abspath(eijiro_location)
            Config.set(self.eijiro_conf_value, 'yes')
        else:
            self.file_loc = None
        super().__init__()
