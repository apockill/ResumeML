import os

import tensorflow as tf
import numpy as np

session = None

class Label:
    # Represents a prediction from the network
    def __init__(self, output_layer, transfer_layer, index, label_text):
        self.output_layer = output_layer
        self.transfer_layer = transfer_layer
        self.index = index
        self.name = label_text

    def __repr__(self):
        return self.name


class Brain:
    def __init__(self, model_dir, output_lex):
        self.session = tf.Session()

        # Load the graph
        meta_file = os.path.join(model_dir, "saved-1000.meta")
        saver = tf.train.import_meta_graph(meta_file)
        saver.restore(self.session, tf.train.latest_checkpoint(model_dir))
        graph = tf.get_default_graph()

        # Get the function for the network
        self.input_tensor = graph.get_tensor_by_name("x:0")
        self.transfer_tensor = graph.get_tensor_by_name("hidden_layer_3/activation:0")
        activation = graph.get_tensor_by_name("output_layer/activation:0")
        self.output_tensor = tf.nn.softmax(logits=activation)

        # Variables
        self.output_lex = output_lex

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def predict(self, input_arr):
        """
        :param input_arr: Hot encoded array of the inputs
        :return: The index of the classified output
        """

        input = np.array([input_arr])
        out = self.session.run([self.transfer_tensor, self.output_tensor], {self.input_tensor: input})[0]
        print(out)
        index = int(round(np.argmax(out), 0))
        label_text = self.output_lex[index]

        return Label(out, index, label_text)

    def predict_transfer_values(self, input_arr):
        pass

    def get_label(self, onehot_output, output_lex):
        index = int(round(np.argmax(onehot_output), 0))
        label_text = self.output_lex[index]
        return label_text

    def close(self):
        self.session.close()


