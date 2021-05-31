import math
from collections import defaultdict

import requests

from bs4 import BeautifulSoup

from cardbuilder.common import Fieldname
from cardbuilder.exceptions import WordLookupException
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import WebApiDataSource
from cardbuilder.lookup.lookup_data import LookupData, outputs
from cardbuilder.lookup.value import ListValue, MultiListValue, PitchAccentValue


# thanks to @huntingdb whose notebook is the basis for some of the implementations
# https://github.com/huntingb/ojad-notebook/blob/master/scraping.ipynb


@outputs({
    Fieldname.AUDIO: MultiListValue,
    Fieldname.INFLECTIONS: ListValue,
    Fieldname.PITCH_ACCENT: MultiListValue,
})
class ScrapingOjad(WebApiDataSource):
    """Scrapes Japanese audio and pitch accent data from http://www.gavo.t.u-tokyo.ac.jp/ojad/."""

    # conjugation_box_dict = {
    #     'katsuyo_jisho_js': 'dictionary form',
    #     'katsuyo_masu_js': 'ます form',
    #     'katsuyo_te_js': 'て form',
    #     'katsuyo_ta_js': 'plain past',
    #     'katsuyo_nai_js': 'negative form',
    #     'katsuyo_nakatta_js': 'negative past',
    #     'katsuyo_ba_js': 'conditional',
    #     'katsuyo_shieki_js': 'causative',
    #     'katsuyo_ukemi_js': 'passive',
    #     'katsuyo_meirei_js': 'imperative',
    #     'katsuyo_kano_js': 'potential',
    #     'katsuyo_ishi_js': 'volitional'
    # }

    pitch_accent_dict = defaultdict(lambda: PitchAccentValue.PitchAccent.LOW, {
        'accent_plain': PitchAccentValue.PitchAccent.HIGH,
        'accent_top': PitchAccentValue.PitchAccent.DROP
    })

    base_url = "http://www.gavo.t.u-tokyo.ac.jp/ojad/"

    def __init__(self, male_audio: bool = True):
        super(ScrapingOjad, self).__init__()
        self.male_audio = male_audio

    def _secondary_audio_url(self, elem_id: str):
        num = "00" + str(math.floor(int(elem_id.split("_")[0]) / 100))
        gender = elem_id.split("_")[-1]
        return f"{self.base_url}sound4/mp3/" + gender + "/" + num[-3:] + "/" + elem_id + ".mp3"

    def _audio_file_url(self, elem_id: str):
        # logic taken from the javascript pronounce_play() function on the OJAD page
        return f'{self.base_url}ajax/wave_download/{elem_id}/{elem_id}'

    def _query_api(self, form: str) -> str:
        url = f'{self.base_url}search/index/sortprefix:accent/narabi1:kata_asc/' \
              f'narabi2:accent_asc/narabi3:mola_asc/yure:visible/curve:fujisaki/details:invisible/limit:20/word:{form}'

        html = requests.get(url).content
        return html.decode('utf-8')

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        parsed = BeautifulSoup(content, 'html.parser')
        word_table = parsed.find('table', attrs={'id': 'word_table'})

        if word_table is None:
            raise WordLookupException(f'Ojad returned no results for word form "{form}"')

        audio = defaultdict(list)
        pitch_accent = defaultdict(list)
        inflections = set()

        for word_row in word_table.find('tbody').find_all('tr'):
            for conj_box in word_row.find_all('td', attrs={'class': 'katsuyo'}):
                # conj_form = next(iter(set(conj_box['class']) - {'katsuyo'}))  # not using this currently

                pronunciation_divs = conj_box.find_all('div', attrs={'class': 'katsuyo_proc'})

                for pron in pronunciation_divs:
                    male_button = pron.find('a', attrs={'class': 'katsuyo_proc_male_button'})
                    female_button = pron.find('a', attrs={'class': 'katsuyo_proc_female_button'})

                    prioritized_pron_buttons = [male_button, female_button] if self.male_audio else [female_button,
                                                                                                     male_button]
                    audio_button = next(iter(x for x in prioritized_pron_buttons if x is not None), None)

                    accented_word = pron.find("span", class_="accented_word")
                    morae_elems = list(accented_word.children)

                    accent_data = []
                    reading = ''
                    for span in morae_elems:
                        span_accent_class = span.get('class')[0]
                        accent_value = self.pitch_accent_dict[span_accent_class]
                        accent_data.append(accent_value)
                        reading += span.find("span", class_="char").string

                    inflections.add(reading)

                    if audio_button is not None:
                        audio[reading].append(self._audio_file_url(audio_button['id']))

                    pitch_accent[reading].append(PitchAccentValue(accent_data, reading))

        if len(inflections) <= 0:
            raise WordLookupException(f'Found no data for word form "{form}" in Ojad')

        return self.lookup_data_type(word, form, content, {
            Fieldname.AUDIO: MultiListValue([(list_val, header_val)
                                             for header_val, list_val in audio.items()]),
            Fieldname.INFLECTIONS: ListValue(list(inflections)),
            Fieldname.PITCH_ACCENT: MultiListValue([(list_val, header_val)
                                                    for header_val, list_val in pitch_accent.items()])
        })

