#!/usr/bin/env python3

import connexion

from openapi_server import encoder
from openapi_server import mongo


def main():
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'Library Management API'},
                pythonic_params=True)
    mongo.init_indexes()

    app.run(port=8080)


if __name__ == '__main__':
    main()
