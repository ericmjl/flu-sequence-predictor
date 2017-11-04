from collections import Counter
from copy import deepcopy

import numpy as np
from sklearn.preprocessing import LabelBinarizer

from keras.models import model_from_yaml


def right_pad(sequences):
    """
    Pads sequences with extra "*" characters.
    """
    padded_sequences = deepcopy(sequences)
    seq_lengths = compute_seq_lengths(sequences)

    for s in padded_sequences:
        while len(s) < max(seq_lengths.keys()):
            s.seq += '*'
    return padded_sequences


def compute_seq_lengths(sequences):
    """
    Computes the sequence lengths.
    """
    seq_lengths = [len(s) for s in sequences]
    seq_lengths = Counter(seq_lengths)
    return seq_lengths


def seq2chararray(sequences):
    """
    Returns sequences coded as a numpy array. Doesn't perform one-hot-encoding.
    """
    padded_sequences = right_pad(sequences)
    seq_lengths = compute_seq_lengths(sequences)
    char_array = np.chararray(shape=(len(sequences), max(seq_lengths.keys())),
                              unicode=True)
    for i, seq in enumerate(padded_sequences):
        char_array[i, :] = list(seq)
    return char_array


def compute_alphabet(sequences):
    """
    Returns the alphabet used in a set of sequences.
    """
    alphabet = set()
    for s in sequences:
        alphabet = alphabet.union(set(s))

    return alphabet


def encode_array(sequences):
    """
    Performs binary encoding of the sequence array.

    Inputs:
    =======
    - seq_array: (numpy array) of characters.
    - seq_lengths: (Counter) dictionary; key::sequence length; value::number of
                   sequences with that length.
    """
    # Binarize the features to one-of-K encoding.
    alphabet = compute_alphabet(sequences)
    seq_lengths = compute_seq_lengths(sequences)
    seq_array = seq2chararray(sequences)
    lb = LabelBinarizer()
    lb.fit(list(alphabet))
    print(len(alphabet))

    encoded_array = np.zeros(shape=(seq_array.shape[0],
                                    max(seq_lengths.keys()) * len(alphabet)))

    for i in range(seq_array.shape[1]):
        encoded_array[:, i*len(alphabet):(i+1)*len(alphabet)] = \
            lb.transform(seq_array[:, i])

    return encoded_array


def embedding2binary(decoder, predictions):
    """
    Decodes the predictions into a binary array.

    Inputs:
    =======
    - decoder: a Keras model.
    - predictions: a numpy array corresponding to the lower dimensional
                   projection.

    Returns:
    ========
    - a binary encoding numpy array that corresponds to a predicted sequence.
    """
    return np.rint(decoder.predict(predictions))


def binary2chararray(sequences, binary_array):
    """
    Converts a binary array into a character array.
    """

    alphabet = compute_alphabet(sequences)
    seq_lengths = compute_seq_lengths(sequences)
    seq_array = seq2chararray(sequences)

    lb = LabelBinarizer()
    lb.fit(list(alphabet))

    char_array = np.chararray(shape=(len(binary_array),
                              max(seq_lengths.keys())), unicode=True)

    for i in range(seq_array.shape[1]):
        char_array[:, i] = lb.inverse_transform(
            binary_array[:, i*len(alphabet):(i+1)*len(alphabet)])

    return char_array


def save_model(model, path):
    with open(path + '.yaml', 'w+') as f:
        model_yaml = model.to_yaml()
        f.write(model_yaml)

    model.save_weights(path + '.h5')


def load_model(path):
    with open(path + '.yaml', 'r+') as f:
        yaml_rep = ''
        for l in f.readlines():
            yaml_rep += l

    model = model_from_yaml(yaml_rep)
    model.load_weights(path + '.h5')

    return model


def get_density_interval(percentage, array, axis=0):
    """
    Returns the highest density interval on the array.

    Parameters:
    ===========
    percentage: (float, int) value between 0 and 100, inclusive.
    array: a numpy array of numbers.
    """
    low = (100 - percentage) / 2
    high = (100 - low)

    lowp, highp = np.percentile(array, [low, high], axis=axis)

    return lowp, highp
