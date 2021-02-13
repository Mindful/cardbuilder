from data_sources.ja_to_ja.nhk_pitch_accent import NhkPitchAccent


if __name__ == '__main__':
    pa = NhkPitchAccent()
    d = pa.lookup_word('開く')
    b = pa.lookup_word('悪意')

    print('debug')