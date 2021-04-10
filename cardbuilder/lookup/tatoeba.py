import csv
import re
import sqlite3
import tarfile
from bz2 import BZ2Decompressor
from collections import defaultdict
from json import loads
from os.path import exists
from string import punctuation
from typing import List, Tuple, Iterable

from fugashi import Tagger

from cardbuilder.common.util import is_hiragana, fast_linecount, loading_bar, log, download_to_stream_with_loading_bar, \
    dedup_by, DATABASE_NAME, InDataDir
from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.common.languages import JAPANESE
from cardbuilder.input.word import Word
from cardbuilder.lookup.lookup_data import outputs, LookupData
from cardbuilder.lookup.value import MultiListValue
from cardbuilder.exceptions import WordLookupException, CardBuilderUsageException
from cardbuilder.lookup.data_source import ExternalDataDataSource

#
# class TatoebaExampleSentencesValue(Value):
#     def __init__(self, example_sentence_pairs: List[Tuple[str, str]]):
#         self.sentence_pairs = sorted(example_sentence_pairs, key=lambda x: 1 if x[1] is None else 0)
#
#     def to_output_string(self, pair_format_string: str = '{}\n{}\n', max_sentences: int = 10,
#                          dedup: bool = True) -> str:
#         sentence_pairs = self.sentence_pairs
#         if dedup:
#             sentence_pairs = dedup_by(dedup_by(sentence_pairs, lambda x: x[0]), lambda x: x[1])
#
#         if max_sentences is not None:
#             sentence_pairs = sentence_pairs[:max_sentences]
#
#         return ''.join([pair_format_string.format(*pair) for pair in sentence_pairs])


@outputs({
    Fieldname.EXAMPLE_SENTENCES: MultiListValue
})
class TatoebaExampleSentences(ExternalDataDataSource):

    links_table_name = 'tatoeba_links'
    sentences_table_name_formatstring = 'tatoeba_{}_sentences'
    index_table_name_formatstring = 'tatoeba_{}_index'
    punctuation_regex = re.compile('[{}]'.format(re.escape(punctuation)))
    links_file = 'links.csv'
    links_url = 'https://downloads.tatoeba.org/exports/links.tar.bz2'
    sentences_filename_template = '{}_sentences.tsv'
    data_dict = {}

    def lookup_word(self, word: Word, form: str) -> LookupData:
        c = self.conn.execute("select sent_id_list from tatoeba_{}_index where word=?;".format(self.source_lang), (form,))
        index_result = c.fetchone()
        if index_result is None:
            raise WordLookupException('Word "{}" not found in the Tatoeba index for language {}'.format(form,
                                                                                                        self.source_lang))
        else:
            index_ids = loads(index_result[0])

        c = self.conn.execute('''
        select tatoeba_{0}_sentences.sentence as {0}_sentence, tatoeba_{1}_sentences.sentence as {1}_sentence
        from tatoeba_{0}_sentences 
        inner join tatoeba_links on tatoeba_{0}_sentences.sent_id=src_sent_id
        inner join tatoeba_{1}_sentences on tatoeba_{1}_sentences.sent_id=target_sent_id
        where tatoeba_{0}_sentences.sent_id in ({2});
        '''.format(self.source_lang, self.target_lang, ','.join(str(x) for x in index_ids)))

        example_sentence_pairs = c.fetchall()
        if len(example_sentence_pairs) == 0:
            raise WordLookupException('Found no corresponding example sentences for word {} in'
                                      ' Tatoeba data for language {}'.format(form, self.target_lang))

        example_sentences_value = TatoebaExampleSentencesValue(example_sentence_pairs)

        return self.lookup_data_type(word, form, {
            Fieldname.EXAMPLE_SENTENCES: example_sentences_value
        })

    def _create_tables(self):
        # links table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS {}(
             src_sent_id INT,
             target_sent_id INT
         );'''.format(self.links_table_name))
        self.conn.execute('''CREATE INDEX IF NOT EXISTS links_source_sentence
            ON {} (src_sent_id);'''.format(self.links_table_name))

        # index of words to sentence IDs table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS {}(
             word TEXT PRIMARY KEY,
             sent_id_list TEXT
         );'''.format(self.index_table_name_formatstring.format(self.source_lang)))

        # sentences table for both languages
        for lang in (self.source_lang, self.target_lang):
            self.conn.execute('''CREATE TABLE IF NOT EXISTS {}(
                 sent_id INT PRIMARY KEY,
                 sentence TEXT
             );'''.format(self.sentences_table_name_formatstring.format(lang)))

        self.conn.commit()

    def _read_links_data(self) -> Iterable[Tuple[int, int]]:
        #  each link is guaranteed to be in the file going both directions, so no special logic is necessary
        with InDataDir():
            line_count = fast_linecount(self.links_file)
            log(self, 'Reading Tatoeba link data into database')
            with open(self.links_file, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                for source_id, target_id in loading_bar(reader, 'reading links.csv', line_count):
                    yield int(source_id), int(target_id)

    def _read_language_sents(self, lang) -> Iterable[Tuple[int, str]]:
        filename = self.sentences_filename_template.format(lang)
        line_count = fast_linecount(filename)
        with open(filename, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for ident, _, sentence in loading_bar(reader, 'reading {}'.format(filename), line_count):
                yield int(ident), sentence

    def _compute_and_yield_index_data(self, id_sent_data: List[Tuple[int, str]]) -> Iterable[Tuple[str, str]]:
        # the word index would certainly take up less memory as a trie, but it's probably not worth the trouble
        results = defaultdict(set)
        for ident, sent in loading_bar(id_sent_data, 'indexing sentences'):
            words = self._split_sentence(sent)
            for word in (w for w in words if not w.isnumeric() and w not in punctuation):
                results[word].add(ident)

        for word, identity_set in results.items():
            yield word, str(list(identity_set))

    def __init__(self, source_lang: str, target_lang: str):
        self.source_lang = source_lang
        self.target_lang = target_lang
        # intentionally don't call parent init; tatoeba doesn't use default sql table
        with InDataDir():
            self.conn = sqlite3.connect(DATABASE_NAME)
            self._fetch_remote_files_if_necessary()

        self._create_tables()
        self._load_data_into_database(self.links_table_name, self._read_links_data)
        for lang in (self.source_lang, self.target_lang):
            self._load_data_into_database(self.sentences_table_name_formatstring.format(lang),
                                          lambda: self._read_language_sents(lang))

        if source_lang == JAPANESE:
            self.tagger = Tagger('-Owakati')
            self._split_sentence = self._split_japanese_sentence
        else:
            self._split_sentence = self._split_by_spaces

        cursor = self.conn.execute('SELECT sent_id, sentence FROM {}'.format(
            self.sentences_table_name_formatstring.format(self.source_lang)))
        source_lang_data = cursor.fetchall()
        self._load_data_into_database(self.index_table_name_formatstring.format(self.source_lang),
                                      lambda: self._compute_and_yield_index_data(source_lang_data))

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

                stream_data = download_to_stream_with_loading_bar(url)
                if url[-8:] == '.tar.bz2':
                    tar = tarfile.open(fileobj=stream_data, mode='r:bz2')
                    tar.extract(filename)
                elif url[-4:] == '.bz2':
                    with open(filename, 'wb+') as f:
                        f.write(BZ2Decompressor().decompress(stream_data.read()))
                else:
                    raise CardBuilderUsageException('Retrieved unexpected file format from Tatoeba: {}'.format(url))

    def _split_japanese_sentence(self, sentence: str) -> List[str]:
        # hacky and only accommodates  exact matches (I.E. conjugated verbs are shot), could probably be done better
        split_words_generator = (str(x) for x in self.tagger(sentence))
        split_words = [x for x in split_words_generator if not (len(x) == 1 and is_hiragana(x))]
        return split_words

    def _split_by_spaces(self, sentence: str) -> List[str]:
        cleaned_sentence = self.punctuation_regex.sub(' ', sentence.lower())
        return cleaned_sentence.split()

    def parse_word_content(self, word: Word, form: str, content: str) -> LookupData:
        pass  # don't need this because we override #lookup_word

    def _read_and_convert_data(self) -> Iterable[Tuple[str, str]]:
        pass  # don't use this because we have functions for reading from several different tables
