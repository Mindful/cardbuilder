import requests

from bs4 import BeautifulSoup

from cardbuilder.common.fieldnames import Fieldname
from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import WebApiDataSource
from cardbuilder.lookup.lookup_data import LookupData, outputs
from cardbuilder.lookup.value import MultiValue, ListValue

# thanks to @huntingdb whose notebook is the basis for some of the implementations
# https://github.com/huntingb/ojad-notebook/blob/master/scraping.ipynb


@outputs({
    Fieldname.AUDIO: MultiValue,
    Fieldname.INFLECTIONS: ListValue,
    Fieldname.PITCH_ACCENT: MultiValue,
})
class ScrapingOjad(WebApiDataSource):

    conjugation_box_dict = {
        'katsuyo_jisho_js': 'dictionary form',
        'katsuyo_masu_js': 'ます form',
        'katsuyo_te_js': 'て form',
        'katsuyo_ta_js': 'plain past',
        'katsuyo_nai_js': 'negative form',
        'katsuyo_nakatta_js': 'negative past',
        'katsuyo_ba_js': 'conditional',
        'katsuyo_shieki_js': 'causative',
        'katsuyo_ukemi_js': 'passive',
        'katsuyo_meirei_js': 'imperative',
        'katsuyo_kano_js': 'potential',
        'katsuyo_ishi_js': 'volitional'
    }

    base_url = "http://www.gavo.t.u-tokyo.ac.jp/ojad/"

    def _audio_file_url(self, elem_id: str):
        # logic taken from the javascript pronounce_play() function on the OJAD page
        return f'{self.base_url}ajax/wave_download/{elem_id}/{elem_id}'

    def _query_api(self, form: str) -> str:
        url = f'{self.base_url}search/index/sortprefix:accent/narabi1:kata_asc/' \
              f'narabi2:accent_asc/narabi3:mola_asc/yure:visible/curve:fujisaki/details:invisible/limit:20/word:{form}'

        html = requests.get(url).content
        return str(html)

    def parse_word_content(self, word: Word, form: str, content: str, following_link: bool = False) -> LookupData:
        parsed = BeautifulSoup(content, 'html.parser')
        word_table = parsed.find('table', attrs={'id': 'word_table'}).find('tbody')

        for word_row in word_table.find_all('tr'):
            for conj_box in word_row.find_all('td', attrs={'class': 'katsuyo'}):
                conj_form = next(iter(set(conj_box['class']) - {'katsuyo'}))
                male_pron_button = conj_box.find('a', attrs={'class': 'katsuyo_proc_male_button'})
                female_pron_button = conj_box.find('a', attrs={'class': 'katsuyo_proc_female_button'})

                male_audio_url = self._audio_file_url(male_pron_button['id'])
                female_audio_url = self._audio_file_url(female_pron_button['id'])
                print('debuggy')

