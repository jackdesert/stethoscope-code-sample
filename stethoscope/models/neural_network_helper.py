from ..models.neural_network import NeuralNetwork
import numpy as np
import pickle
import ipdb

class DisjointBeaconsError(Exception):
    '''
        If the beacons present in this RssiReading are disjoint from
        the beacons that were used to train the keras model,
        `vectorize_and_normalize_reading` would return a
        numpy array of zeros. Instead, we raise this error.

        Make sure the only beacons active in your house are the ones
        used during keras model training. Otherwise your accuracy will suffer.
    '''
    # TODO alert engineers when /:badge_id/location is called that uses
    # an RssiReading containing any beacons that were not present during training
    @property
    def __name__(self):
        return 'DisjointBeaconsError'

class NoBeaconsError(Exception):
    '''
        If there are no beacons in the RssiReading
    '''
    @property
    def __name__(self):
        return 'NoBeaconsError'


class NeuralNetworkHelper:
    @classmethod
    def vectorize_and_normalize_reading(cls, rssi_reading, metadata=None):
        # For bulk usage, pass in `metadata` so it need not be read from disk each time
        if not metadata:
            with open(NeuralNetwork.METADATA_FILEPATH, 'rb') as f:
                metadata = pickle.load(f)


        beacons_present = False
        imposter_beacons = set()
        bmap = metadata.beacon_id_to_beacon_index
        output = np.zeros(len(bmap))
        for number in range(1, 6):
            beacon_id = getattr(rssi_reading, f'beacon_{number}_id')
            beacon_strength = getattr(rssi_reading, f'beacon_{number}_strength')
            if beacon_id:
                beacons_present = True
                if beacon_id in metadata.beacon_id_to_beacon_index:
                    beacon_index = metadata.beacon_id_to_beacon_index[beacon_id]
                    output[beacon_index] = beacon_strength - metadata.min_strength
                else:
                    imposter_beacons.add(beacon_id)

        if not beacons_present:
            raise NoBeaconsError('No beacons present in RssiReading')

        if np.unique(output).shape == (1,):
            msg = f'No Matching Beacons in RssiReading with id {rssi_reading.id} and beacons {rssi_reading.beacons}. This means that beacons used for training and beacons in this reading are disjoint.'
            raise DisjointBeaconsError(msg)

        output /= metadata.strength_range

        return output, imposter_beacons

