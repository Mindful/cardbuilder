
# cardbuilder
<p align="left">
    <a href="https://pypi.org/project/cardbuilder/">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/cardbuilder">
    </a>
    <a href="https://github.com/Mindful/cardbuilder/blob/main/LICENSE.txt">
        <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
    </a>
    <br/>
</p>

`cardbuilder` helps streamline the process of programmatically generating language learning flashcards. We currently support the following language pairs, but we're adding more all the time.


| Learning Language | From Language | 
|----------|:-------------:|
| Japanese |  English 
| Esperanto | English   
| English | Japanese


## Installation

The easiest way to install is via pip:
```
pip install cardbuilder
```

The current package requirements are (likely unnecessarily) quite specific, so it will likely be easiest to do the install in a fresh environment of some kind, such as a new conda environment. 

Cloning the source from github and pip installing the `requirements.txt` file should also work fine, though.

## Usage

Broadly, flashcards are constructed by declaring a source of data,  the list of input words you want to generate flashcards for, and a set of fields which correspond to data that will be populated in each flaschard.

An extremely simple example that looks up Japanese words from [Jisho](jisho.org) and returns English definitions looks like this: 

```
from cardbuilder.card_resolvers import Field, CsvResolver
from cardbuilder.common.fieldnames import WORD, DEFINITIONS, DETAILED_READING
from cardbuilder.data_sources.ja_to_en import Jisho
from cardbuilder.word_lists import InputList

dictionary = Jisho()
words = InputList(input_file_name)

fields = [
    Field(dictionary, WORD, 'word'),
    Field(dictionary, DEFINITIONS, 'definitions'),
    Field(dictionary, DETAILED_READING, 'readding'),
]

resolver = CsvResolver(fields)
failed_resolutions = resolver.resolve_to_file(words, output_filename)
```

Each component is explained in its own section below, but there are also more in-depth [examples](https://github.com/Mindful/cardbuilder/tree/main/cardbuilder/examples) available to showcase what a finished script looks like. 

## Word Lists

Word lists are an abstraction representing the list of input words - the words that you want to retrieve information for and turn into flashcards. To use one in a script, simply initialize it and pass it in as the first argument of your card resolver's `resolve_to_file` method.

There are prebuilt lists of words available in packages like `cardbuilder.word_lists.en`, but for reading custom input you want the [InputList](https://github.com/Mindful/cardbuilder/blob/main/cardbuilder/word_lists/input_list.py). This simply takes the name of an input file, formatted with one word per line like in the example below.

```
impertinent
superflous
catastrophe
...
```

## Data Sources
Data sources represent - as their name suggests - sources of data such as dictionaries or other types of databases containing linguistic information. In order to use a data source in a card producing script, simply
initialize it and pass it in as the first argument of a `Field` object. Many data sources will need to download data and/or build database tables the first time they are constructed, but this happens automatically. Most can be constructed with no arguments at all, although some require specific information - for example, the [MerriamWebster](https://github.com/Mindful/cardbuilder/blob/main/cardbuilder/data_sources/en_to_en/merriam_webster.py) data source requires API keys.

```
from cardbuilder.data_sources.en_to_en import MerriamWebster

mw = MerriamWebster("leaner's dict api key", "thesaurus api key")
```

Data sources are organized in packages named after the language they
expect input in and the language they produce output in, like 
`cardbuilder.data_sources.inputlang_to_outputlang`.

 
## Card Resolvers

Card resolvers are responsible for actually producing flaschards. They are initialized with a list of `Field` objects, which include information about what output fields to populate and which data source to use. Actually generating cards is as easy as calling `resolver.resolve_to_file(words, output_filename)`, although some resolvers benefit from having extra information set. For example, the Anki resolver [AkpgResolver](https://github.com/Mindful/cardbuilder/blob/main/cardbuilder/card_resolvers/anki.py) includes methods that allow you to control the format and styling of cards in the generated Anki deck. 

```
resolver.set_card_templates([
            {
                'name': "<card name">,
                'qfmt': "<card front>",
                'afmt': "<card back>",
            }
        ], css="<card CSS>")
```




## FAQ

### Can you add support for `<language>` or `<data source>`? 

Probably! You're welcome to [open an issue](https://github.com/Mindful/cardbuilder/issues/new) requesting support for a new language and/or new source of data, although in both cases it really helps if you can point to the location of a publicly available web API or dictionary file. Alternatively, we welcome pull requests implementing new [data sources](#data-sources).

### Can you add support for `<flashcard app>`?

As with new languages, it's likely possible and you're welcome to [open an issue](https://github.com/Mindful/cardbuilder/issues/new) or submit a PR yourself for a new [card resolver](#card-resolvers).

### Can I generate flashcards without writing code?

Not yet, but we're planning to add a command-line interface to handle simple use cases in the future.

### Is this like [genanki](https://github.com/kerrickstaley/genanki)?

No, `genanki` is a great library and `cardbuilder` depends on it to output Anki decks, but the two packages serve different purposes. `genanki` is specifically for taking data and transforming it into the format that Anki uses, while `cardbuilder` attempts to simplify the process of going from a list of words to a set of complete flashcards with all the required information. 
