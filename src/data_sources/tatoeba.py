import os
import csv
from collections import defaultdict
from typing import List, Dict, Union
from common import *
from data_sources import DataSource
from tqdm import tqdm
from fugashi import Tagger
import re
from string import punctuation


MAX_RESULTS = 100
EN_PUNCTUATION_REGEX = re.compile('[{}]'.format(re.escape(punctuation)))


class TatoebaExampleSentences(DataSource):
    def _split_japanese_sentence(self, sentence: str) -> List[str]:
        # hacky and only accommodates  exact matches (I.E. conjugated verbs are shot), could probably be done better
        split_words_generator = (str(x) for x in self.tagger(sentence))
        split_words = [x for x in split_words_generator if not (len(x) == 1 and is_hiragana(x))]
        return split_words

    def _split_english_sentence(self, sentence: str) -> List[str]:
        cleaned_sentence = EN_PUNCTUATION_REGEX.sub(' ', sentence.lower())
        return cleaned_sentence.split()

    def __init__(self, source_lang: str, target_lang: str):
        self.source_lang = source_lang
        self.target_lang = target_lang
        source_lang_data = self._load_language_sents(source_lang)

        if source_lang == JAPANESE:
            self.tagger = Tagger('-Owakati')
            self._split_sentence = self._split_japanese_sentence
        elif source_lang == ENGLISH:
            self._split_sentence = self._split_english_sentence
        else:
            raise RuntimeError('No sentence splitting implemented for source language {}'.format(source_lang))

        self.source_index = self._build_word_index(source_lang_data)
        self.source_lang_data = dict(source_lang_data)
        self.target_lang_data = dict(self._load_language_sents(target_lang))

        self.source_target_links = {}
        links_file = os.path.join(DATA_DIR, 'links.csv')
        line_count = fast_linecount(links_file)
        with open(links_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for source_id, target_id in tqdm(reader, total=line_count, desc='reading links.csv'):
                if source_id in self.source_lang_data and target_id in self.target_lang_data:
                    self.source_target_links[source_id] = target_id

    def _load_language_sents(self, lang):
        filename = '{}_sentences.tsv'.format(lang)
        sentence_file = os.path.join(DATA_DIR, filename)
        line_count = fast_linecount(sentence_file)
        results = []
        with open(sentence_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for ident, _, sentence in tqdm(reader, total=line_count, desc='reading {}'.format(filename)):
                results.append((ident, sentence))

        return results

    def _build_word_index(self, id_sent_data):
        # the word index would certainly take up less memory as a trie, but it's probably not worth the trouble
        results = defaultdict(set)
        for ident, sent in tqdm(id_sent_data, desc='indexing sentences'):
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

        final_selection = sorted(example_sentence_pairs, key=lambda x: 1 if x[1] is None else 0)[:MAX_RESULTS]

        return {
            EXAMPLE_SENTENCES: ['{}\n{}'.format(example, translated_example) if translated_example is not None
                                else example for example, translated_example in final_selection]
        }
