import os
from flask import redirect, request, session, jsonify
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import google.auth.transport.requests

# ---------- CONFIG ----------
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

REDIRECT_URI = os.getenv(
    "REDIRECT_URI",
    "http://127.0.0.1:5000/callback"
)

# Allow HTTP locally
if "127.0.0.1" in REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


# ---------- CREATE FLOW ----------
def create_flow():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )


    flow.code_verifier = None
    flow.autogenerate_code_verifier = False

    return flow

# ---------- LOGIN ----------
def login():
    try:
        flow = create_flow()

        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        session['state'] = state
        return redirect(auth_url)

    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500



def callback():
    try:
        if "state" not in session:
            return jsonify({"error": "Session expired. Please login again."}), 400

        flow = create_flow()
        flow.state = session['state']

        flow.fetch_token(authorization_response=request.url)

        credentials = flow.credentials

        session['credentials'] = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }

        return redirect("/?login=success")

    except Exception as e:
        return jsonify({"error": f"Callback failed: {str(e)}"}), 500


# ---------- GET CREDENTIALS ----------
def get_credentials():
    creds_dict = session.get("credentials")

    if not creds_dict:
        return None

    creds = Credentials(**creds_dict)

    # ---------- AUTO REFRESH ----------
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(google.auth.transport.requests.Request())

            session['credentials'] = {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes
            }

        except Exception:
            session.pop("credentials", None)
            return None

    return creds


# ---------- CHECK LOGIN ----------
def is_logged_in():
    return 'credentials' in session


# ---------- LOGOUT ----------
def logout():
    session.clear()
    return redirect("/")