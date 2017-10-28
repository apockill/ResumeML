import os
import pickle

from brain import Brain
from linkedin.html_profile import HTMLProfile
from linkedin.feature_creation import hot_feature, get_features

import numpy as np
import tensorflow as tf
from selenium.webdriver import Chrome as Driver


def predict_profile(brain, html, input_lexicon, output_lexicon, input_features, output_feature):
    """
    This class predicts the output for this profile given an inputlexicon, outputlexicon, inputfeatures, outputfeatures
    :param html: A string of html
    :param input_features: A list of strings accepted by get_features
    :param output_feature: A string accepted by get_features
    :return:
    """
    print("Starting Analysis...")

    profile = HTMLProfile(html)
    inputs = get_features(profile, input_features)
    output = get_features(profile, [output_feature])

    hot_input = hot_feature(input_lexicon, inputs)
    hot_expected_out = hot_feature(output_lexicon, output)

    predicted = brain.predict(hot_input)
    sorted_outputs = np.argsort(predicted.output_activation)

    print("#" * 50)
    print("Analyzing", profile.name)
    print("Prediction Label", predicted)
    print("Included skills: ", hot_input.count(1), "skills out of", len(inputs))
    print("\nMost Likely Industries: ")
    for index in sorted_outputs[-5:][::-1]:
        print("\t", output_lexicon[index])

    print("\nLeast Likely Industries: ")
    for index in sorted_outputs[:5]:
        print("\t", output_lexicon[index])


if __name__ == "__main__":
    # Input paths
    tests_dir = "./test_dir/dataset_3"
    checkpoint_path = "2017-10-22-21-44 FEATURES944_LABELS42_LAYERS_4000_4000_4000_LR0.001000_BS1000_NE1000"
    driver_path = "./Resources/chromedriver.exe"


    # Prepare all the paths
    checkpoint_path = os.path.join(tests_dir, checkpoint_path)
    dataset_to_load = [pickle_file for pickle_file in os.listdir(tests_dir) if ".pickle" in pickle_file][0]
    dataset_to_load = os.path.join(tests_dir, dataset_to_load)

    # Load the dataset
    data = pickle.load(open(dataset_to_load, "rb"))
    input_lexicon = data["input_lexicon"]
    output_lexicon = data["output_lexicon"]

    # Open the browser
    browser = Driver(executable_path=driver_path)

    # wait for user to continue
    print("Please load a linkedin profile into the browser")
    with tf.device("/cpu:0"):
        with Brain(checkpoint_path, output_lexicon) as brain:
            while input("Press any key to start analysis, press 'q' to quit") != "q":
                html = browser.page_source
                predict_profile(brain, html, input_lexicon, output_lexicon, ["skills"], "industry")

    browser.close()