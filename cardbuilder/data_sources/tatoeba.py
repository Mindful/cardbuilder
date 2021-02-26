import csv
import re
import tarfile
from bz2 import BZ2Decompressor
from collections import defaultdict
from io import BytesIO
from os.path import exists
from string import punctuation
from typing import Dict, Union, List, Any

import requests
from fugashi import Tagger

from common import ExternalDataDependent, InDataDir
from common.util import is_hiragana, fast_linecount, loading_bar, log
from common.fieldnames import EXAMPLE_SENTENCES
from common.languages import JAPANESE, ENGLISH
from data_sources import DataSource
from exceptions import CardBuilderException, WordLookupException


class TatoebaExampleSentences(DataSource, ExternalDataDependent):
    max_results = 100
    en_punctuation_regex = re.compile('[{}]'.format(re.escape(punctuation)))
    links_file = 'links.csv'
    links_url = 'https://downloads.tatoeba.org/exports/links.tar.bz2'
    sentences_filename_template = '{}_sentences.tsv'
    data_dict = {}

    @staticmethod
    def _load_language_sents(lang):
        filename = TatoebaExampleSentences.sentences_filename_template.format(lang)
        line_count = fast_linecount(filename)
        results = []
        with open(filename, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for ident, _, sentence in loading_bar(reader, 'reading {}'.format(filename), line_count):
                results.append((ident, sentence))

        return results

    def _read_data(self) -> Any:
        pass  # not used because we override get_data()

    def get_data(self) -> Any:
        # we need different data depending on the languages this instance was initialized with
        # the info we need is also different form the links file depending on what languages we're using
        # so we just read that every time. could be avoided, but probably not worth the work
        self.download_if_necessary()

        with InDataDir():
            for langname in (self.source_lang, self.target_lang):
                if langname not in self.data_dict:
                    log(self, 'Loading external Tatoeba data for language {}...'.format(langname))
                    self.data_dict[langname] = self._load_language_sents(langname)

        return self.data_dict[self.source_lang], self.data_dict[self.target_lang]

    def _fetch_remote_files_if_necessary(self):
        url_template = 'https://downloads.tatoeba.org/exports/per_language/{}/{}_sentences.tsv.bz2'
        filenames_and_urls = [
            (self.sentences_filename_template.format(self.source_lang),
             url_template.format(self.source_lang, self.source_lang)),
            (self.sentences_filename_template.format(self.target_lang),
             url_template.format(self.target_lang, self.target_lang)),
            (self.links_file, self.links_url)
        ]

        for filename, url in filenames_and_urls:
            if not exists(filename):
                log(self, '{} not found - downloading and extracting...'.format(filename))
                data = requests.get(url)
                if url[-8:] == '.tar.bz2':
                    filelike = BytesIO(data.content)
                    tar = tarfile.open(fileobj=filelike, mode='r:bz2')
                    tar.extract(filename)
                elif url[-4:] == '.bz2':
                    with open(filename, 'wb+') as f:
                        f.write(BZ2Decompressor().decompress(data.content))
                else:
                    raise CardBuilderException('Retrieved unexpected file format from Tatoeba: {}'.format(url))


    def _split_japanese_sentence(self, sentence: str) -> List[str]:
        # hacky and only accommodates  exact matches (I.E. conjugated verbs are shot), could probably be done better
        split_words_generator = (str(x) for x in self.tagger(sentence))
        split_words = [x for x in split_words_generator if not (len(x) == 1 and is_hiragana(x))]
        return split_words

    def _split_english_sentence(self, sentence: str) -> List[str]:
        cleaned_sentence = self.en_punctuation_regex.sub(' ', sentence.lower())
        return cleaned_sentence.split()

    def __init__(self, source_lang: str, target_lang: str):
        self.source_lang = source_lang
        self.target_lang = target_lang
        source_lang_data, target_lang_data = self.get_data()

        if source_lang == JAPANESE:
            self.tagger = Tagger('-Owakati')
            self._split_sentence = self._split_japanese_sentence
        elif source_lang == ENGLISH:
            self._split_sentence = self._split_english_sentence
        else:
            raise CardBuilderException('No sentence splitting implemented for source language {}'.format(source_lang))

        self.source_index = self._build_word_index(source_lang_data)
        self.source_lang_data = dict(source_lang_data)
        self.target_lang_data = dict(target_lang_data)

        self.source_target_links = {}
        with InDataDir():
            line_count = fast_linecount(self.links_file)
            log(self, 'Loading external Tatoeba link data for languages {} -> {}'.format(self.source_lang,
                                                                                         self.target_lang))
            with open(self.links_file, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                for source_id, target_id in loading_bar(reader, 'reading links.csv', line_count):
                    if source_id in self.source_lang_data and target_id in self.target_lang_data:
                        self.source_target_links[source_id] = target_id

    def _build_word_index(self, id_sent_data):
        # the word index would certainly take up less memory as a trie, but it's probably not worth the trouble
        results = defaultdict(set)
        for ident, sent in loading_bar(id_sent_data, 'indexing sentences'):
            words = self._split_sentence(sent)
            for word in words:
                results[word].add(ident)

        return results

    def lookup_word(self, word: str) -> Dict[str, Union[str, List[str]]]:
        if word not in self.source_index:
            raise WordLookupException('Could not find {} in Tatoeba example sentences for {}'.
                                      format(word, self.source_lang))

        source_idents = [ident for ident in self.source_index[word]]
        example_sentence_pairs = [(self.source_lang_data[ident],
                                   self.target_lang_data[self.source_target_links[ident]]
                                   if ident in self.source_target_links else None)
                                  for ident in source_idents]

        final_selection = sorted(example_sentence_pairs, key=lambda x: 1 if x[1] is None else 0)[:self.max_results]

        return {
            EXAMPLE_SENTENCES: ['{}\n{}'.format(example, translated_example) if translated_example is not None
                                else example for example, translated_example in final_selection]
        }
