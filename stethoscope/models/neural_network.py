# This neural network is modeled after the "Classifying Newswires"
# (Section 3.5) in Francois Chollet's *Deep Learning with Python*

# Invoke:
#    cd path/to/stethoscope
#
#    # Train model
#    env/bin/python stethoscope/models/neural_network.py
#
#    # Train model and save to disk
#    env/bin/python stethoscope/models/neural_network.py --save
#
#    # Load model and metadata from disk
#    env/bin/python stethoscope/models/neural_network.py --load


import pdb
import numpy as np

from keras import models
from keras import layers

from keras.utils.np_utils import to_categorical

from stethoscope.models.training_run import TrainingRun

class NeuralNetwork:
    MODEL_FILEPATH = 'keras/model.h5'
    METADATA_FILEPATH = 'keras/metadata.pickle'

    def __init__(self, dbsession):
        self.dbsession = dbsession
        self.model = None
        self.history = None
        self.input_shape = None
        self.data_vectorized = None
        self.labels_one_hot = None
        self.history = None
        self.metadata = None

    def train(self, validate):
        self._fetch_data_and_labels()
        self._build_model()
        self._train_model(validate)

    def write_to_disk(self):
        self.model.save(self.MODEL_FILEPATH)
        with open(self.METADATA_FILEPATH, 'wb') as f:
            pickle.dump(self.metadata, f)

    def _fetch_data_and_labels(self):
        # Fetch
        data_vectorized, labels, metadata = TrainingRun.data_and_labels(self.dbsession)
        labels_one_hot = to_categorical(labels)


        # Deduplication
        # TODO There is some chance that two RssiReadings
        #      will have identical badge ids and strengths,
        #      yet will be tagged to different rooms.
        #      Ideal #1: this wouldn't happen ;)
        #      Ideal #2: These would be shuffled before deduplication
        #                so that instead of always removing, say,
        #                the duplicate that belongs in room 2A,
        #                the duplicate that is removed would be
        #                chosen randomly.
        data_vectorized, dedup_index = np.unique(data_vectorized,
                                                 axis=0,
                                                 return_index=True)

        labels_one_hot = labels_one_hot[dedup_index]
        self.metadata = metadata


        # Shuffle two numpy arrays in unison
        # https://stackoverflow.com/questions/4601373/better-way-to-shuffle-two-numpy-arrays-in-unison#answer-37710486
        randomize = np.arange(len(data_vectorized))
        np.random.shuffle(randomize)
        self.data_vectorized = data_vectorized[randomize]
        self.labels_one_hot  = labels_one_hot[randomize]



    def _build_model(self):
        model = models.Sequential()
        input_shape = (self.data_vectorized.shape[-1],) # 5 beacons max per RssiReading
        num_rooms = self.labels_one_hot.shape[-1]
        # TODO What Type of Layers (and how big) are best for this model?
        # TODO Why are we specifying an input shape???
        model.add(layers.Dense(32, activation='relu', input_shape=input_shape))
        model.add(layers.Dense(16, activation='relu'))
        model.add(layers.Dense(num_rooms, activation='softmax'))

        model.compile(optimizer='rmsprop',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        self.model = model

    def _train_model(self, validate):
        num_samples = self.data_vectorized.shape[0]
        if validate:
            num_training_samples = num_samples * 2 // 3
        else:
            num_training_samples = num_samples

        train_samples = self.data_vectorized[:num_training_samples]
        validation_samples = self.data_vectorized[num_training_samples:]

        train_labels = self.labels_one_hot[:num_training_samples]
        validation_labels = self.labels_one_hot[num_training_samples:]

        augmented_samples, augmented_labels = self._augmented(train_samples, train_labels)

        self.history = self.model.fit(augmented_samples,
                                      augmented_labels,
                                      epochs=60,
                                      batch_size=512,
                                      validation_data=(validation_samples, validation_labels))

    def _augmented_single(self, sample):
        # Adjust gain in two ways:
        #  1. Together
        #  2. Separately

        together_scale = 0.1
        separate_scale = 0.05

        together_gain = np.random.normal(loc=1, scale=together_scale)
        new_sample = sample * together_gain

        for index in range(len(sample)):
            separate_gain = np.random.normal(loc=1, scale=separate_scale)
            new_sample[index] *= separate_gain

        return new_sample


    def _augmented(self, samples, labels):

        # multiplier vs average validation accuracy
        # 1          83%
        # 2          86%
        # 4          87%
        # 8          86%
        multiplier = 4

        lsh1, lsh2 = labels.shape
        output_labels_shape = (lsh1 * multiplier, lsh2)
        output_labels = np.zeros(output_labels_shape, dtype=labels.dtype)

        ssh1, ssh2 = samples.shape
        output_samples_shape = (ssh1 * multiplier, ssh2)
        output_samples = np.zeros(output_samples_shape, dtype=samples.dtype)

        output_index = 0
        for input_index in range(len(samples)):
            sample = samples[input_index]
            label  = labels[input_index]
            for i in range(multiplier):
                output_samples[output_index] = self._augmented_single(sample)
                output_labels[output_index] = label
                output_index += 1
        assert(output_index == len(output_samples))
        return output_samples, output_labels



if __name__ == '__main__':


    from pyramid.paster import bootstrap
    import sys
    import pickle

    # Defaults
    train = False
    save  = False
    load  = False

    if len(sys.argv) == 1:
        train = True
    elif sys.argv[1] == '--save':
        train = True
        save  = True
    elif sys.argv[1] == '--load':
        load = True

    if train:
        with bootstrap('development.ini') as env:
            request = env['request']
            request.tm.begin()
            net = NeuralNetwork(request.dbsession)
            net.train(not save)
            if save:
                net.write_to_disk()
                print('\nKeras model and metadata written to disk')
    if load:
        model = models.load_model(NeuralNetwork.MODEL_FILEPATH)
        metadata = pickle.load(open(NeuralNetwork.METADATA_FILEPATH, 'rb'))
        pdb.set_trace()
        a = 5


