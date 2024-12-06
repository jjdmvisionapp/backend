import pytest
from flask import session


# Helper function to send registration requests
def register_user(client, url, email, username, password):
    return client.post(url, data={"email": email, "username": username, "password": password})

# Helper function to send login requests
def login_user(client, url, email, username, password):
    return client.post(url, data={"email": email, "username": username, "password": password})

# Helper function to perform a @me request
def get_me(client, url):
    return client.get(url)

def test_new_registration(client, app, endpoint, port):
    url = f"http://localhost:{port}{endpoint}user/register"
    with app.app_context():
        response = register_user(client, url, "test@test.com", "username", "testpassword")
        assert response.status_code == 200
        assert response.json.get("status") == "success"

def test_existing_registration(client, app, endpoint, port):
    url = f"http://localhost:{port}{endpoint}user/register"
    with app.app_context():
        # First, register the user
        register_user(client, url, "test@test.com", "username", "testpassword")

        # Now try registering the same user
        response = register_user(client, url, "test@test.com", "username", "testpassword")

        # Check if the response code is an error (400 for bad request)
        assert response.status_code == 400
        assert response.json.get("status") == "error"
        assert response.json.get("message") == "Invalid data provided"

def test_invalid_registration(client, app, endpoint, port):
    url = f"http://localhost:{port}{endpoint}user/register"
    with app.app_context():
        # Invalid email
        response = register_user(client, url, "test @abcdefb", "username", "testpassword")
        # Check if the response code is an error (400 for bad request)
        assert response.status_code == 400
        assert response.json.get("status") == "error"
        assert response.json.get("message") == "Invalid data provided"

        # No password
        response = register_user(client, url, "test@test.com", "username", "")
        # Check if the response code is an error (400 for bad request)
        assert response.status_code == 400
        assert response.json.get("status") == "error"
        assert response.json.get("message") == "Invalid data provided"

        # No username
        response = register_user(client, url, "test@test.com", "", "testpassword")
        # Check if the response code is an error (400 for bad request)
        assert response.status_code == 400
        assert response.json.get("status") == "error"
        assert response.json.get("message") == "Invalid data provided"

def test_existing_login(client, app, endpoint, port):
    url = f"http://localhost:{port}{endpoint}user/login"
    with app.app_context():
        response = login_user(client, url, "test@test.com", "username", "testpassword")
        assert response.status_code == 200
        assert response.json.get("status") == "success"

def test_invalid_login(client, app, endpoint, port):
    url = f"http://localhost:{port}{endpoint}user/login"
    with app.app_context():
        # Incorrect password
        response = login_user(client, url, "test@test.com", "username", "testpassword1235")
        # Check if the response code is an error (400 for bad request)
        assert response.status_code == 400
        assert response.json.get("status") == "error"
        assert response.json.get("message") == "Invalid data provided"

        # Incorrect username
        response = login_user(client, url, "test@test.com", "username2", "testpassword")
        # Check if the response code is an error (400 for bad request)
        assert response.status_code == 400
        assert response.json.get("status") == "error"
        assert response.json.get("message") == "Invalid data provided"

        # Incorrect email
        response = login_user(client, url, "test2@test.com", "username2", "testpassword")
        # Check if the response code is an error (400 for bad request)
        assert response.status_code == 400
        assert response.json.get("status") == "error"
        assert response.json.get("message") == "Invalid data provided"


def test_session(client, app, endpoint, port):
    login_url = f"http://localhost:{port}{endpoint}user/login"


    with app.test_client() as test_client:
        with app.app_context():
            # Perform login request
            login_response = login_user(test_client, login_url, "test@test.com", "username", "testpassword")

            # Assert login is successful
            assert login_response.status_code == 200
            assert login_response.json.get("status") == "success"

            # Manually set session cookie in the test client (if needed)
            with test_client.session_transaction() as session:
                session["USER_ID"] = login_response.json["session"]["id"]

            # Make the @me request
            me_url = f"http://localhost:{port}{endpoint}user/@me"
            me_response = get_me(test_client, me_url)

            # Assert the response is successful
            assert me_response.status_code == 200
            assert me_response.json.get("status") == "success"

            # Verify user ID
            assert me_response.json.get("user")["id"] == login_response.json["session"]["id"]



def test_update_user_info(client, app, endpoint, port):
    # First, register a new user and log them in
    with app.app_context():
        login_url = f"http://localhost:{port}{endpoint}user/login"

        # Login as user 1
        login_response = login_user(client, login_url, "test@test.com", "username", "testpassword")
        assert login_response.status_code == 200
        assert login_response.json.get("status") == "success"

        # Perform update as user 1
        update_url = f"http://localhost:{port}{endpoint}user/update"
        update_data = {"user_username": "josh"}

        update_response = client.post(update_url, data=update_data)

        assert update_response.status_code == 200
        assert update_response.json.get("status") == "success"
        assert update_response.json.get("message") == "Info update successful"


