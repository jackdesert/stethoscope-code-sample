

from collections import defaultdict
from pyramid.paster import bootstrap
from stethoscope.models import RssiReading
from stethoscope.models import TrainingRun
from stethoscope.models.neural_network import NeuralNetwork
from stethoscope.models.neural_network_helper import NeuralNetworkHelper
import pickle
import json
import numpy
import pdb
import sys

def grouped_readings():
    with bootstrap('development.ini') as env:
        request = env['request']
        request.tm.begin()
        dbsession = request.dbsession

        data = defaultdict(dict)
        for trun in dbsession.query(TrainingRun):
            room_id = trun.room_id
            # initialize dict
            data[room_id]
            for reading in trun.rssi_readings(dbsession, True):
                for bid, strength in reading.beacons:
                    if not bid in data[room_id]:
                        data[room_id][bid] = dict(strengths=[])
                    data[room_id][bid]['strengths'].append(strength)

        output = defaultdict(list)
        for room_id, beacon_data in data.items():
            for bid, raw_data in beacon_data.items():
                strengths = raw_data['strengths']
                mean = numpy.mean(strengths)
                raw_data['mean'] = mean
                raw_data['count'] = len(strengths)
                output[room_id].append((bid, mean))

        for room_id, means in output.items():
            means.sort(key=lambda x: -x[1])





def mean_values(argv=None):
    with bootstrap('development.ini') as env:
        request = env['request']
        request.tm.begin()
        dbsession = request.dbsession

        data = defaultdict(dict)
        for trun in dbsession.query(TrainingRun):
            room_id = trun.room_id
            # initialize dict
            data[room_id]
            for reading in trun.rssi_readings(dbsession, True):
                for bid, strength in reading.beacons:
                    if not bid in data[room_id]:
                        data[room_id][bid] = dict(strengths=[])
                    data[room_id][bid]['strengths'].append(strength)

        output = defaultdict(list)
        for room_id, beacon_data in data.items():
            for bid, raw_data in beacon_data.items():
                strengths = raw_data['strengths']
                mean = numpy.mean(strengths)
                raw_data['mean'] = mean
                raw_data['count'] = len(strengths)
                output[room_id].append((bid, mean))

        for room_id, means in output.items():
            means.sort(key=lambda x: -x[1])


        print(json.dumps(output))


def vectorized_readings():
    with bootstrap('development.ini') as env:
        request = env['request']
        request.tm.begin()
        dbsession = request.dbsession

        with open(NeuralNetwork.METADATA_FILEPATH, 'rb') as f:
            metadata = pickle.load(f)


        truns = defaultdict(list)
        for trun in dbsession.query(TrainingRun):
            room_id = trun.room_id
            for reading in trun.rssi_readings(dbsession, True):
                vectorized = NeuralNetworkHelper.vectorize_and_normalize_reading(reading,
                                                                                 metadata)
                truns[room_id].append(vectorized[0])


        print(json.dumps(truns))





if __name__ == "__main__":
    sys.exit(vectorized_readings())















