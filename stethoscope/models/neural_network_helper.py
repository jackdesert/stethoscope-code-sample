from ..models.neural_network import NeuralNetwork
import numpy as np
import pickle
import pdb

class NeuralNetworkHelper:
    @classmethod
    def vectorize_and_normalize_reading(cls, rssi_reading, metadata=None):
        if not metadata:
            with open(NeuralNetwork.METADATA_FILEPATH, 'rb') as f:
                # TODO Load this once in the controller so it does not have to read from disk
                # during each http request
                metadata = pickle.load(f)


        bmap = metadata.beacon_id_to_beacon_index
        output = np.zeros(len(bmap))
        for number in range(1, 6):
            beacon_id = getattr(rssi_reading, f'beacon_{number}_id')
            beacon_strength = getattr(rssi_reading, f'beacon_{number}_strength')
            if beacon_id:
                beacon_index = metadata.beacon_id_to_beacon_index[beacon_id]
                output[beacon_index] = beacon_strength - metadata.min_strength

        output /= metadata.strength_range

        return output

