import re

from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer

lemmetizer = WordNetLemmatizer()
stemmer = PorterStemmer()


def clean_skill(skill):
    """ Given a skill, it will do the following operations on the string
    lowercase
    remove punctuation
    lemmatize each word
    stem each word
    sort each word alphabetically
    return a string
    """
    lower = skill.lower()
    word_list = lower.split()

    for i, word in enumerate(word_list):
        word_list[i] = re.sub("[^a-zA-Z]+", "", word)

    word_list = [lemmetizer.lemmatize(word, 'v') for word in word_list]
    word_list = [str(stemmer.stem(word)) for word in word_list]

    # Alphabetize the order of the words in skills
    word_list.sort()

    skill = " ".join(word_list)
    return skill
