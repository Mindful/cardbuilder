from cardbuilder.lookup.en.merriam_webster import MerriamWebster, CollegiateThesaurus, LearnerDictionary
from cardbuilder.lookup.en.word_freq import WordFrequency
from cardbuilder.lookup.en_to_ja.eijiro import Eijiro
from cardbuilder.lookup.en_to_ja.ejdict_hand import EJDictHand
from cardbuilder.lookup.en_to_ja.gene_dict import GeneDict
from cardbuilder.lookup.eo_to_en.espdic import ESPDIC
from cardbuilder.lookup.ja_to_en.jisho import Jisho
from cardbuilder.lookup.ja.nhk_pitch_accent import NhkPitchAccent
from cardbuilder.lookup.tatoeba import TatoebaExampleSentences

instantiable_data_sources = {
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

