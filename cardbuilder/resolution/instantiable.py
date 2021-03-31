from cardbuilder.resolution.anki import AkpgResolver
from cardbuilder.resolution.delimited import CsvResolver

i = {
    'csv': CsvResolver,
    'anki': AkpgResolver
}
