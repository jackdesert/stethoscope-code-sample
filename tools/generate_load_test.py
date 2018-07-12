# This module generates load test data for use by vegeta
# ``NUM_BADGES`` means total of all badges in all houses
# To simulate adding a second house, double NUM_BADGES
# but keep NUM_PIS_PER_HOUSE the same.

from random import randint
import json

class Badge:
    NUM_BADGES = 100
    NUM_PIS_PER_HOUSE = 4
    PAYLOAD_UPDATE_PERIOD_IN_SECONDS = 5
    TARGET_FILE = 'targets.txt'

    def __init__(self, id):
        self.emission_counter = 0
        self.payload_counter = 0

        self.id = id

    def emit(self):
        if self.emission_counter % (self.NUM_PIS_PER_HOUSE * self.PAYLOAD_UPDATE_PERIOD_IN_SECONDS) == 0:
            self.generate_fresh_payload()
        with open(self.TARGET_FILE, 'a') as f:
            f.write('POST https://bip-stethoscope.elitecare.com/rssi_readings\n')
            f.write(f'@{self.payload_filename}\n\n')
        self.emission_counter += 1


    def generate_fresh_payload(self):
        self.payload_filename = f'vegeta_data/badge_{self.id}_payload_{self.payload_counter}.json'
        payload = { 'badge_id': f'badge_{self.id}',
                    'pi_id':    '32',
                    'beacons': { 'beacon_1': self._random_strength(),
                                 'beacon_2': self._random_strength(),
                                 'beacon_3': self._random_strength() }
                  }
        with open(self.payload_filename, 'w') as f:
            f.write(json.dumps(payload))
        self.payload_counter += 1

    def _random_strength(self):
        return randint(-100, -30)




NUM_SECONDS = 60
EMISSIONS_PER_SECOND = Badge.NUM_PIS_PER_HOUSE * Badge.NUM_BADGES
NUM_EMISSIONS = NUM_SECONDS * EMISSIONS_PER_SECOND

# Initialize File
with open(Badge.TARGET_FILE, 'w') as f:
    f.write('')


badges = [Badge(i) for i in range(Badge.NUM_PIS_PER_HOUSE)]

for n in range(NUM_EMISSIONS):
    for badge in badges:
        badge.emit()

denom = Badge.NUM_PIS_PER_HOUSE * Badge.PAYLOAD_UPDATE_PERIOD_IN_SECONDS

print(f'\n{NUM_EMISSIONS} emissions generated in targets.txt')
print(f'  {Badge.NUM_BADGES} badges')
print(f'  {Badge.NUM_PIS_PER_HOUSE} pis')
print(f'  {NUM_SECONDS} seconds\n')
print(f'  1 out of {denom} is unique\n')

print(f'  {EMISSIONS_PER_SECOND} API hits per second')
print(f'  {EMISSIONS_PER_SECOND // denom} database writes per second')

print('Invoke like this:')
print(f'vegeta attack -targets=targets.txt -rate={EMISSIONS_PER_SECOND} -duration={NUM_SECONDS}s | vegeta report')

