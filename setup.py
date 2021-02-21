import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cardbuilder",
    version="0.0.1",
    author="Joshua Tanner",
    author_email="mindful.jt@gmail.com",
    description="A package for programmatically generating language learning flashcards",
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
)