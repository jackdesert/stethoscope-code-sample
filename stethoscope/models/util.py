from datetime import datetime
import requests
import redis
import ipdb

def bip_rooms():
    # TODO If these rooms change under foot---what does that do to our keras model?
    uri = 'https://bip.elitecare.com/api/stethoscope/rooms_insecure'
    data = requests.get(uri, timeout=10)
    return data.json()

def bip_rooms_hash():
    return { room_id: room_name for (room_id, room_name) in bip_rooms() }

class PiName:
    NAMES =  {'000000001351facb': 'Larch 2nd Floor (WITH TV)',
              '0000000066c55ea2': 'Tabor 2nd Floor (WITH TV)',
              '0000000088d14482': 'Larch/Tabor 2nd Floor Middle',
              '00000000336e3945': 'Larch/Tabor 3rd Floor Middle',
              '00000000f6ef3162': 'Larch 3rd Floor',
              '00000000accba0fa': 'Tabor 3rd Floor',
              '000000009dc13fc1': 'Tabor 3D (Suite)',
              '000000007f5c3da0': 'Cascade Xerox',
             }

    @classmethod
    def by_id(cls, id):
        return cls.NAMES.get(id) or id


class PiTracker:
    REDIS = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    RECENT_KEY_PREPEND        = 'pi-recent-pi'
    NO_EXPIRATION_KEY_PREPEND = 'pi-no-expiration'

    @classmethod
    def record(cls, pi_id, ip_address):
        ip_address = str(ip_address).ljust(16)
        ansible = f'{ip_address}# {pi_id.ljust(18)}'
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        ansible_with_timestamp = f'{ansible}{now}'
        cls.REDIS.set(f'{cls.RECENT_KEY_PREPEND}:{pi_id}', ansible, ex=60)
        cls.REDIS.set(f'{cls.NO_EXPIRATION_KEY_PREPEND}:{pi_id}', ansible_with_timestamp)

    @classmethod
    def pis(cls, keysOnly=False):
        return cls._pis_by_key_prepend(cls.NO_EXPIRATION_KEY_PREPEND, keysOnly)

    @classmethod
    def active_pis(cls, keysOnly=False):
        return cls._pis_by_key_prepend(cls.RECENT_KEY_PREPEND, keysOnly)


    @classmethod
    def _pis_by_key_prepend(cls, key_prepend, keysOnly):
        keys = set()
        cursor = None
        while cursor != 0:
            if not cursor:
                cursor = 0 # first time through
            cursor, returned_keys = cls.REDIS.scan(cursor, match=f'{key_prepend}*')
            for key in returned_keys:
                keys.add(key)
        if not keys:
            return []
        if keysOnly:
            return keys
        return sorted(cls.REDIS.mget(keys))


class PrudentIterator:
    # This class allows you to check whether there are remaining elements
    # before you actually fetch them
    def __init__(self, elements):
        self._elements = elements
        self._index = 0
        self._max_index = len(elements) - 1

    @property
    def available(self):
        return self._index <= self._max_index

    @property
    def peek(self):
        # View the item without advancing the index
        return self._elements[self._index]

    @property
    def next(self):
        output = self.peek
        self._index += 1
        return output




if __name__ == '__main__':
    for i in range(30):
        PiTracker.write(i)

    pis = PiTracker.active_pis()
    bip_rooms()


