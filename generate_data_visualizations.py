import os
import pickle

from data_vis.confusion import generate_confusion_matrix, plot_confusion_matrix
from brain import Brain

import numpy as np


test_dir = "test_dir\\"
test_dirs = [os.path.join(test_dir, sub_dir) for sub_dir in os.listdir(test_dir)]

data = pickle.load(open("skills_to_industry.pickle", "rb"))

test_inputs = data["inputs"][-10000:]
test_outputs = data["outputs"][-10000:]


# Get the labels for each output
test_outputs = [np.argmax(out) for out in test_outputs]

# Get the plots for every single test run so far
for test_name in os.listdir(test_dir):
    test_path = os.path.join(test_dir, test_name)

    with Brain(test_dirs[0], data["output_lexicon"]) as brain:
        # Generate the confusion matrix
        cnf_matrix = generate_confusion_matrix(test_inputs, test_outputs, brain)
        plot_title = test_name
        save_to = os.path.join(test_path, "confusion_matrix.png")
        plot_confusion_matrix(cnf_matrix, data["output_lexicon"], normalize=True, title=plot_title, save_to=save_to)
