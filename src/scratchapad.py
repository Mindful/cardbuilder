from merriam_webster import LearnerDictionary, CollegiateThesaurus


def main():
    with open('mw_learner_api_key.txt') as f:
        learner_key = f.readlines()[0]

    with open('mw_thesaurus_api_key.txt') as f:
        thesaurus_key = f.readlines()[0]

    # ld = LearnerDictionary(learner_key)
    # dog = ld.lookup_word('dog')
    # print(dog)

    ct = CollegiateThesaurus(thesaurus_key)
    hot = ct.lookup_word('hot')
    print(hot)


if __name__ == '__main__':
    main()


