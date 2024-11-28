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
3. And finally, do `pipenv shell`