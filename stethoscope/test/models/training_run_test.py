from pyramid import testing

import datetime
import ipdb
import transaction
import unittest

from stethoscope.test.base_test import BaseTest



############ TrainingRun Model Tests Written by Jack  #########################

class TestTrainingRun(BaseTest):


    def validTrainingRun(self):
        from stethoscope.models.training_run import TrainingRun

        training_run = TrainingRun(room_id='a',
                                   badge_id='b')
        return training_run


    def test_happy_path(self):
        run = self.validTrainingRun()
        self.assertTrue(run.valid)

    def test_fails_del_no_badge_id(self):
        run = self.validTrainingRun()
        run.badge_id = None
        self.assertFalse(run.valid)
        self.assertTrue(run.invalid)

    def test_fails_del_no_room_id(self):
        run = self.validTrainingRun()
        run.room_id = None
        self.assertFalse(run.valid)
        self.assertTrue(run.invalid)


