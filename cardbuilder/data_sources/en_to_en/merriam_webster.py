# https://dictionaryapi.com/products/json
import re
from typing import Dict, Union, List, Optional

import requests

from cardbuilder.common import fieldnames
from cardbuilder.data_sources import DataSource, Value, StringListValue, StringValue
from cardbuilder.data_sources.value import StringListsWithPOSValue, StringListsWithPrimaryPOSValue, RawDataValue, \
    StringsWithPosValue
from cardbuilder.exceptions import WordLookupException

WORD_ID = 'wid'

# https://dictionaryapi.com/products/api-collegiate-thesaurus
class CollegiateThesaurus(DataSource):
    def __init__(self, api_key):
        self.api_key = api_key

    def _query_api(self, word):
        url = 'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key={api_key}'.format(
            word=word, api_key=self.api_key
        )
        return requests.get(url).json()

    def lookup_word(self, word: str) -> Dict[str, Value]:
        raw_json = self._query_api(word)

        target_words = [x for x in raw_json if x['meta']['id'].split(':')[0] == word]
        if len(target_words) == 0:
            raise WordLookupException('Merriam Webster collegiate thesaurus had no exact matches for {}'.format(word))

        syns_with_pos = []
        ants_with_pos = []
        word_ids = []

        # we only take the first set of synonyms/antonyms per part of speech; at some point it's just overkill
        for word_data in target_words:
            pos = word_data['fl']
            word_ids.append(word_data['meta']['id'].split(':')[0] + '_' + pos)
            syns_with_pos.append((word_data['meta']['syns'][0] if len(word_data['meta']['syns']) > 0 else [], pos))
            ants_with_pos.append((word_data['meta']['ants'][0] if len(word_data['meta']['ants']) > 0 else [], pos))

        return {
            fieldnames.SYNONYMS: StringListsWithPOSValue(syns_with_pos),
            fieldnames.ANTONYMS: StringListsWithPOSValue(ants_with_pos),
            WORD_ID: StringListValue(word_ids),
            fieldnames.RAW_DATA: RawDataValue(raw_json)
        }


# https://dictionaryapi.com/products/api-learners-dictionary
class LearnerDictionary(DataSource):
    audio_file_format = 'ogg'
    number_subdir_regex = re.compile(r'^[^a-zA-Z]+')
    formatting_marker_regex = re.compile(r'{.*}')

    def __init__(self, api_key):
        self.api_key = api_key

    def _query_api(self, word):
        url = 'https://www.dictionaryapi.com/api/v3/references/learners/json/{word}?key={api_key}'.format(
            word=word, api_key=self.api_key)
        return requests.get(url).json()

    def _get_word_pronunciation_url(self, filename) -> str:
        if filename.startswith('bix'):
            subdir = 'bix'
        elif filename.startswith('gg'):
            subdir = 'gg'
        elif self.number_subdir_regex.match(filename):
            subdir = 'number'
        else:
            subdir = filename[0]
        url = 'https://media.merriam-webster.com/audio/prons/en/us/{format}/{subdir}/{filename}.{format}'.format(
            format=self.audio_file_format, subdir=subdir, filename=filename
        )

        return url

    def lookup_word(self, word: str) -> Dict[str, Value]:
        raw_json = self._query_api(word)

        target_words = [x for x in raw_json if x['meta']['id'].split(':')[0] == word]
        if len(target_words) == 0:
            raise WordLookupException('Merriam Webster learner\'s dictionary had no exact matches for {}'.format(word))

        pos_list = []
        word_id_list = []
        ipa_with_pos = []
        inflections_with_pos = []
        audio_with_pos = []
        definitions_with_pos = []
        for word_data in target_words:
            metadata = word_data['meta']
            shortdef = metadata['app-shortdef']
            pos_label = shortdef['fl']
            word_id = word_data['meta']['id'].split(':')[0] + '_' + pos_label
            try:
                pronunciation_data = word_data['hwi']['prs'][0]
            except KeyError:
                pronunciation_data = None
            if pronunciation_data:
                if 'ipa' in pronunciation_data:
                    ipa_with_pos.append((pronunciation_data['ipa'].strip(), pos_label))
                try:
                    pronunciation_url = self._get_word_pronunciation_url(pronunciation_data['sound']['audio'])
                    audio_with_pos.append((pronunciation_url, pos_label))
                except KeyError:
                    pass

            inflections_with_pos.append(([x['if'].replace('*', '') for x in word_data['ins']
                                          if 'if' in x] if 'ins' in word_data else [], pos_label))
            definitions_with_pos.append(([self.formatting_marker_regex.sub('', x) for x in shortdef['def']], pos_label))
            pos_list.append(pos_label)
            word_id_list.append(word_id)

        return {
                fieldnames.PART_OF_SPEECH: StringListValue(pos_list),
                fieldnames.DEFINITIONS: StringListsWithPOSValue(definitions_with_pos),
                fieldnames.PRONUNCIATION_IPA: StringsWithPosValue(ipa_with_pos),
                fieldnames.INFLECTIONS: StringListsWithPOSValue(inflections_with_pos),
                fieldnames.AUDIO: StringsWithPosValue(audio_with_pos),
                WORD_ID: StringListValue(word_id_list),
                fieldnames.RAW_DATA: RawDataValue(raw_json)
            }


# Each lookup here is two requests to MW; be careful if using an account limited to 1000/day
class MerriamWebster(DataSource):
    def __init__(self, learners_api_key, thesaurus_api_key, pos_in_definitions=False):
        self.learners_dict = LearnerDictionary(learners_api_key)
        self.thesaurus = CollegiateThesaurus(thesaurus_api_key)
        self.pos_in_definitions = pos_in_definitions

    @staticmethod
    def _add_primary_pos_value_if_present(val: StringListsWithPOSValue, pos: str,
                                          key: str, target_dict: Dict[str, Value]):
        present_parts_of_speech = {pos for values, pos in val.values_with_pos}
        if pos in present_parts_of_speech:
            target_dict[key] = StringListsWithPrimaryPOSValue(val.values_with_pos, pos)

    def lookup_word(self, word: str) -> Dict[str, Value]:
        dictionary_data = self.learners_dict.lookup_word(word)
        thesaurus_data = self.thesaurus.lookup_word(word)

        primary_pos = dictionary_data[fieldnames.PART_OF_SPEECH].val_list[0]

        output = {
            fieldnames.PART_OF_SPEECH: dictionary_data[fieldnames.PART_OF_SPEECH],
            fieldnames.DEFINITIONS: dictionary_data[fieldnames.DEFINITIONS],
            fieldnames.PRONUNCIATION_IPA: dictionary_data[fieldnames.PRONUNCIATION_IPA],
            fieldnames.AUDIO: dictionary_data[fieldnames.AUDIO],
            fieldnames.RAW_DATA: RawDataValue({
                'thesaurus': thesaurus_data[fieldnames.RAW_DATA].data,
                'dictionary': dictionary_data[fieldnames.RAW_DATA].data
            })
        }

        self._add_primary_pos_value_if_present(dictionary_data[fieldnames.INFLECTIONS], primary_pos,
                                               fieldnames.INFLECTIONS, output)
        self._add_primary_pos_value_if_present(thesaurus_data[fieldnames.SYNONYMS], primary_pos,
                                               fieldnames.SYNONYMS, output)
        self._add_primary_pos_value_if_present(thesaurus_data[fieldnames.ANTONYMS], primary_pos,
                                               fieldnames.ANTONYMS, output)

        return output




