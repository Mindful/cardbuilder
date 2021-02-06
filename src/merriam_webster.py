# https://dictionaryapi.com/products/json
import requests
import re
from lookup_exception import LookupExceptinon
from constants import *


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
        word_data = raw_json[0]
        # TODO: smarter way to pick which word (such as POS), or if we need multiple words. see: dog:1, dog:2, etc.

        synonyms = word_data['meta']['syns']
        antonyms = word_data['meta']['ants']

        return {
            SYNONYMS: synonyms,
            ANTONYMS: antonyms
        }


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
        word_data = raw_json[0]
        # TODO: smarter way to pick which word (such as POS), or if we need multiple words. see: dog:1, dog:2, etc.
        pronunciation_data = word_data['hwi']['prs'][0]

        shortdef = word_data['meta']['app-shortdef']
        word_form = shortdef['hw'].split(':')[0]
        if word_form != word:
            raise LookupExceptinon('Retrieved word "{}" looking up word "{}"'.format(word_form, word))

        pos_label = shortdef['fl']
        definition = self.formatting_marker_regex.sub('', shortdef['def'][0])

        pronunciation_url = self._get_word_pronunciation_url(pronunciation_data['sound']['audio'])
        word_ipa = pronunciation_data['ipa']

        return {
            WORD: word,
            PART_OF_SPEECH: pos_label,
            DEFINITION: definition,
            PRONUNCIATION_IPA: word_ipa,
            'audio_url': pronunciation_url
        }

