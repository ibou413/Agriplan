import os
from tempfile import NamedTemporaryFile
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    cred_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if cred_json:
        with NamedTemporaryFile(delete=False) as temp:
            temp.write(cred_json.encode())
            temp.flush()
            cred = credentials.Certificate(temp.name)
            firebase_admin.initialize_app(cred)
    else:
        raise Exception("GOOGLE_CREDENTIALS_JSON is not set")
