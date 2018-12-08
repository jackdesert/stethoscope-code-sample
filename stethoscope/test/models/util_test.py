import pdb

from stethoscope.test.base_test import BaseTest
from stethoscope.models.util import BiasedScorekeeper



############ TrainingRun Model Tests Written by Jack  #########################

class TestBiasedScorekeeper(BaseTest):

    def test_increment(self):
        sk = BiasedScorekeeper()
        key = 'one'
        sk.increment(key)
        sk.increment(key)

    def test_winner_no_trumped(self):
        sk = BiasedScorekeeper()
        sk.increment('one')
        sk.increment('one')
        sk.increment('two')

        self.assertEqual(sk.winner(), 'one')

    def test_winner_with_only_trumped(self):
        trump_1 = 'few'
        trump_2 = 'weak'
        trumped_keys = {trump_1, trump_2}
        sk = BiasedScorekeeper(trumped_keys)
        sk.increment(trump_1)
        sk.increment(trump_2)
        sk.increment(trump_2)

        self.assertEqual(sk.winner(), trump_2)

    def test_winner_rooms_and_trumped(self):
        room_1  = 'Mansion 5'
        trump_1 = 'silent'
        trump_2 = 'small'
        trumped_keys = {trump_1, trump_2}
        sk = BiasedScorekeeper(trumped_keys)
        sk.increment(trump_1)
        sk.increment(trump_1)
        sk.increment(trump_2)
        sk.increment(trump_2)
        sk.increment(room_1)

        self.assertEqual(sk.winner(), room_1)
