import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cardbuilder",
    version="0.0.1.2",
    author="Joshua Tanner",
    author_email="mindful.jt@gmail.com",
    description="A package for programmatically generating language learning flashcards",
    keywords="flashcards anki language learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mindful/cardbuilder",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[
        "requests ~= 2.25.1",
        "lxml ~= 4.6.2",
        "genanki ~= 0.10.1",
        "tqdm ~= 4.56.0",
        "pykakasi ~= 2.0.6",
        "unidic-lite ~= 1.0.8",
        "fugashi ~= 1.1.0"
    ]
)