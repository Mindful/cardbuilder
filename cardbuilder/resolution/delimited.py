import csv
from typing import List

from cardbuilder.resolution.card_data import CardData
from cardbuilder.resolution.resolver import Resolver


class CsvResolver(Resolver):
    def _output_file(self, rows: List[CardData], filename: str) -> str:
        final_out_name = '{}.csv'.format(filename.lower().replace(' ', '_'))
        with open(final_out_name, 'w+', encoding='utf-8') as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL, quotechar='"', delimiter=',')
            w.writerows([field.value for field in row.fields] for row in rows)

        return final_out_name
