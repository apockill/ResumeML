from os.path import join
import time

import numpy as np
import tensorflow as tf
import pickle

all_train_summaries = []


def full_con_layer(input_data, size_in, size_out, name):
    with tf.name_scope(name):
        w = tf.Variable(tf.random_normal([size_in, size_out]), name="W")
        b = tf.Variable(tf.random_normal([size_out]), name="b")
        activation = tf.add(tf.matmul(input_data, w), b, name="activation")

        # Make summaries for this layer
        global all_train_summaries
        train_weights_summary = tf.summary.histogram("weights", w)
        train_biases_summary = tf.summary.histogram("biases", b)
        train_activations_summary = tf.summary.histogram("activations", activation)
        layer_summaries = [train_weights_summary, train_biases_summary, train_activations_summary]
        all_train_summaries += layer_summaries

        return activation


def neural_network(x):
    """
    Sets up structure and model of nn
    :param data: followed tutorials.... Unused???
    :return: output activation
    """

    hidden_layer_1 = full_con_layer(x, input_shape[1], node_h1, name="hidden_layer_1")
    hidden_layer_2 = full_con_layer(tf.nn.relu(hidden_layer_1), node_h1, node_h2, name="hidden_layer_2")
    hidden_layer_3 = full_con_layer(tf.nn.relu(hidden_layer_2), node_h2, node_h3, name="hidden_layer_3")
    # hidden_layer_4 = full_con_layer(tf.nn.relu(hidden_layer_3), node_h3, node_h4, name="hidden_layer_3")
    output_layer = full_con_layer(tf.nn.relu(hidden_layer_3), node_h3, output_shape[1], name="output_layer")
    return output_layer


# Train the neural network using all the settings
def train_neural_network():
    """
    :param x: tensor for input

    :return: void
    """
    global all_train_summaries

    # Build network
    x = tf.placeholder(tf.float32, shape=[None, input_shape[1]], name="x")
    y = tf.placeholder(tf.float32, shape=[None, output_shape[1]], name="labels")
    prediction = neural_network(x)

    save_dir = join(LOGDIR, make_hparam_string(input_shape[1], output_shape[1],
                    node_h1, node_h2, node_h3, learning_rate, minibatch_size, num_epochs))

    with tf.name_scope(name="Cost"):
        cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=y))
        cost_summary = tf.summary.scalar("cost", cost)
        all_train_summaries.append(cost_summary)

    with tf.name_scope(name="Train"):
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

    with tf.name_scope(name="Train_Accuracy"):
        correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
        train_accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        train_accuracy_summary = tf.summary.scalar("train_accuracy", train_accuracy)
        all_train_summaries.append(train_accuracy_summary)

    with tf.name_scope(name="Test_Accuracy"):
        correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
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
        # Every time the network beats its record, save it to file
        best_accuracy_so_far = 0
        for epoch in range(num_epochs):
            num_steps = int(input_shape[0] / minibatch_size)

            for step in range(num_steps):
                start = step * minibatch_size
                end = (step + 1) * minibatch_size
                batch_x = np.array(train_inputs[start:end])
                batch_y = np.array(train_outputs[start:end])

                if step % 100 == 0:
                    [_, s] = sess.run([train_accuracy, train_summaries], feed_dict={x: batch_x, y: batch_y})
                    writer.add_summary(s, num_steps * epoch + step)

                sess.run([optimizer, cost], feed_dict={x: batch_x, y: batch_y})

            if epoch % 5 == 0:
                accuracy, summary = sess.run([test_accuracy, test_summaries], feed_dict={x: test_inputs, y:test_outputs})
                writer.add_summary(summary, num_steps * epoch)

                # Save model if it broke it's previous record
                if accuracy > best_accuracy_so_far:
                    best_accuracy_so_far = accuracy
                    print("Saving new record: ", accuracy)
                    saver.save(sess, join(save_dir, "saved"), global_step=0)
                print(accuracy)
            print("Epoch", epoch + 1, "out of", num_epochs, "epochs")

        print("Finished Training...")
        writer.close()


def make_hparam_string(num_features, num_labels, nodes_1, nodes_2, nodes_3, learning_rate, mini_batch_size, number_epochs):
    return time.strftime("%Y-%m-%d-%H-%M ") + \
           "FEATURES%d_LABELS%d_LAYERS_%d_%d_%d_LR%f_BS%d_NE%d" % \
           (num_features, num_labels, nodes_1, nodes_2, nodes_3, learning_rate, mini_batch_size, number_epochs)


# Run it!
if __name__ == "__main__":
    # Import Data
    LOGDIR = "..\\test_dir\\dataset_4\\"

    print("Loading data...")
    data = pickle.load(open(LOGDIR + "\\FROM_skills_TO_industry_MININPUTSPER_6_INPUTSAMPLES_125_OUTPUTSAMPLES_3500.pickle", "rb"))
    print("in: ", len(data["inputs"]),
          "out: ", len(data["outputs"]),
          "in lex", len(data["input_lexicon"]),
          "out lex", len(data["output_lexicon"]))


    # Prep the data
    num_tests = 10000  # Number of test examples
    train_inputs = data["inputs"][:-num_tests]
    train_outputs = data["outputs"][:-num_tests]
    test_inputs = data["inputs"][-num_tests:]
    test_outputs = data["outputs"][-num_tests:]

    # Setup characteristics of network:
    node_h1 = 4000
    node_h2 = 4000
    node_h3 = 4000
    # node_h4 = 3500
    input_shape = np.shape(train_inputs)
    output_shape = np.shape(train_outputs)

    # Learning
    minibatch_size = 1000
    learning_rate = 0.001
    num_epochs = 1000

    train_neural_network()


