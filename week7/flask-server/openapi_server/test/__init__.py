import logging
import os

import connexion
from flask_testing import TestCase

from openapi_server.encoder import JSONEncoder
from openapi_server import mongo


class BaseTestCase(TestCase):

    def create_app(self):
        os.environ["USE_MONGOMOCK"] = "1"
        mongo.reset_connection()
        logging.getLogger('connexion.operation').setLevel('ERROR')
        app = connexion.App(__name__, specification_dir='../openapi/')
        app.app.json_encoder = JSONEncoder
        app.add_api('openapi.yaml', pythonic_params=True)
        mongo.init_indexes()
        return app.app

    def tearDown(self):
        mongo.reset_connection()
        super().tearDown()
