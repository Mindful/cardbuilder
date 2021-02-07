# https://dictionaryapi.com/products/json
import requests
import re
from common import *


# https://dictionaryapi.com/products/api-collegiate-thesaurus
class CollegiateThesaurus:
    def __init__(self, api_key):
        self.api_key = api_key

    def _query_api(self, word):
        url = 'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key={api_key}'.format(
            word=word, api_key=self.api_key
        )
        return requests.get(url).json()

    def lookup_word(self, word):
        raw_json = self._query_api(word)
        results = []

        target_words = [x for x in raw_json if x['meta']['id'].split(':')[0] == word]
        if len(target_words) == 0:
            raise LookupException('Merriam Webster collegiate thesaurus had no exact matches for {}'.format(word))

        for word_data in target_words:
            uuid = word_data['meta']['uuid']
            synonyms = word_data['meta']['syns'][0] if len(word_data['meta']['syns']) > 0 else []
            antonyms = word_data['meta']['ants'][0] if len(word_data['meta']['ants']) > 0 else []

            results.append({
                SYNONYMS: synonyms,
                ANTONYMS: antonyms,
                'uuid': uuid
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

    def lookup_word(self, word):
        raw_json = self._query_api(word)
        results = []

        target_words = [x for x in raw_json if x['meta']['id'].split(':')[0] == word]
        if len(target_words) == 0:
            raise LookupException('Merriam Webster learner\'s dictionary had no exact matches for {}'.format(word))

        for word_data in target_words:
            metadata = word_data['meta']
            uuid = metadata['uuid']
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
                'audio_url': pronunciation_url,
                'uuid': uuid
            })

        return results


# Each lookup here is two requests to MW; be careful if you're limited to 1000/day
class MerriamWebster:
    def __init__(self, learners_api_key, thesaurus_api_key):
        self.learners_dict = LearnerDictionary(learners_api_key)
        self.thesaurus = CollegiateThesaurus(thesaurus_api_key)

    def lookup_word(self, word):
        dictionary_data = self.learners_dict.lookup_word(word)
        thesaurus_data = self.thesaurus.lookup_word(word)

        results_by_uuid = {
            x['uuid']: x for x in dictionary_data
        }

        for d in thesaurus_data:
            if d['uuid'] in results_by_uuid:
                results_by_uuid[d['uuid']].update(d)

        return list(results_by_uuid.values())


