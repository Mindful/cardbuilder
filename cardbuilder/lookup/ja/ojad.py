import requests

from bs4 import BeautifulSoup

from cardbuilder.input.word import Word
from cardbuilder.lookup.data_source import WebApiDataSource
from cardbuilder.lookup.lookup_data import LookupData


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

    def _query_api(self, form: str) -> str:
        url = 'http://www.gavo.t.u-tokyo.ac.jp/ojad/search/index/sortprefix:accent/narabi1:kata_asc/' \
              f'narabi2:accent_asc/narabi3:mola_asc/yure:visible/curve:fujisaki/details:invisible/limit:20/word:{form}'

        html = requests.get(url).content
        return str(html)

    def parse_word_content(self, word: Word, form: str, content: str) -> LookupData:
        parsed = BeautifulSoup(content, 'html.parser')
        word_table = parsed.find('tbody', attrs={'class': 'ui-sortable'})

        for word_row in word_table.find_all('tr'):
            for conj_box in word_row.find_all('td', attrs={'class': 'katsuyo'}):
                pass

