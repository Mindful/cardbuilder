from typing import List

from cardbuilder.resolution.field import ResolvedField


class CardData:
    def __init__(self, fields: List[ResolvedField]):
        self.fields = fields

