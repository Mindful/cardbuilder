# https://dictionaryapi.com/products/json
import re
from typing import Dict

import requests
from json import loads

from cardbuilder.common import fieldnames
from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.util import log
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import WebApiDataSource, AggregatingDataSource
from cardbuilder.lookup.lookup_data import LookupData, lookup_data_type_factory
from cardbuilder.lookup.value import StringListsWithPOSValue, StringListsWithPrimaryPOSValue, RawDataValue, \
    StringsWithPosValue, StringValue, Value, StringListValue
from cardbuilder.exceptions import WordLookupException


# https://dictionaryapi.com/products/api-collegiate-thesaurus
class CollegiateThesaurus(WebApiDataSource):
    lookup_data_type = lookup_data_type_factory('CollegiateThesaurusLookupData', {Fieldname.RAW_DATA,
                                                                                  Fieldname.SYNONYMS,
                                                                                  Fieldname.ANTONYMS,
                                                                                  Fieldname.SUPPLEMENTAL})

    def __init__(self, api_key):
        super().__init__()
        log(self, 'initializing Collegiate Thesaurus with api key {}'.format(api_key))
        self.api_key = api_key

    def _query_api(self, word) -> str:
        url = 'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key={api_key}'.format(
            word=word, api_key=self.api_key
        )
        return requests.get(url).text

    def parse_word_content(self, word: Word, form: str, content: str) -> LookupData:
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
        word_ids = []

        # we only take the first set of synonyms/antonyms per part of speech; at some point it's just overkill
        for word_data in target_words:
            pos = word_data['fl']
            word_ids.append(word_data['meta']['id'].split(':')[0] + '_' + pos)
            syns_with_pos.append((word_data['meta']['syns'][0] if len(word_data['meta']['syns']) > 0 else [], pos))
            ants_with_pos.append((word_data['meta']['ants'][0] if len(word_data['meta']['ants']) > 0 else [], pos))

        return self.lookup_data_type(word, form, {
            Fieldname.SYNONYMS: StringListsWithPOSValue(syns_with_pos),
            Fieldname.ANTONYMS: StringListsWithPOSValue(ants_with_pos),
            Fieldname.SUPPLEMENTAL: StringListValue(word_ids),
            Fieldname.RAW_DATA: RawDataValue(content)
        })


# https://dictionaryapi.com/products/api-learners-dictionary
class LearnerDictionary(WebApiDataSource):
    lookup_data_type = lookup_data_type_factory('LearnerDictionaryLookupData', {Fieldname.PART_OF_SPEECH,
                                                                                Fieldname.DEFINITIONS,
                                                                                Fieldname.PRONUNCIATION_IPA,
                                                                                Fieldname.INFLECTIONS,
                                                                                Fieldname.SUPPLEMENTAL,
                                                                                Fieldname.AUDIO,
                                                                                Fieldname.RAW_DATA})

    audio_file_format = 'mp3'
    number_subdir_regex = re.compile(r'^[^a-zA-Z]+')
    # TODO: this might be too aggressive - for example it entirely erases "{it} chiefly US {/it}"
    formatting_marker_regex = re.compile(r'{.*}')

    def __init__(self, api_key):
        super().__init__()
        log(self, 'initializing Learner\'s Dictionary with api key {}'.format(api_key))
        self.api_key = api_key

    def _query_api(self, word) -> str:
        url = 'https://www.dictionaryapi.com/api/v3/references/learners/json/{word}?key={api_key}'.format(
            word=word, api_key=self.api_key)
        return requests.get(url).text

    def parse_word_content(self, word: Word, form: str, content: str) -> LookupData:
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
                        output = {Fieldname.RAW_DATA: RawDataValue(content)}
                        if 'prs' in target_word:
                            pronunciation_data = target_word['prs'][0]
                            if 'ipa' in pronunciation_data:
                                output[Fieldname.PRONUNCIATION_IPA] = StringValue(pronunciation_data['ipa'])
                            if 'sound' in pronunciation_data:
                                output[Fieldname.AUDIO] = StringValue(self._get_word_pronunciation_url(
                                    pronunciation_data['sound']['audio']))

                        if 'fl' in target_word:
                            # There's only going to be one POS, but we expect this to be a StringListValue
                            # in the MerriamWebster data source
                            output[Fieldname.PART_OF_SPEECH] = StringListValue([target_word['fl']])

                        if len(output) > 0:
                            return self.lookup_data_type(word, form, output)

            raise WordLookupException('Merriam Webster learner\'s dictionary had no exact matches for {}'.format(form))

        pos_list = []
        word_id_list = []
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
            definitions_with_pos.append(([d for d in (self.formatting_marker_regex.sub('', x)
                                                      for x in shortdef['def']) if d],
                                         pos_label))
            pos_list.append(pos_label)
            word_id_list.append(word_id)

        out = {
            Fieldname.PART_OF_SPEECH: StringListValue(pos_list),
            Fieldname.DEFINITIONS: StringListsWithPOSValue(definitions_with_pos),
            Fieldname.PRONUNCIATION_IPA: StringsWithPosValue(ipa_with_pos),
            Fieldname.INFLECTIONS: StringListsWithPOSValue(inflections_with_pos),
            Fieldname.SUPPLEMENTAL: StringListValue(word_id_list),
            Fieldname.RAW_DATA: RawDataValue(content)
        }

        if len(audio_with_pos) > 0:
            out[Fieldname.AUDIO] = StringsWithPosValue(audio_with_pos)

        return self.lookup_data_type(word, form, out)

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


# Each lookup here is two requests to MW; be careful if using an account limited to 1000/day
class MerriamWebster(AggregatingDataSource):
    keylike = re.compile(r'.+-.+-.+-.+')

    lookup_data_type = lookup_data_type_factory('MerriamWebsterLookupData',
                                                LearnerDictionary.lookup_data_type.fields() |
                                                CollegiateThesaurus.lookup_data_type.fields())

    def __init__(self, learners_api_key: str, thesaurus_api_key: str, pos_in_definitions=False):
        api_keys = []
        for key in [learners_api_key, thesaurus_api_key]:
            if self.keylike.match(key) and '.' not in key:
                log(self, '{} looks like API key - using it'.format(key))
                api_key = key
            else:
                with open(key) as f:
                    api_key = f.readlines()[0]
                log(self, 'read API key {} from file {} - using it'.format(api_key, key))

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

    @staticmethod
    def _add_primary_pos_value_if_present(val: StringListsWithPOSValue, pos: str,
                                          key: Fieldname, target_dict: Dict[Fieldname, Value]):
        present_parts_of_speech = {pos for values, pos in val.values_with_pos}
        if pos in present_parts_of_speech:
            target_dict[key] = StringListsWithPrimaryPOSValue(val.values_with_pos, pos)

    def lookup_word(self, word: Word, form: str) -> LookupData:
        dictionary_data = self.learners_dict.lookup_word(word, form)
        if len(dictionary_data[Fieldname.PART_OF_SPEECH].val_list) > 0:
            primary_pos = dictionary_data[Fieldname.PART_OF_SPEECH].val_list[0]
        else:
            raise WordLookupException('No parts of speech found in MerriamWebster for {}'.format(form))

        output = dictionary_data.get_data()
        try:  # thesaurus gags an awful lot
            thesaurus_data = self.thesaurus.lookup_word(word, form)
            output[Fieldname.RAW_DATA] = RawDataValue({
                'thesaurus': thesaurus_data[Fieldname.RAW_DATA].data,
                'dictionary': dictionary_data[Fieldname.RAW_DATA].data
            })
            thesaurus = True
        except WordLookupException:
            output[Fieldname.RAW_DATA] = RawDataValue({
                'dictionary': dictionary_data[Fieldname.RAW_DATA].data
            })
            thesaurus = False

        if Fieldname.INFLECTIONS in dictionary_data:
            self._add_primary_pos_value_if_present(dictionary_data[Fieldname.INFLECTIONS], primary_pos,
                                                   Fieldname.INFLECTIONS, output)

        if thesaurus:
            self._add_primary_pos_value_if_present(thesaurus_data[Fieldname.SYNONYMS], primary_pos,
                                                   Fieldname.SYNONYMS, output)
            self._add_primary_pos_value_if_present(thesaurus_data[Fieldname.ANTONYMS], primary_pos,
                                                   Fieldname.ANTONYMS, output)

        return self.lookup_data_type(word, form, output)
