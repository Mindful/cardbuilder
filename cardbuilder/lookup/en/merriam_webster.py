import re
from json import loads
from typing import Optional, List, Tuple

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from cardbuilder.common.config import Config
from cardbuilder.common import Fieldname
from cardbuilder.common.util import log
from cardbuilder.exceptions import WordLookupException, CardBuilderUsageException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import WebApiDataSource, AggregatingDataSource
from cardbuilder.lookup.lookup_data import LookupData, outputs
from cardbuilder.lookup.value import MultiListValue, ListValue


@outputs({
    Fieldname.SYNONYMS: MultiListValue,
    Fieldname.ANTONYMS: MultiListValue,
    Fieldname.AUDIO: MultiListValue,
    Fieldname.PART_OF_SPEECH: ListValue,
    Fieldname.INFLECTIONS: MultiListValue
})
class ScrapingMerriamWebster(WebApiDataSource):

    synonyms_name = 'synonyms'
    antonyms_name = 'antonyms'

    pos_cleaning_regex = re.compile(r"[^a-zA-Z]")

    def _query_api(self, form: str) -> str:
        url = 'https://www.merriam-webster.com/dictionary/{}'.format(form)
        # custom Accept-Encoding header is very important: without it, MW sometimes returns redirect loops
        # (this happens for example with "science")
        html = requests.get(url, headers={'Accept-Encoding': 'identity'}).content
        return str(html)

    #TODO: throw lookup exception if we can't find anything/content is empty (right now we just return empty data?)
    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        parsed = BeautifulSoup(content, 'html.parser')

        rows = parsed.find_all('div', {'class': 'row'})
        audio_list = []
        inflections_list = []
        parts_of_speech = []
        for row in rows:
            if 'entry-header' in row['class']:
                word_elem = row.find(attrs={'class': 'hword'})
                if word_elem is None or word_elem.text != form:
                    word = None
                    pos = None
                    continue
                else:
                    word = word_elem.text

                pos_elem = row.find('a', {'class': 'important-blue-link'})
                if pos_elem is not None:  # definitions under "more definitions" sometimes lack a POS
                    pos = self.pos_cleaning_regex.sub('', pos_elem.text)
                    parts_of_speech.append(self.pos_cleaning_regex.sub('', pos_elem.text))
                else:
                    pos = None
            elif 'entry-attr' in row['class'] or 'headword-row' in row['class'] and pos is not None:
                audio_links = []
                audio_content = row.find_all('a', {'class': 'play-pron'})
                for audio_element in audio_content:
                    audio_links.append(LearnerDictionary.get_word_pronunciation_url(audio_element['data-file']))

                inflection_content = row.find_all('span', {'class': 'if'})
                inflections = [x.text for x in inflection_content]

                if len(audio_links) > 0:
                    audio_list.append((audio_links, pos))

                if len(inflections) > 0:
                    inflections_list.append((inflections, pos))

        synonym_list = []
        antonym_list = []

        syn_ant_div = parsed.find('div', {'id': 'synonyms-anchor'})

        if syn_ant_div:
            for elem in syn_ant_div:
                if isinstance(elem, Tag):
                    if elem.has_attr('class') and "function-label" in elem['class']:
                        header_text_list = elem.text.split(':')
                        if len(header_text_list) > 1:
                            relation, pos = header_text_list
                        else:
                            relation = header_text_list[0]
                            pos = None

                        relation = relation.lower()

                    elif elem.has_attr('class') and elem.name == 'ul':
                        list_contents = [x.text for x in elem.find_all('a')]
                        if relation == self.synonyms_name:
                            synonym_list.append((list_contents, pos))
                        elif relation == self.antonyms_name:
                            antonym_list.append((list_contents, pos))

        return self.lookup_data_type(word, form, content, {
            Fieldname.PART_OF_SPEECH: ListValue(parts_of_speech),
            Fieldname.AUDIO: MultiListValue(audio_list),
            Fieldname.INFLECTIONS: MultiListValue(inflections_list),
            Fieldname.SYNONYMS: MultiListValue(synonym_list),
            Fieldname.ANTONYMS: MultiListValue(antonym_list)
        })


@outputs({
    Fieldname.SYNONYMS: MultiListValue,
    Fieldname.ANTONYMS: MultiListValue
})
class CollegiateThesaurus(WebApiDataSource):
    # https://dictionaryapi.com/products/api-collegiate-thesaurus

    def __init__(self, api_key):
        super().__init__()
        log(self, 'initializing Collegiate Thesaurus with api key {}'.format(api_key))
        self.api_key = api_key

    def _query_api(self, word) -> str:
        url = 'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key={api_key}'.format(
            word=word, api_key=self.api_key
        )
        return requests.get(url).text

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        raw_json = loads(content)

        # thesaurus sometimes returns invalid data, such as for "percent", which returns a list like
        # ["perching","decent","percentage","descent","parchment","recent"]
        if not all(isinstance(x, dict) for x in raw_json):
            raise WordLookupException('Collegeiate Thesaurus returned invalid data for word "{}"'.format(form))
        target_words = [x for x in raw_json if x['meta']['id'].split(':')[0] == form]
        if len(target_words) == 0:
            raise WordLookupException('Merriam Webster collegiate thesaurus had no exact matches for {}'.format(form))

        syns_with_pos = []
        ants_with_pos = []

        # we only take the first set of synonyms/antonyms per part of speech; at some point it's just overkill
        for word_data in target_words:
            pos = word_data['fl']
            syns_with_pos.append((word_data['meta']['syns'][0] if len(word_data['meta']['syns']) > 0 else [], pos))
            ants_with_pos.append((word_data['meta']['ants'][0] if len(word_data['meta']['ants']) > 0 else [], pos))

        return self.lookup_data_type(word, form, content, {
            Fieldname.SYNONYMS: MultiListValue(syns_with_pos),
            Fieldname.ANTONYMS: MultiListValue(ants_with_pos),
        })


@outputs({
    Fieldname.PART_OF_SPEECH: ListValue,
    Fieldname.DEFINITIONS: MultiListValue,
    Fieldname.PRONUNCIATION_IPA: MultiListValue,
    Fieldname.INFLECTIONS: MultiListValue,
    Fieldname.AUDIO: MultiListValue
})
class LearnerDictionary(WebApiDataSource):
    # https://dictionaryapi.com/products/api-learners-dictionary

    audio_file_format = 'mp3'
    number_subdir_regex = re.compile(r'^[^a-zA-Z]+')
    # this is fairly aggressive - for example it entirely erases "{it} chiefly US {/it}"
    formatting_marker_regex = re.compile(r'{.*}')

    def __init__(self, api_key):
        super().__init__()
        log(self, 'initializing Learner\'s Dictionary with api key {}'.format(api_key))
        self.api_key = api_key

    def _query_api(self, word) -> str:
        url = 'https://www.dictionaryapi.com/api/v3/references/learners/json/{word}?key={api_key}'.format(
            word=word, api_key=self.api_key)
        return requests.get(url).text

    def _get_pronunciation_content(self, pronunciation_data: List) -> Tuple[List, List]:
        pronunciation_url_list = []
        ipa_list = []

        for pronunciation_entry in pronunciation_data:
            if 'ipa' in pronunciation_entry:
                ipa_list.append(pronunciation_entry['ipa'].strip())
            if 'sound' in pronunciation_entry:
                pronunciation_url_list.append(self.get_word_pronunciation_url(
                    pronunciation_entry['sound']['audio']))

        return ipa_list, pronunciation_url_list

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        raw_json = loads(content)

        # MW occasionally just returns a list of words, not actual data...
        if any(not isinstance(val, dict) for val in raw_json):
            raise WordLookupException('Learner\'s Dictionary returned invalid data for word "{}"'.format(form))
        else:
            target_words = [x for x in raw_json if x['meta']['id'].split(':')[0] == form]

        if len(target_words) == 0:
            # If we can find the target word as an "undefined run-on" of one of the results, use that data instead
            for word_json in raw_json:
                if 'uros' in word_json:
                    target_word = next((json for json in word_json['uros'] if json['ure'].replace('*', '') == form),
                                       None)
                    if target_word is not None:
                        pos_label = None
                        output = {}
                        if 'fl' in target_word:
                            pos_label = target_word['fl']
                            # There's only going to be one POS, but this has to be a StringListValue anyway
                            output[Fieldname.PART_OF_SPEECH] = ListValue([target_word['fl']])

                        if 'prs' in target_word:
                            pronunciation_data = target_word['prs']
                            ipa_list, pronunciation_url_list = self._get_pronunciation_content(pronunciation_data)
                            output[Fieldname.AUDIO] = MultiListValue([(pronunciation_url_list, pos_label)])
                            output[Fieldname.PRONUNCIATION_IPA] = MultiListValue([(ipa_list, pos_label)])

                        if len(output) > 0:
                            return self.lookup_data_type(word, content, form, output)

            raise WordLookupException('Merriam Webster learner\'s dictionary had no matches for {}'.format(form))

        pos_list = []
        ipa_with_pos = []
        inflections_with_pos = []
        audio_with_pos = []
        definitions_with_pos = []
        for word_data in target_words:
            metadata = word_data['meta']
            shortdef = metadata['app-shortdef']
            if not shortdef:
                continue
            pos_label = shortdef['fl']
            if 'prs' in word_data['hwi']:
                ipa_list, pronunciation_url_list = self._get_pronunciation_content(word_data['hwi']['prs'])
                if len(pronunciation_url_list) > 0:
                    audio_with_pos.append((pronunciation_url_list, pos_label))
                if len(ipa_list) > 0:
                    ipa_with_pos.append((ipa_list, pos_label))

            inflections = [x['if'].replace('*', '') for x in word_data['ins']
                           if 'if' in x] if 'ins' in word_data else []
            if len(inflections) > 0:
                inflections_with_pos.append((inflections, pos_label))

            definitions = [d for d in (self.formatting_marker_regex.sub('', x) for x in shortdef['def']) if d]
            if len(definitions) > 0:
                definitions_with_pos.append((definitions, pos_label))
            pos_list.append(pos_label)

        out = {
            Fieldname.PART_OF_SPEECH: ListValue(pos_list),
            Fieldname.DEFINITIONS: MultiListValue(definitions_with_pos),
            Fieldname.PRONUNCIATION_IPA: MultiListValue(ipa_with_pos),
            Fieldname.INFLECTIONS: MultiListValue(inflections_with_pos),
        }

        if len(audio_with_pos) > 0:
            out[Fieldname.AUDIO] = MultiListValue(audio_with_pos)

        return self.lookup_data_type(word, form, content, out)

    @classmethod
    def get_word_pronunciation_url(cls, filename) -> str:
        if filename.startswith('bix'):
            subdir = 'bix'
        elif filename.startswith('gg'):
            subdir = 'gg'
        elif cls.number_subdir_regex.match(filename):
            subdir = 'number'
        else:
            subdir = filename[0]
        url = 'https://media.merriam-webster.com/audio/prons/en/us/{format}/{subdir}/{filename}.{format}'.format(
            format=cls.audio_file_format, subdir=subdir, filename=filename
        )

        return url


@outputs({
    **LearnerDictionary.lookup_data_type.fields(), **CollegiateThesaurus.lookup_data_type.fields()
})
class MerriamWebster(AggregatingDataSource):
    # https://dictionaryapi.com/products/json
    # Each lookup here is two requests to MW; be careful if using an account limited to 1000/day

    keylike = re.compile(r'.+-.+-.+-.+')

    learners_api_conf_name = 'mw_learners_api_key'
    thesaurus_api_conf_name = 'thesaurus_api_key'

    def __init__(self, learners_api_key: Optional[str] = None, thesaurus_api_key: Optional[str] = None,
                 pos_in_definitions=False):
        api_keys = []
        for idx, key in enumerate([learners_api_key, thesaurus_api_key]):
            key_name = self.learners_api_conf_name if idx == 0 else self.thesaurus_api_conf_name
            if key is None:
                try:
                    api_key = Config.get(key_name)
                except KeyError:
                    raise CardBuilderUsageException('MerriamWebster was passed None for an API key but could not'
                                                    'find it in the config database. Please pass in a key')
            else:
                if self.keylike.match(key) and '.' not in key:
                    log(self, '{} looks like API key - using it'.format(key))
                    api_key = key
                else:
                    with open(key, encoding='utf-8') as f:
                        api_key = f.readlines()[0]
                    log(self, 'read API key {} from file {} - using it'.format(api_key, key))
                Config.set(key_name, api_key)

            api_keys.append(api_key)

        # deliberately don't call super().__init__() because MW doesn't need an sqlite table
        # the learners dict and thesaurus have their own tables
        log(self, 'Instantiating {} dictionary with owernship of {} and {}'.format(
            *(x.__name__ for x in (MerriamWebster, LearnerDictionary, CollegiateThesaurus))))
        self.learners_dict = LearnerDictionary(api_keys[0])
        self.thesaurus = CollegiateThesaurus(api_keys[1])
        self.pos_in_definitions = pos_in_definitions

    def __del__(self):
        pass  # no need to close any database connections like DataSource does

    def lookup_word(self, word: Word, form: str, following_link: bool = False) -> LookupData:
        dictionary_data = self.learners_dict.lookup_word(word, form)

        output = dictionary_data.get_data()
        try:  # thesaurus gags an awful lot
            thesaurus_data = self.thesaurus.lookup_word(word, form)
            output = {
                **output, **thesaurus_data.get_data()
            }
            content = dictionary_data.get_raw_content() + self.aggregated_content_delimiter \
                      + thesaurus_data.get_raw_content()
        except WordLookupException:
            content = dictionary_data.get_raw_content()

        return self.lookup_data_type(word, form, content, output)
