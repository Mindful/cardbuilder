
# Cardbuilder
A command line tool and Python library for creating language learning flashcards in a wide variety of languages.

<hr/>
<p align="center">
    <a href="https://pypi.org/project/cardbuilder/">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/cardbuilder">
    </a>
    <a href='https://cardbuilder.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/cardbuilder/badge/?version=latest' alt='Documentation Status' />
    </a>
    <a href="https://github.com/Mindful/cardbuilder/blob/main/LICENSE.txt">
        <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
    </a>
    <br/>
</p>

## Quick Start

Cardbuilder can output flashcards in several different formats, but the quick start will focus on [Anki](https://apps.ankiweb.net/).

```
pip install cardbuilder
printf "暗記\nカード\n作る" > words.txt
cardbuilder ja_to_en --input words.txt --output cards
```

That's it - cards built! Just import `cards.apkg` into Anki and you're good to go. Note that the first time you run Cardbuilder it will download data which may take some time, but this only has to be done once.


## Supported Languages 

| Learning Language | From Language | 
|----------|:-------------:|
| Japanese |  English 
| Esperanto | English   
| English | Japanese


## FAQ

### Can you add support for `<language>` or `<data source>`? 

Probably! You're welcome to [open an issue](https://github.com/Mindful/cardbuilder/issues/new) requesting support for a new language and/or new source of data, although in both cases it really helps if you can point to the location of a publicly available web API or dictionary file. Alternatively, we welcome pull requests implementing new [data sources](#data-sources).

### Can you add support for `<flashcard app>`?

As with new languages, it's likely possible and you're welcome to [open an issue](https://github.com/Mindful/cardbuilder/issues/new) or submit a PR yourself for a new [card resolver](#card-resolvers).

### Can I generate flashcards without writing code?

Not yet, but we're planning to add a command-line interface to handle simple use cases in the future.

### Is this like [genanki](https://github.com/kerrickstaley/genanki)?

No, `genanki` is a great library and Cardbuilder depends on it to output Anki decks, but the two packages serve different purposes. `genanki` is specifically for taking data and transforming it into the format that Anki uses, while Cardbuilder attempts to simplify the process of going from a list of words to a set of complete flashcards with all the required information. 
