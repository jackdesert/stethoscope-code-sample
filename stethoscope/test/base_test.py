from pyramid import testing
import pdb
import transaction
import unittest

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('stethoscope.models')
        settings = self.config.get_settings()

        from stethoscope.models import (
            get_engine,
            get_session_factory,
            get_tm_session,
            )

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)

        self.session = get_tm_session(session_factory, transaction.manager)

    def init_database(self):
        from stethoscope.models.meta import Base
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        from stethoscope.models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)

