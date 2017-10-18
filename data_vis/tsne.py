import random

from sklearn.datasets import fetch_mldata
from sklearn.decomposition import PCA


def generate_pca(features_list, features_names, brain):
    """
    :param features_list: A list of samples, where each sample is a a layer of the network before softmax
    :param features_names: The names, in order, corresponding to each element of the features_list
    :param features_names: The names, in order, corresponding to each element of the features_list
    :return:
    """
    pca = PCA(n_components=2)

    features_reduced = pca.fit_transform(features_list)



# TRASH
if __name__ == "__main__":
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
            # Generate the PCA chart
            features = [brain.predict_transfer_values("")]
