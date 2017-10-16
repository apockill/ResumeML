import pickle

import tensorflow as tf
import numpy as np


def neural_network_model(input_layer, len_inputs, n_classes):
    n_nodes_hl1 = 100
    n_nodes_hl2 = 50
    n_nodes_hl3 = 10

    n_classes = n_classes  # Positive or Negative

    hidden_1_layer = {'weights': tf.Variable(tf.random_normal([len_inputs, n_nodes_hl1])),
                      'biases': tf.Variable(tf.random_normal([n_nodes_hl1]))}

    hidden_2_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
                      'biases': tf.Variable(tf.random_normal([n_nodes_hl2]))}

    hidden_3_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_hl3])),
                      'biases': tf.Variable(tf.random_normal([n_nodes_hl3]))}

    output_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl3, n_classes])),
                    'biases': tf.Variable(tf.random_normal([n_classes])), }

    l1 = tf.add(tf.matmul(input_layer, hidden_1_layer['weights']), hidden_1_layer['biases'])
    l1 = tf.nn.relu(l1)

    l2 = tf.add(tf.matmul(l1, hidden_2_layer['weights']), hidden_2_layer['biases'])
    l2 = tf.nn.relu(l2)

    l3 = tf.add(tf.matmul(l2, hidden_3_layer['weights']), hidden_3_layer['biases'])
    l3 = tf.nn.relu(l3)

    output = tf.matmul(l3, output_layer['weights']) + output_layer['biases']

    return output


def train_neural_network(train_inputs, train_outputs, test_inputs, test_outputs, batch_size):
    """
    :param inputs: An array of hot encoded arrays
    :param outputs: An array of one-hot encoded arrays
    :return:
    """

    print("Starting Session")
    input_layer = tf.placeholder('float', [None, len(train_inputs[0])])
    output = tf.placeholder('float')

    prediction = neural_network_model(input_layer, len(train_inputs[0]), len(train_outputs[0]))
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=output))

    optimizer = tf.train.AdamOptimizer().minimize(cost)

    hm_epochs = 10
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        print("Beginning Training")
        for epoch in range(hm_epochs):
            epoch_loss = 0


            i = 0
            while i < len(train_inputs):
                start = i
                end   = i + batch_size
                batch_x = np.array(train_inputs[start:end])
                batch_y = np.array(train_outputs[start:end])

                _, c = sess.run([optimizer, cost], feed_dict={input_layer: batch_x, output: batch_y})
                epoch_loss += c
                print(c)

                i += batch_size

            print('Epoch', epoch, 'completed out of', hm_epochs, 'loss:', epoch_loss)

        correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(output, 1))

        accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        print('Accuracy:', accuracy.eval({input_layer:test_inputs,  output: test_outputs}))



if __name__ == "__main__":
    print("Getting training and testing data")
    # train_x, train_y, test_x, test_y = create_feature_sets_and_labels('Positive.txt', 'Negative.txt')
    data = pickle.load(open("../skills_to_google.pickle", "rb"))

    num_tests = 100
    train_inputs = data["inputs"][:-num_tests]
    train_outputs = data["outputs"][:-num_tests]
    test_inputs = data["inputs"][-num_tests:]
    test_outputs = data["outputs"][-num_tests:]

    train_neural_network(train_inputs, train_outputs, test_inputs, test_outputs, batch_size=100)