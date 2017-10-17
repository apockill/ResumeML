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


# Hack to make it work better maybe? (because our output works best with two output neurons)
# print(""""Fixing" Labels...""")
# for i in range(np.shape(test_outputs)[0]):
#     if test_outputs[i] == [0]:
#         test_outputs_temp = np.append(test_outputs_temp, [[0, 1]], axis=0)
#
#     else:
#         test_outputs_temp = np.append(test_outputs_temp, [[1, 0]], axis=0)
#         print("Hey")
#
# for i in range(np.shape(train_outputs)[0]):
#     if train_outputs[i] == [0]:
#         train_outputs_temp = np.append(train_outputs_temp, [[0, 1]], axis=0)
#
#     else:
#         train_outputs_temp = np.append(train_outputs_temp, [[1, 0]], axis=0)


# Setup characteristics of network:
# Shape
node_h1 = 100
node_h2 = 100
node_h3 = 100
input_size = np.shape(train_inputs)
output_size = np.shape(train_outputs)

# Learning
batch_size = 300
learning_rate = 0.01
num_epochs = 1000

# Tensorflow placeholders for inputs and outputs
x = tf.placeholder(tf.float32, shape=[None, input_size[1]], name="x")
y = tf.placeholder(tf.float32, shape=[None, output_size[1]], name="y")

# Setup structure of network using tf


def neural_network_model(data):
    """
    Sets up structure and model of nn
    :param data: followed tutorials.... Unused???
    :return: output activation
    """
    hidden_layer_1 = {'weights': tf.Variable(tf.random_normal([input_size[1], node_h1])),
                      'biases': tf.Variable(tf.random_normal([node_h1]))}

    hidden_layer_2 = {'weights': tf.Variable(tf.random_normal([node_h1, node_h2])),
                      'biases': tf.Variable(tf.random_normal([node_h2]))}

    hidden_layer_3 = {'weights': tf.Variable(tf.random_normal([node_h2, node_h3])),
                      'biases': tf.Variable(tf.random_normal([node_h3]))}

    output_layer = {'weights': tf.Variable(tf.random_normal([node_h3, output_size[1]])),
                    'biases': tf.Variable(tf.random_normal([output_size[1]]))}
    l1 = tf.add(tf.matmul(data, hidden_layer_1['weights']), hidden_layer_1['biases'])
    l1 = tf.nn.relu(l1)

    l2 = tf.add(tf.matmul(l1, hidden_layer_2['weights']), hidden_layer_2['biases'])
    l2 = tf.nn.relu(l2)

    l3 = tf.add(tf.matmul(l2, hidden_layer_3['weights']), hidden_layer_3['biases'])
    l3 = tf.nn.relu(l3)

    output = tf.add(tf.matmul(l3, output_layer['weights']), output_layer['biases'])

    return output

# Train the neural network using all the settings


def train_neural_network(x):
    """
    :param x: tensor for input
    :return: void
    """
    prediction = neural_network_model(x)
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=y))
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        print("Begin Training...")
        for epoch in range(num_epochs):
            epoch_loss = 0
            # print("Epoch", epoch + 1, "started.")
            for iteration in range(int(input_size[0]/batch_size)):
                start = iteration * batch_size
                end = (iteration + 1) * batch_size
                batch_x = np.array(train_inputs[start:end])
                batch_y = np.array(train_outputs[start:end])
                _, c = sess.run([optimizer, cost], feed_dict={x: batch_x, y: batch_y})
                epoch_loss += c
            print("Epoch", epoch + 1, " completed out of", num_epochs, ". Loss: ", epoch_loss)

            correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
            accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
            test_x = test_inputs
            test_y = test_outputs
            print("Accuracy: ", accuracy.eval({x: test_x, y: test_y}))

        print("Finished Training...")


# Run it!
train_neural_network(x)
