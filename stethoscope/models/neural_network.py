# This neural network is modeled after the "Classifying Newswires"
# (Section 3.5) in Francois Chollet's *Deep Learning with Python*

# Invoke:
#    cd path/to/stethoscope
#    env/bin/python stethoscope/models/neural_network.py


import pdb
import numpy as np

from keras import models
from keras import layers

from keras.utils.np_utils import to_categorical

from stethoscope.models.training_run import TrainingRun

class NeuralNetwork:

    def __init__(self, dbsession):
        self.dbsession = dbsession
        self.model = None
        self.history = None
        self.input_shape = None
        self.data_vectorized = None
        self.labels_one_hot = None
        self.history = None

    def train(self):
        self._fetch_data_and_labels()
        self._build_model()
        self._train_model()


    def _fetch_data_and_labels(self):
        # Fetch
        data_vectorized, labels = TrainingRun.data_and_labels(self.dbsession)
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
        model.add(layers.Dense(16, activation='relu', input_shape=input_shape))
        model.add(layers.Dense(16, activation='relu'))
        model.add(layers.Dense(num_rooms, activation='softmax'))

        model.compile(optimizer='rmsprop',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        self.model = model

    def _train_model(self):
        halfway = self.data_vectorized.shape[0] // 2

        train_samples = self.data_vectorized[:halfway]
        validation_samples = self.data_vectorized[halfway:]

        train_labels = self.labels_one_hot[:halfway]
        validation_labels = self.labels_one_hot[halfway:]

        self.history = self.model.fit(train_samples,
                                      train_labels,
                                      epochs=20,
                                      batch_size=512,
                                      validation_data=(validation_samples, validation_labels))


if __name__ == '__main__':


    from pyramid.paster import bootstrap

    with bootstrap('/home/jd/r/stethoscope/development.ini') as env:
        request = env['request']
        request.tm.begin()
        net = NeuralNetwork(request.dbsession)
        net.train()
        a = 5

