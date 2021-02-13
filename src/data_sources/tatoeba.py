import os
import csv
from collections import defaultdict
from typing import List, Dict, Union
from common import *
from data_sources import DataSource
from tqdm import tqdm

MAX_RESULTS = 100


class TatoebaExampleSentences(DataSource):
    def __init__(self, source_lang, target_lang):
        self.source_lang = source_lang
        self.target_lang = target_lang
        source_lang_data = self._load_language_sents(source_lang)

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
        results = defaultdict(set)
        for ident, sent in id_sent_data:
            # TODO: split() is only reliable for languages that use spaces.
            # we'll need something else to split words for japanese
            tokens = [x.lower() for x in sent.split()]
            for token in tokens:
                results[token].add(ident)

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
