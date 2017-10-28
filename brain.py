import os

import tensorflow as tf
import numpy as np

session = None


class Label:
    # Represents a prediction from the network
    def __init__(self, input, output_layer, transfer_layer, output_activation, index, label_text):
        """
        :param input: The hot-input that was given to get this output
        :param output_layer: The final output layer after softmax
        :param output_activation: The final output layer of the network, before softmax
        :param transfer_layer: The second to last layer of the network, after relu
        :param index:
        :param label_text:
        """
        self.input = input
        self.output = output_layer
        self.output_activation = output_activation
        self.transfer_layer = transfer_layer
        self.id = index
        self.name = label_text

    def __repr__(self):
        return self.name


class Brain:
    def __init__(self, model_dir, output_lex):
        self.session = tf.Session()
        # Load the graph
        meta_file = os.path.join(model_dir, "saved-0.meta")
        saver = tf.train.import_meta_graph(meta_file)
        saver.restore(self.session, tf.train.latest_checkpoint(model_dir))
        graph = tf.get_default_graph()

        # Get the functions for the network
        transfer_layer = graph.get_tensor_by_name("hidden_layer_3/activation:0")
        self.input_tensor = graph.get_tensor_by_name("x:0")
        self.transfer_tensor = tf.nn.relu(transfer_layer)
        self.output_before_softmax = graph.get_tensor_by_name("output_layer/activation:0")
        self.output_tensor = tf.nn.softmax(logits=self.output_before_softmax)

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
        transfer_layer, output_layer, activation = self.session.run(
                                                        [self.transfer_tensor,
                                                         self.output_tensor,
                                                         self.output_before_softmax],
                                                        {self.input_tensor: input})
        output_activation = activation[0]
        output_layer = output_layer[0]
        transfer_layer = transfer_layer[0]
        index = int(round(np.argmax(output_layer), 0))
        label_text = self.output_lex[index]

        return Label(input, output_layer, transfer_layer, output_activation, index, label_text)

    def predict_transfer_values(self, input_arr):
        pass

    def get_label(self, onehot_output, output_lex):
        index = int(round(np.argmax(onehot_output), 0))
        label_text = self.output_lex[index]
        return label_text

    def close(self):
        self.session.close()
        tf.reset_default_graph()


