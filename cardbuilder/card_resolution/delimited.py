import csv
from typing import List

from card_resolution import ResolvedField
from card_resolution.resolver import Resolver


class CsvResolver(Resolver):
    def _output_file(self, rows: List[List[ResolvedField]], filename: str) -> str:
        final_out_name = '{}.csv'.format(filename.lower().replace(' ', '_'))
        with open(final_out_name, 'w+') as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL, quotechar='"', delimiter=',')
            w.writerows([field.value for field in row] for row in rows)

        return final_out_name
