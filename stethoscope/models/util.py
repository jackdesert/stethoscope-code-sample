import requests
import redis
import pdb

def bip_rooms():
    # TODO If these rooms change under foot---what does that do to our keras model?
    uri = 'https://bip.elitecare.com/api/stethoscope/rooms_insecure'
    data = requests.get(uri, timeout=10)
    return data.json()

class PiTracker:
    REDIS = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    KEY_PREPEND = 'active_pi'

    @classmethod
    def record(cls, pi_id):
        cls.REDIS.set(f'{cls.KEY_PREPEND}:{pi_id}', pi_id, ex=60)

    @classmethod
    def active_pis(cls):
        keys = set()
        cursor = None
        while cursor != 0:
            if not cursor:
                cursor = 0 # first time through
            cursor, returned_keys = cls.REDIS.scan(cursor, match=f'{cls.KEY_PREPEND}*')
            for key in returned_keys:
                keys.add(key)
        if not keys:
            return []
        return cls.REDIS.mget(keys)





if __name__ == '__main__':
    for i in range(30):
        PiTracker.write(i)

    pis = PiTracker.active_pis()
    bip_rooms()


