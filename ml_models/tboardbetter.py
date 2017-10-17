from os.path import join
import time

import numpy as np
import tensorflow as tf
import pickle

# Import Data
print("Loading data...")
data = pickle.load(open("../skills_to_industry.pickle", "rb"))
print("in: ", len(data["inputs"]), "out: ", len(data["outputs"]), "in lex", len(data["input_lexicon"]), "out lex", len(data["output_lexicon"]))
num_tests = 10000  # Number of test examples
train_inputs = data["inputs"][:-num_tests]
train_outputs = data["outputs"][:-num_tests]
test_inputs = data["inputs"][-num_tests:]
test_outputs = data["outputs"][-num_tests:]

# Setup characteristics of network:
# Shape
node_h1 = 500
node_h2 = 500
node_h3 = 500
input_shape = np.shape(train_inputs)
output_shape = np.shape(train_outputs)
LOGDIR = "..\\test_dir\\"

# Learning
minibatch_size = 300
learning_rate = 0.0001
num_epochs = 5

# Tensorflow placeholders for inputs and outputs
input_tensor = tf.placeholder(tf.float32, shape=[None, input_shape[1]], name="input_tensor")
output_tensor = tf.placeholder(tf.float32, shape=[None, output_shape[1]], name="output_tensor")

all_train_summaries = []


def full_con_layer(input_data, size_in, size_out, name="fc"):
    with tf.name_scope(name):
        w = tf.Variable(tf.random_normal([size_in, size_out]), name="W")
        b = tf.Variable(tf.random_normal([size_out]), name="b")
        activation = tf.add(tf.matmul(input_data, w), b)

        # Make summaries for this layer
        global all_train_summaries
        train_weights_summary = tf.summary.histogram("weights", w)
        train_biases_summary = tf.summary.histogram("biases", b)
        train_activations_summary = tf.summary.histogram("activations", activation)
        layer_summaries = [train_weights_summary, train_biases_summary, train_activations_summary]
        all_train_summaries += layer_summaries
        return activation


def neural_network(data):
    """
    Sets up structure and model of nn
    :param data: followed tutorials.... Unused???
    :return: output activation
    """
    hidden_layer_1 = full_con_layer(input_tensor, input_shape[1], node_h1, name="hidden_layer_1")
    hidden_layer_2 = full_con_layer(tf.nn.relu(hidden_layer_1), node_h1, node_h2, name="hidden_layer_2")
    hidden_layer_3 = full_con_layer(tf.nn.relu(hidden_layer_2), node_h2, node_h3, name="hidden_layer_3")
    output_layer = full_con_layer(tf.nn.relu(hidden_layer_3), node_h3, output_shape[1], name="output_layer")

    return output_layer


# Train the neural network using all the settings
def train_neural_network(x, learning_rate, save_dir):
    """
    :param x: tensor for input

    :return: void
    """
    global all_train_summaries
    prediction = neural_network(x)

    with tf.name_scope(name="Cost"):
        cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=output_tensor))
        cost_summary = tf.summary.scalar("cost", cost)
        all_train_summaries.append(cost_summary)

    with tf.name_scope(name="Train"):
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

    with tf.name_scope(name="Train_Accuracy"):
        correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(output_tensor, 1))
        train_accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        train_accuracy_summary = tf.summary.scalar("train_accuracy", train_accuracy)
        all_train_summaries.append(train_accuracy_summary)

    with tf.name_scope(name="Test_Accuracy"):
        correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(output_tensor, 1))
        test_accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        test_accuracy_summary = tf.summary.scalar("test_accuracy", test_accuracy)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        # Set up TensorBoard
        train_summaries = tf.summary.merge(all_train_summaries)
        test_summaries = tf.summary.merge([test_accuracy_summary])
        writer = tf.summary.FileWriter(save_dir)
        writer.add_graph(sess.graph)

        # Set up saving
        saver = tf.train.Saver()

        print("Begin Training...")
        for epoch in range(num_epochs):
            num_steps = int(input_shape[0] / minibatch_size)

            for step in range(num_steps):
                start = step * minibatch_size
                end = (step + 1) * minibatch_size
                batch_x = np.array(train_inputs[start:end])
                batch_y = np.array(train_outputs[start:end])

                if step % 5 == 0:
                    [_, s] = sess.run([train_accuracy, train_summaries], feed_dict={x: batch_x, output_tensor: batch_y})
                    writer.add_summary(s, num_steps * epoch + step)

                sess.run([optimizer, cost], feed_dict={x: batch_x, output_tensor: batch_y})
            out, summary = sess.run([test_accuracy, test_summaries], feed_dict={x: test_inputs, output_tensor:test_outputs})
            writer.add_summary(summary, num_steps * epoch)
            print("Accuracy", out)
            print("Epoch", epoch + 1, "out of", num_epochs, "epochs")

        print("Finished Training...")

        saver.save(sess, join(save_dir, "saved"), global_step=1000)
        writer.close()


def make_hparam_string(nodes_1, nodes_2, nodes_3, learning_rate, mini_batch_size, number_epochs):
    return time.strftime("%Y-%m-%d-%H-%M ") + \
           "LAYERS_%d_%d_%d_LR%f_BS%d_NE%d" % \
           (nodes_1, nodes_2, nodes_3, learning_rate, mini_batch_size, number_epochs)


# Run it!
if __name__ == "__main__":
    name_it = join(LOGDIR, make_hparam_string(node_h1, node_h2, node_h3, learning_rate, minibatch_size, num_epochs))
    train_neural_network(input_tensor, learning_rate, name_it)
