from cardbuilder.data_sources.data_source import DataSource
from cardbuilder.data_sources.en_to_en.word_freq import WordFrequency
from cardbuilder.data_sources.en_to_en.merriam_webster import MerriamWebster, CollegiateThesaurus, LearnerDictionary
from cardbuilder.data_sources.ja_to_en.jisho import Jisho
from cardbuilder.data_sources.en_to_ja.gene_dict import GeneDict
from cardbuilder.data_sources.en_to_ja.eijiro import Eijiro
from cardbuilder.data_sources.en_to_ja.ejdict_hand import EJDictHand
from cardbuilder.data_sources.ja_to_ja.nhk_pitch_accent import NhkPitchAccent
from cardbuilder.data_sources.eo_to_en.espdic import ESPDIC
from cardbuilder.data_sources.tatoeba import TatoebaExampleSentences

instantiable = {
    'word-freq-en': WordFrequency,
    'merriam-webster': MerriamWebster,
    'merriam-webster-thesaurus': CollegiateThesaurus,
    'merriam-webster-dictionary': LearnerDictionary,
    'jisho': Jisho,
    'gene-dict': GeneDict,
    'eijiro': Eijiro,
    'ejdict-hand': EJDictHand,
    'nhk-pitch-accent': NhkPitchAccent,
    'espdic': ESPDIC,
    'tatoeba': TatoebaExampleSentences
}

