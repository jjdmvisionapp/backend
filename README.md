Backend for the project, contact Josh if you have any issues.

Run `jjdmvision.py` to start the server.
# Required Packages:
- email_validator
- flask
- flask-session
- pytest
- flask-socketio 
- eventlet
- torch
- torchvision
- pillow
- requests

*It is advised to use Python 3.12 for the minute to prevent issues with packages.*

You should be able to use the Pipfile to get these all installed easily:
1. Install pipenv using `pip install pipenv` (on Python 3.12.7, it's installed but does not work unless you re-install it for some reason sometimes)
2. Then, in this directory, run `pipenv install`
3. And finally, do `pipenv run python jjdmvision.py`

## Testing
*optional*

`pipenv run pytest` should do the trick, hopefully they all pass! Only testing user routes at the minute.

## Routes

*Here is what a route could return generically upon an error*:

HTTP 400 Bad Request

```json
{
  "status": "error",
  "message": "Invalid data provided"
}
```
or

HTTP 500 Internal Server Error

```json
{
  "status": "error",
  "message": "Invalid data provided"
}
```

### Chat

---

`/api/v1/user/login`

Logs in a user.

*Accepts a form*
- email
- password

*Returns*

**on success:**
HTTP 200 OK

```json
{
  "status": "success", 
  "message": "Login successful",
  "session": {
    "id": "32813",
    "username": "johndoe",
    "email": "example@email.com"
  }
}
```

**on fail:**

See generic errors

---
`/api/v1/user/register`

Registers a user.

*Accepts a form* **(requires auth)**
- username
- email
- password

*Returns*

**on success:**

HTTP 200 OK
```json
{
  "status": "success", 
  "message": "Login successful"
}
```

**on fail:**

See generic errors

---
`/api/v1/user/update`

Updates user attributes e.g. username, password etc.

*Accepts a form* **(requires auth)**
- username
- email
- password

*Returns*

**on success:**

HTTP 200 OK
```json
{
  "status": "success", 
  "message": "Info update successful"
}
```

**on fail:**

See generic errors

---
`/api/v1/user/@me`

Checks if the current user has a session or not. Used if you want to check auth status.

*Returns*

**on success:**

HTTP 200 OK
```json
{
  "status": "success", 
  "user": {
    "id": "32813",
    "username": "johndoe",
    "email": "example@email.com"
  }
}
```

**on fail:**

HTTP 401 Internal Server Error

```json
{
  "status": "error",
  "message": "Unauthorized"
}
```

See generic errors

---
`/api/v1/user/logout`

Logs the user out and ends the current session. **(requires auth)**

*Returns*

**on success:**

HTTP 200 OK
```json
{
  "status": "success", 
  "message": "Logged out successfully"
}
```

***

