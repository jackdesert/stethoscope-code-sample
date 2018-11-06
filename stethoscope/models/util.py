from datetime import datetime
import requests
import redis
import pdb

def bip_rooms():
    # TODO If these rooms change under foot---what does that do to our keras model?
    uri = 'https://bip.elitecare.com/api/stethoscope/rooms_insecure'
    data = requests.get(uri, timeout=10)
    return data.json()

def bip_rooms_hash():
    return { room_id: room_name for (room_id, room_name) in bip_rooms() }

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





if __name__ == '__main__':
    for i in range(30):
        PiTracker.write(i)

    pis = PiTracker.active_pis()
    bip_rooms()


