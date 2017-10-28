import random
from collections import OrderedDict

import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


def x_to_color(x):
    """ X is anything that can be used as a seed """
    random.seed(x)
    return np.asarray([[random.uniform(.1, 1) for i in range(3)]])


def plot_tsne(predictions, iterations=15000, save_to=None, show_plot=False):
    """
    :param features_list: A list of samples, where each sample is a a layer of the network before softmax
    :param features_names: The names, in order, corresponding to each element of the features_list
    :param brain: Access object for the model
    :return:
    """

    # predictions = predictions[:1000]
    features_list = np.asarray([pred.transfer_layer for pred in predictions])
    features_names = [pred.name for pred in predictions]

    # First use PCA to reduce the dimensionality of the problem to 50, something that TSNE could handle
    pca_down_to = 100
    if len(features_list[0]) > pca_down_to:
        pca = PCA(n_components=pca_down_to)
        features_list = pca.fit_transform(features_list)


    # Clear previous plot information
    plt.clf()
    plt.cla()
    plt.close()

    tsne = TSNE(perplexity=20, n_components=2, init='random', n_iter=iterations)
    print("Starting TSNE")
    low_dim_features = tsne.fit_transform(features_list)
    print("Done with TSNE")

    # Count how many dots have been plotted for each label, and limit it
    total_per = {name:0 for name in features_names}
    for i, label in enumerate(features_names):
        if total_per[label] > 100: continue
        total_per[label] += 1

        x, y = low_dim_features[i, :]
        plt.scatter(x, y, facecolors=x_to_color(label), label=label)
        # plt.annotate(label,
        #              xy=(x, y),
        #              xytext=(5, 2),
        #              textcoords='offset points',
        #              ha='right',
        #              va='bottom')

    # Create the legend (without duplicate labels)
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='upper_right', numpoints=1, ncol=3, bbox_to_anchor=(0, 0)) # loc='upper left', numpoints=1, ncol=3, fontsize=8, bbox_to_anchor=(0, 0))

    if show_plot:
        plt.show()

    if save_to is not None:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(12, 12)
        plt.savefig(save_to, bbox_inches="tight", dpi=100)


if __name__ == "__main__":
    import random
    # outs = 1000
    # features = [[random.uniform(.9, 1.1) for x in range(0, outs)] for x in range(0, 50)] +\
    #             [[random.uniform(.5, .7) for x in range(0, outs)] for x in range(0, 25)] +\
    #             [[random.uniform(0, .3) for x in range(0, outs)] for x in range(0, 75)]
    #
    # plot_tsne(features, [], [])
    import os
    import pickle

    from brain import Brain


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

            features = [brain.predict("")]
