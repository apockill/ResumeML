import os
import pickle

from data_visualisation.confusion import generate_confusion_matrix, plot_confusion_matrix
from data_visualisation.tsne import plot_tsne
from brain import Brain

import numpy as np


tests_dir = "test_dir\\dataset_1"
tests_paths = [entry.path for entry in os.scandir(tests_dir) if entry.is_dir()]

data = pickle.load(open("./test_dir/dataset_1/FROM_skills_TO_industry_MININPUTSPER_1_INPUTSAMPLES_100_OUTPUTSAMPLES_2500.pickle", "rb"))

test_inputs = data["inputs"][-10000:]
test_outputs = data["outputs"][-10000:]

# Get the labels for each output
test_outputs = [np.argmax(out) for out in test_outputs]

# Get the plots for every single test run so far
for test_path in tests_paths:

    with Brain(test_path, data["output_lexicon"]) as brain:
        # Generate the confusion matrix
        predictions = [brain.predict(input) for input in test_inputs]
        cnf_matrix = generate_confusion_matrix(predictions, test_outputs)

        plot_title = os.path.basename(test_path)
        save_to = os.path.join(test_path, "confusion_matrix.png")
        plot_confusion_matrix(cnf_matrix, data["output_lexicon"], normalize=True, title=plot_title, save_to=save_to)

        save_to = os.path.join(test_path, "tsne_plot.png")
        plot_tsne(predictions, save_to=save_to)