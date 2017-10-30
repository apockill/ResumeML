import re

from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer

lemmetizer = WordNetLemmatizer()
stemmer = PorterStemmer()


def clean_feature(skill):
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

    # Remove punctuation, lemmetize, and stem the words
    for i, word in enumerate(word_list):
        sanitized_word = re.sub("[^a-zA-Z]+", "", word)
        sanitized_word = lemmetizer.lemmatize(sanitized_word, 'v')
        sanitized_word = str(stemmer.stem(sanitized_word))
        word_list[i] = sanitized_word

    # word_list = [lemmetizer.lemmatize(word, 'v') for word in word_list]
    # word_list = [str(stemmer.stem(word)) for word in word_list]

    # Alphabetize the order of the words in the string
    word_list.sort()

    skill = " ".join(word_list)
    return skill


if __name__ == "__main__":
    words = ["management", "manager", "managing", "run", "running", "ran"]

    print("Lemmatizing")
    for word in words:
        print(word, lemmetizer.lemmatize(word, "v"))

    print("\nStemming")
    for word in words:
        print(word, stemmer.stem(word))
