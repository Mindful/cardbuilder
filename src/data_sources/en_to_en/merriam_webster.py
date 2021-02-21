# https://dictionaryapi.com/products/json
import re
from typing import Dict, Union, List

import requests

from common.fieldnames import DEFINITIONS, PART_OF_SPEECH, SYNONYMS, AUDIO, ANTONYMS, WORD, PRONUNCIATION_IPA, \
    INFLECTIONS
from data_sources import DataSource
from exceptions import WordLookupException

WORD_ID = 'wid'


# https://dictionaryapi.com/products/api-collegiate-thesaurus
class CollegiateThesaurus:
    def __init__(self, api_key):
        self.api_key = api_key

    def _query_api(self, word):
        url = 'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key={api_key}'.format(
            word=word, api_key=self.api_key
        )
        return requests.get(url).json()

    def query_api(self, word: str) -> List[Dict[str, Union[str, List[str]]]]:
        raw_json = self._query_api(word)
        results = []

        target_words = [x for x in raw_json if x['meta']['id'].split(':')[0] == word]
        if len(target_words) == 0:
            raise WordLookupException('Merriam Webster collegiate thesaurus had no exact matches for {}'.format(word))

        for word_data in target_words:
            word_id = word_data['meta']['id'].split(':')[0] + '_' + word_data['fl']
            synonyms = word_data['meta']['syns'][0] if len(word_data['meta']['syns']) > 0 else []
            antonyms = word_data['meta']['ants'][0] if len(word_data['meta']['ants']) > 0 else []

            results.append({
                SYNONYMS: synonyms,
                ANTONYMS: antonyms,
                WORD_ID: word_id
            })

        return results


# https://dictionaryapi.com/products/api-learners-dictionary
class LearnerDictionary:

    audio_file_format = 'ogg'
    number_subdir_regex = re.compile(r'^[^a-zA-Z]+')
    formatting_marker_regex = re.compile(r'{.*}')

    def __init__(self, api_key):
        self.api_key = api_key

    def _query_api(self, word):
        url = 'https://www.dictionaryapi.com/api/v3/references/learners/json/{word}?key={api_key}'.format(
            word=word, api_key=self.api_key)
        return requests.get(url).json()

    def _get_word_pronunciation_url(self, filename):
        subdir = None
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

    def query_api(self, word: str) -> List[Dict[str, Union[str, List[str]]]]:
        raw_json = self._query_api(word)
        results = []

        target_words = [x for x in raw_json if x['meta']['id'].split(':')[0] == word]
        if len(target_words) == 0:
            raise WordLookupException('Merriam Webster learner\'s dictionary had no exact matches for {}'.format(word))

        for word_data in target_words:
            metadata = word_data['meta']
            word_id = word_data['meta']['id'].split(':')[0] + '_' + word_data['fl']
            try:
                pronunciation_data = word_data['hwi']['prs'][0]
            except KeyError:
                pronunciation_data = None
            if pronunciation_data:
                word_ipa = pronunciation_data.get('ipa', None)
                try:
                    pronunciation_url = self._get_word_pronunciation_url(pronunciation_data['sound']['audio'])
                except KeyError:
                    pronunciation_url = None
            else:
                pronunciation_url = None
                word_ipa = None

            shortdef = metadata['app-shortdef']
            inflections = [x['if'].replace('*', '') for x in word_data['ins']
                           if 'if' in x] if 'ins' in word_data else []
            pos_label = shortdef['fl']
            definitions = [self.formatting_marker_regex.sub('', x) for x in shortdef['def']]

            results.append({
                WORD: word,
                PART_OF_SPEECH: pos_label,
                DEFINITIONS: definitions,
                PRONUNCIATION_IPA: word_ipa,
                INFLECTIONS: inflections,
                AUDIO: pronunciation_url,
                WORD_ID: word_id
            })

        return results


# Each lookup here is two requests to MW; be careful if using an account limited to 1000/day
class MerriamWebster(DataSource):
    def __init__(self, learners_api_key, thesaurus_api_key, pos_in_definitions=False):
        self.learners_dict = LearnerDictionary(learners_api_key)
        self.thesaurus = CollegiateThesaurus(thesaurus_api_key)
        self.pos_in_definitions = pos_in_definitions

    def lookup_word(self, word: str) -> Dict[str, Union[str, List[str]]]:
        dictionary_data = self.learners_dict.query_api(word)
        thesaurus_data = self.thesaurus.query_api(word)

        results_by_wid = {
            x[WORD_ID]: x for x in dictionary_data
        }

        for d in thesaurus_data:
            if d[WORD_ID] in results_by_wid:
                results_by_wid[d[WORD_ID]].update(d)

        if self.pos_in_definitions:
            for result in results_by_wid.values():
                result[DEFINITIONS] = ['{}: {}'.format(result[PART_OF_SPEECH], x) for x in result[DEFINITIONS]]

        primary_result = next(iter(results_by_wid.values()))
        for secondary_result in list(results_by_wid.values())[1:]:
            primary_result[DEFINITIONS].extend(secondary_result[DEFINITIONS])

        # TODO: something smarter than just taking the first result
        return next(iter(results_by_wid.values()))