import pickle
from collections import Counter

from data_visualisation.matplotlib_utils import reset_plot

import matplotlib.pyplot as plt


def plot_accuracy_skill_count(predictions, expected_outputs, save_to=None, show_plot=False):
    data = {}  # {skill_count: [True, False, False]} where T/F means it was correct or not

    bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 17, 20, 23, 27, 32, 65]

    for i, pred in enumerate(predictions):
        count = list(pred.input).count(1)
        # bin = [bin for bin in bins if count < bin][0]
        bin = count
        if bin not in data: data[bin] = []
        data[bin].append(pred.id == expected_outputs[i])

    num_skills = []
    accuracy = []
    # print("Counts per bin: ", [[bin, len(data[bin])] for bin in sorted(data.keys())])
    for bin in sorted(data.keys()):
        acc = data[bin].count(True) / len(data[bin])
        accuracy.append(acc * 100.0)
        num_skills.append(bin)
        print(str(bin) + "\t" + str(acc))

    reset_plot()

    plt.plot(num_skills, accuracy)
    plt.title("Effect of Skill Count on Prediction Accuracy")
    plt.xlabel("Skill Count")
    plt.ylabel("Average Accuracy")

    if show_plot:
        plt.show()

    if save_to is not None:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(6, 6)
        plt.savefig(save_to, bbox_inches="tight", dpi=100)


def plot_skill_distribution(data, save_to=None, show_plot=False):
    # Prep the data
    num_tests = 10000  # Number of test examples
    inputs = data["inputs"][:-num_tests]
    outputs = data["outputs"][:-num_tests]

    avg = 0
    counts = []
    for input in inputs:
        count = input.count(1)
        avg += count
        counts.append(count)

    counted = Counter(counts)
    num_skills = []
    num_people = []
    for i in range(0, 1000):
        if i in counted:
            num_skills.append(i)
            num_people.append(counted[i])

    reset_plot()

    plt.plot(num_skills, num_people)
    plt.title("Dataset Skill Count Distribution")
    plt.xlabel("Skill Count")
    plt.ylabel("Number of Profiles")

    if show_plot:
        plt.show()

    if save_to is not None:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(12, 12)
        plt.savefig(save_to, bbox_inches="tight", dpi=100)
