import itertools
import numpy as np
import matplotlib.pyplot as plt

from data_visualisation.matplotlib_utils import reset_plot

from sklearn import svm, datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

# import some data to play with
# iris = datasets.load_iris()
# X = iris.data
# y = iris.target
# class_names = iris.target_names
# print(class_names)
# Split the data into a training set and a test set
# X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

# Run classifier, using a model that is too regularized (C too low) to see the impact on the results
# classifier = svm.SVC(kernel='linear', C=0.01)
# y_pred = classifier.fit(X_train, y_train).predict(X_test)


def plot_confusion_matrix(cm, classes, normalize=False,
                          title='Confusion matrix',
                          show_plot=False,
                          save_to=None,
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    reset_plot()

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=90)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    # for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
    #     plt.text(j, i, format(cm[i, j], fmt),
    #              horizontalalignment="center",
    #              color="white" if cm[i, j] > thresh else "black")

    # plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

    if save_to is not None:
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(12, 12)
        plt.savefig(save_to, bbox_inches="tight", dpi=100)

    if show_plot:
        plt.show()


def generate_confusion_matrix(predictions, expected_outputs):

    pred_outputs = []
    for pred in predictions:
        pred_outputs.append(pred.id)

    cnf_matrix = confusion_matrix(expected_outputs, pred_outputs)
    return cnf_matrix
