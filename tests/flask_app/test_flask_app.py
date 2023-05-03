import pytest
from flask_app import app as main_app


@pytest.fixture()
def app():
    main_app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield main_app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_request_index(client):
    response = client.get("/")
    assert response.status_code == 200


def test_request_interpret(client):

    response = client.post("/interpret", follow_redirects=True, data={
        "source": "x = 1;"
    })

    assert response.status_code == 200

    # Check that there was one redirect response.
    assert len(response.history) == 1

    # Check that the second request was to the index page.
    assert response.request.path == "/"

