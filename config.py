import os

os.environ["OPENAI_API_KEY"] = "sk-proj-DrVUWntO_M41qbVctYWmDKo0ePJO19x_xyZcXb7BjTZXV39jjoZE4K29knZeULcXDc2kQVS0jT3BlbkFJe2gdEMaVuWiR67i_TC7MTrpv_0zG7zavwbFgWFrI_L5HxlERG7Hgrx2bxI-j24oufOdh-73GoA"
# -------- GOOGLE OAUTH --------
GOOGLE_CLIENT_SECRETS = os.getenv("GOOGLE_CLIENT_SECRETS", "client_secret.json")

REDIRECT_URI = os.getenv(
    "REDIRECT_URI",
    "http://127.0.0.1:5000/callback"
)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


# -------- OPENAI --------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# -------- FLASK --------
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")


# -------- RAG SETTINGS --------
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 1.5))


# -------- FILE STORAGE --------
TEMP_FOLDER = os.getenv("TEMP_FOLDER", "temp")