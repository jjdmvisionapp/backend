import os

import pytest
from flask import Flask

from jjdmvision import create_app


@pytest.fixture()
def app():
    flask_app = create_app()
    yield flask_app


@pytest.fixture()
def client(app: Flask):
    return app.test_client()


@pytest.fixture()
def endpoint(app: Flask):
    return app.config["ENDPOINT"]


@pytest.fixture()
def port(app: Flask):
    return app.config["PORT"]


