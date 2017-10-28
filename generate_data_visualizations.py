import os
import pickle

from data_visualisation.confusion import generate_confusion_matrix, plot_confusion_matrix
from data_visualisation.tsne import plot_tsne
from brain import Brain

import numpy as np

# Choose the folder to analyze
tests_dir = "test_dir\\dataset_1"


dataset_to_load = [pickle_file for pickle_file in os.listdir(tests_dir) if ".pickle" in pickle_file][0]
dataset_to_load = os.path.join(tests_dir, dataset_to_load)
data = pickle.load(open(dataset_to_load, "rb"))

print("Analyzing tests from dataset ", dataset_to_load)

tests_paths = [entry.path for entry in os.scandir(tests_dir) if entry.is_dir()]

# Get the test set from the chosen dataset
test_inputs = data["inputs"][-10000:]
test_outputs = data["outputs"][-10000:]
test_outputs = [np.argmax(out) for out in test_outputs]


test_results = {}
for test_path in tests_paths[::-1]:

    with Brain(test_path, data["output_lexicon"]) as brain:
        # Predict every object in the test set and get the model accuracy
        predictions = [brain.predict(input) for input in test_inputs]
        correct_preds = [pred for i, pred in enumerate(predictions) if pred.id == test_outputs[i]]
        test_results = len(correct_preds) / len(predictions)

        # Write test results to file
        with open(os.path.join(tests_dir, "results"), "a+") as results_file:
            results_file.write(test_path + "\t" + str(test_results) + "\n")


        # Generate the confusion matrix
        print("Generating confusion graph")
        cnf_matrix = generate_confusion_matrix(predictions, test_outputs)
        plot_title = os.path.basename(test_path)
        save_to = os.path.join(test_path, "confusion_matrix.png")
        plot_confusion_matrix(cnf_matrix, data["output_lexicon"], normalize=True, title=plot_title, save_to=save_to)

        # Get the correct predictions and generate a TSNE graph
        print("Generating TSNE graph")
        print("len b4", len(predictions), "Len after", len(correct_preds))
        save_to = os.path.join(test_path, "tsne_plot.png")
        plot_tsne(correct_preds, save_to=save_to, show_plot=False)