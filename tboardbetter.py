import numpy as np
import tensorflow as tf
import pickle

# Import Data
print("Loading data...")
data = pickle.load(open("./skills_to_industry.pickle", "rb"))
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
input_size = np.shape(train_inputs)
output_size = np.shape(train_outputs)
LOGDIR = "./demo2/"

# Learning
batch_size = 300
learning_rate = 0.001
num_epochs = 100

# Tensorflow placeholders for inputs and outputs
x = tf.placeholder(tf.float32, shape=[None, input_size[1]], name="x")
y = tf.placeholder(tf.float32, shape=[None, output_size[1]], name="labels")


def full_con_layer(input_data, size_in, size_out, name="fc"):
    with tf.name_scope(name):
        w = tf.Variable(tf.random_normal([size_in, size_out]), name="W")
        b = tf.Variable(tf.random_normal([size_out]), name="b")
        activation = tf.add(tf.matmul(input_data, w), b)
        tf.summary.histogram("weights", w)
        tf.summary.histogram("biases", b)
        tf.summary.histogram("activations", activation)
        return activation


def neural_network(data):
    """
    Sets up structure and model of nn
    :param data: followed tutorials.... Unused???
    :return: output activation
    """
    hidden_layer_1 = full_con_layer(x, input_size[1], node_h1, name="hidden_layer_1")
    hidden_layer_2 = full_con_layer(tf.nn.relu(hidden_layer_1), node_h1, node_h2, name="hidden_layer_2")
    hidden_layer_3 = full_con_layer(tf.nn.relu(hidden_layer_2), node_h2, node_h3, name="hidden_layer_3")
    output_layer = full_con_layer(tf.nn.relu(hidden_layer_3), node_h3, output_size[1], name="output_layer")

    return output_layer

# Train the neural network using all the settings


def train_neural_network(x, learning_rate, hparam):
    """
    :param x: tensor for input

    :return: void
    """
    prediction = neural_network(x)

    with tf.name_scope(name="Cost"):
        cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=y))
        tf.summary.scalar("cost", cost)

    with tf.name_scope(name="Train"):
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

    with tf.name_scope(name="Accuracy"):
        correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        test_x = test_inputs
        test_y = test_outputs
        tf.summary.scalar("accuracy", accuracy)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        # Setup TensorBoard
        merged_summary = tf.summary.merge_all()
        writer = tf.summary.FileWriter(LOGDIR + hparam)
        writer.add_graph(sess.graph)

        print("Begin Training...")
        for epoch in range(num_epochs):
            # print("Epoch", epoch + 1, "started.")
            for iteration in range(int(input_size[0]/batch_size)):
                start = iteration * batch_size
                end = (iteration + 1) * batch_size
                batch_x = np.array(train_inputs[start:end])
                batch_y = np.array(train_outputs[start:end])

                if iteration % 5 == 0:
                    [train_accuracy, s] = sess.run([accuracy, merged_summary], feed_dict={x: batch_x, y: batch_y})
                    writer.add_summary(s, int(input_size[0]/batch_size)*epoch + iteration)

                sess.run([optimizer, cost], feed_dict={x: batch_x, y: batch_y})
            print("Epoch", epoch + 1, "out of", num_epochs, "epochs")

        print("Finished Training...")

        writer.close()


def make_hparam_string(nodes_1, nodes_2, nodes_3, learning_rate, mini_batch_size, number_epochs):
    return "HL1%d_HL2%d_HL3%d_LR%f_BS%d_NE%d" % (nodes_1, nodes_2, nodes_3, learning_rate, mini_batch_size, number_epochs)


# Run it!
name_it = make_hparam_string(node_h1, node_h2, node_h3, learning_rate, batch_size, num_epochs)
train_neural_network(x, learning_rate, name_it)
