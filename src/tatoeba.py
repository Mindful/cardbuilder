import os
import csv
from collections import defaultdict
from common import *

class TatoebaExampleSentences:
    def __init__(self, source_lang, target_lang):
        self.source_lang = source_lang
        self.target_lang = target_lang
        source_lang_data = self._load_language_sents(source_lang)

        self.source_index = self._build_word_index(source_lang_data)
        self.source_lang_data = dict(source_lang_data)
        self.target_lang_data = dict(self._load_language_sents(target_lang))

        self.source_target_links = {}
        links_file = os.path.join(DATA_DIR, 'links.csv')
        with open(links_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for source_id, target_id in reader:
                if source_id in self.source_lang_data and target_id in self.target_lang_data:
                    self.source_target_links[source_id] = target_id

    def _load_language_sents(self, lang):
        sentence_file = os.path.join(DATA_DIR, '{}_sentences.tsv'.format(lang))
        results = []
        with open(sentence_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for ident, _, sentence in reader:
                results.append((ident, sentence))

        return results

    def _build_word_index(self, id_sent_data):
        results = defaultdict(set)
        for ident, sent in id_sent_data:
            tokens = [x.lower() for x in sent.split()]
            for token in tokens:
                results[token].add(ident)

        return results

    def lookup_word(self, word):
        if word not in self.source_index:
            raise LookupException('Could not find {} in Tatoeba example sentences for {}'.
                                  format(word, self.source_lang))

        source_idents = [ident for ident in self.source_index[word]]

        return {
            EXAMPLE_SENTENCES: [(self.source_lang_data[ident],
                                 self.target_lang_data[self.source_target_links[ident]]
                                 if ident in self.source_target_links else None)
                                for ident in source_idents]
        }

