from collections import Counter

from mlearning.sanitization import clean_skill


def create_lexicon(skills, min_uses):
    """
    Each skill will be listed ONCE

    :param lemmatizer: A WordNetLemmatizer object
    :param skills: A list of ALL skills
    :param min_uses: Minimum amount of times that a skill has to exist for it to be added as an input to the network
    :return: Returns a list of the skills that will actually be used
    """

    # Clean data
    cleaned = [clean_skill(skill) for skill in skills]

    # Get rid of words that are too rare or too common
    keep_words = []
    counter = Counter(cleaned)

    for word in counter.keys():
        if counter[word] > min_uses:
            keep_words.append(word)

    return list(set(keep_words))


def hot_feature(lexicon, user_features):
    """
    Example
    lexicon = ["nail painting", "management", "matlab"]
    user_features = ["matlab", "lawn care", "nail painting"]
    output: [1, 0, 1]  ([1: has nail painting, 0: does not have management, 1: has matlab)

    :param lexicon: A list of strings with no duplicates, where order matters
    :param user_features: A list of strings to find the hot_array relative to the lexicon
    """

    user_features = [clean_skill(feature) for feature in user_features]
    output = []
    for feature in lexicon:
        # Put a 1 if the user has a skill, 0 otherwise
        output.append(1 if feature in user_features else 0)
    return output


def create_skill_features(reader):
    all_skills = reader.skill
    skill_lexicon = create_lexicon(all_skills, 5)

    for profile in reader:
        skill_feature = hot_feature(skill_lexicon, profile.skills)
        print("in: ", profile.skills, "out: ", skill_feature)


if __name__ == "__main__":
    all_skills = ["manage"] * 10 + ["matlab"] * 1000 + ["lawn and order"] * 7
    user_skills = ["matlab", "paint nails", "and lawn order", "matlab's", "management"]

    skill_lexicon = create_lexicon(all_skills, 5)

    output = hot_feature(skill_lexicon, user_skills)
    print("lexicon", skill_lexicon, "Out", output)