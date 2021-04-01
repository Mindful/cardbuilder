from cardbuilder.resolution.anki import AkpgResolver
from cardbuilder.resolution.delimited import CsvResolver

instantiable_resolvers = {
    'csv': CsvResolver,
    'anki': AkpgResolver
}
