from data_sources.ja_to_ja import NhkPitchAccent
from data_sources.en_to_ja import EJDictHand
from word_sources.en import SvlWords
from common import LOGGER, WordFrequency
import logging
import sys

if __name__ == '__main__':
    # create console handler with a higher log level
    logging.getLogger().setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    LOGGER.addHandler(ch)
    pa = NhkPitchAccent()
    d = pa.lookup_word('開く')
    b = pa.lookup_word('悪意')

    dict = EJDictHand()

    d2 = dict.lookup_word('last')
    wf = WordFrequency()
    wf2 = WordFrequency()
    s = SvlWords(wf)
    a = s[1]

    print('debug')