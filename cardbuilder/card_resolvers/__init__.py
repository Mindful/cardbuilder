from cardbuilder.card_resolvers.anki import AkpgResolver
from cardbuilder.card_resolvers.delimited import CsvResolver
from cardbuilder.card_resolvers.field import ResolvedField, Field


instantiable = {
    'csv': CsvResolver,
    'anki': AkpgResolver
}
