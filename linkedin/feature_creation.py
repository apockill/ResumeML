import pickle
import os
from collections import Counter
from random import shuffle

from linkedin.sanitization import clean_feature


def create_lexicon(all_feature_strings, min_uses):
    """
    Each skill will be listed ONCE

    :param lemmatizer: A WordNetLemmatizer object
    :param all_feature_strings: A list of strings representing skills, locations, or whatever features will be input to the network.
        It specifically includes duplicates. For example, if you want to train on skills, the all_feature_strings
        variable will be a list of EVERY SKILL from EVERY PERSON, INCLUDING DUPLICATES.
        If it's location + skill, same deal. It's every skill and every location, including duplicates.
    :param min_uses: Minimum amount of times that a skill has to exist for it to be added as an input to the network
    :return: Returns a list of the skills that will actually be used
    """

    # Clean data
    cleaned = [clean_feature(skill) for skill in all_feature_strings]

    # Get rid of words that are too rare or too common
    keep_words = []
    counter = Counter(cleaned)

    for word in counter.keys():
        if counter[word] > min_uses:
            keep_words.append(word)

    no_duplicates = list(set(keep_words))
    no_duplicates.sort()
    return no_duplicates


def hot_feature(lexicon, user_features):
    """
    Example
    lexicon = ["nail painting", "management", "matlab"]
    user_features = ["matlab", "lawn care", "nail painting"]
    output: [1, 0, 1]  ([1: has nail painting, 0: does not have management, 1: has matlab)

    :param lexicon: A list of strings with no duplicates, where order matters
    :param user_features: A list of strings to find the hot_array relative to the lexicon
    """

    # Clean the user features
    user_features = list(set([clean_feature(feature) for feature in user_features]))

    output = [0] * len(lexicon)
    for feature in user_features:
        try:
            output[lexicon.index(feature)] = 1
        except ValueError: pass
    return output


def get_features(profile, feature_list):
    """
    :param profile:
    :param feature_list: A list of strings. Currently supports
        "skills"
        "current_company"
        "location"
        "all_companies"
    :return: A list of strings of all the features, duplicates included, order doesn't necessarily matter.
    """
    supported_features = ["skills", "current_company", "location", "all_companies", "industry"]
    # Verify that all the features being requested are implemented
    assert all([feature in supported_features for feature in feature_list]),\
            "One of the features you requested does not exist! Supported: " + str(supported_features) + \
            "Your Request:" + str(feature_list)

    features = []
    if "skills" in feature_list:
        features += profile.skills

    if "current_company" in feature_list:
        if profile.current_company is not None:
            features.append(profile.current_company)

    if "location" in feature_list:
        if profile.location is not None:
            features.append(profile.location)

    if "all_companies" in feature_list:
        features += profile.all_companies

    if "industry" in feature_list:
        if profile.industry is not None:
            features.append(profile.industry)

    # Throw errors just in case profile code is faulty
    if not all(isinstance(f, str) for f in features):
        raise TypeError("Found a feature that was not a string!")
    if None in features:
        raise TypeError("Found None in features!")
    if [] in features:
        raise TypeError("Found an empty list in features!")

    return features


def create_features(reader, input_features, output_feature,
                    min_input_samples=None,
                    min_output_samples=None,
                    input_lexicon=None,
                    output_lexicon=None,
                    save_dir=None):
    """
    Returns the train_inputs train_outputs and test_inputs and test_outputs for skills

    :param reader: The profile reader
    :save_to_file: If you want to save to a pickle
    :input_list: A list of any supported strings by get_features()
    :output: A string, supported by get_features()
    :return: A json of the following format:
        {
         "inputs": A list of hot-encoded arrays,
         "outputs": A list of one-hot encoded arrays,
         "input_lexicon": The lexicon for inputs,
         "output_lexicon": The lexicon for outputs
        }
    """

    # Verify that the output is not one of the inputs
    assert output_feature not in input_features, "The output was one of the input!"


    # Create a lexicon of all possible inputs, if the user didn't specify one
    if input_lexicon is None or output_lexicon is None:
        input_strings = []
        output_strings = []
        for profile in reader:
            input_strings += get_features(profile, input_features)
            output_strings += get_features(profile, [output_feature])
    if input_lexicon is None:
        input_lexicon = create_lexicon(input_strings, min_input_samples)
    if output_lexicon is None:
        output_lexicon = create_lexicon(output_strings, min_output_samples)


    # Generate the input and output corresponding arrays
    all_hot_inputs = []
    all_hot_outputs = []
    shuffled_profiles = [profile for profile in reader]
    shuffle(shuffled_profiles)
    for i, profile in enumerate(shuffled_profiles):
        inputs = get_features(profile, input_features)
        outputs = get_features(profile, [output_feature])
        if len(inputs) == 0:
            continue
        if len(outputs) == 0:
            continue

        print("Processing I/O for profile", str(i) + "/" + str(len(reader)))
        hot_input = hot_feature(input_lexicon, inputs)
        hot_output = hot_feature(output_lexicon, outputs)

        if all([x == 0 for x in hot_output]):
            # print("ALL ARE 0 FOR OUTPUT")
            continue
        if all([x == 0 for x in hot_input]):
            # print("ALL ARE 0 FOR INPUT")
            continue

        all_hot_inputs.append(hot_input)
        all_hot_outputs.append(hot_output)

    data = {"inputs": all_hot_inputs, "outputs": all_hot_outputs,
            "input_lexicon": input_lexicon, "output_lexicon": output_lexicon}
    if save_dir is not None:
        filename = make_pickle_name(input_features, output_feature, input_lexicon, output_lexicon)
        save_file = os.path.join(save_dir, filename)
        pickle.dump(data, open(save_file, "wb"))

    print("Skipped", len(reader) - len(all_hot_inputs), "profiles")
    return data


def make_pickle_name(inputs, output, input_lexicon, output_lexicon):
    input_str = '_'.join(inputs)
    input_num = str(len(input_lexicon))
    output_num = str(len(output_lexicon))
    return "FROM_" + input_str + "_TO_" + output + "_INPUTS_" + input_num + "_OUTS_" + output_num + ".pickle"


if __name__ == "__main__":
    all_skills = ["jumping"] * 10 + ["manage"] * 10 + ["matlab"] * 1000 + ["lawn and order"] * 7 + ["and order lawn"] * 100 + ["blarg"] * 1
    user_skills = ["matlab", "paint nails", "and lawn order", "matlab's", "management", "blarg", "donkey"]

    skill_lexicon = create_lexicon(all_skills, 5)

    output = hot_feature(skill_lexicon, user_skills)
    print(clean_feature("google"))
    print("lexicon", skill_lexicon, "Out", output)

