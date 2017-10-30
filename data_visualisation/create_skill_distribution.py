import pickle
from collections import Counter

import matplotlib.pyplot as plt


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

    # Clear previous plot information
    plt.clf()
    plt.cla()
    plt.close()

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
