from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

from services.auth import get_credentials


# -------- CREATE DRIVE SERVICE --------
def get_drive_service():
    creds = get_credentials()
    return build('drive', 'v3', credentials=creds)


# -------- LIST FOLDERS --------
def list_folders():
    service = get_drive_service()

    results = service.files().list(
        q="mimeType='application/vnd.google-apps.folder' and trashed=false",
        spaces="drive",
        fields="files(id, name)",
        pageSize=20
    ).execute()

    folders = results.get("files", [])

    print("Folders:", folders)  # DEBUG

    return folders


# -------- LIST FILES IN FOLDER --------
def list_files_in_folder(folder_id):
    service = get_drive_service()

    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name, mimeType)",
        pageSize=50
    ).execute()

    files = results.get("files", [])

    print("Files in folder:", files)  # DEBUG

    return files


# -------- DOWNLOAD FILES (PDF + TXT + MD) --------
def download_files_from_folder(folder_id):
    service = get_drive_service()
    files = list_files_in_folder(folder_id)

    supported_files = []

    for file in files:
        mime = file["mimeType"]
        name = file["name"]

        # ✅ Supported types
        if mime in [
            "application/pdf",
            "text/plain",
            "text/markdown"
        ] or name.endswith((".txt", ".md")):

            request = service.files().get_media(fileId=file["id"])

            file_data = io.BytesIO()
            downloader = MediaIoBaseDownload(file_data, request)

            done = False
            while not done:
                _, done = downloader.next_chunk()

            file_data.seek(0)

            supported_files.append({
                "name": name,
                "content": file_data.read(),
                "mime": mime
            })

    print("Files downloaded:", [f["name"] for f in supported_files])  # DEBUG

    return supported_files