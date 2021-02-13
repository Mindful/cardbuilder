from data_sources.ja_to_ja.nhk_pitch_accent import NhkPitchAccent
from data_sources.en_to_ja.ejdict_hand import EJDictHand


if __name__ == '__main__':
    # pa = NhkPitchAccent()
    # d = pa.lookup_word('開く')
    # b = pa.lookup_word('悪意')

    dict = EJDictHand()

    d = dict.lookup_word('last')

    print('debug')