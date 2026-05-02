import config 
from flask import Flask, render_template, request, jsonify, redirect

from services.auth import login, callback, logout, is_logged_in
from services.drive import list_folders, download_files_from_folder
from services.rag import load_documents, ask_question

app = Flask(__name__)

app.secret_key = "supersecretkey"



@app.route("/")
def home():
    return render_template("index.html")



@app.route("/login")
def login_route():
    return login()


@app.route("/callback")
def callback_route():
    return callback()


@app.route("/logout")
def logout_route():
    return logout()


@app.route("/list-folders")
def get_folders():
    try:
        if not is_logged_in():
            return jsonify({"error": "User not authenticated"}), 401

        folders = list_folders()

        # Ensure empty list handled properly
        return jsonify({
            "folders": folders
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/load", methods=["POST"])
def load_docs():
    try:
        if not is_logged_in():
            return jsonify({"error": "User not authenticated"}), 401

        data = request.get_json()
        folder_id = data.get("folder_id")

        if not folder_id:
            return jsonify({"error": "Folder ID is required"}), 400

        files = download_files_from_folder(folder_id)

        if not files:
            return jsonify({"error": "No PDF files found in this folder"}), 400

        load_documents(files)

        return jsonify({
            "message": "Documents loaded successfully",
            "files": [f["name"] for f in files]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------- ASK QUESTION --------
@app.route("/ask", methods=["POST"])
def ask():
    try:
        if not is_logged_in():
            return jsonify({"error": "User not authenticated"}), 401

        data = request.get_json()
        question = data.get("question")

        if not question:
            return jsonify({"error": "Question is required"}), 400

        result = ask_question(question)

        # 🔥 FORCE correct structure
        return jsonify({
            "answer": result.get("answer", "No answer"),
            "sources": result.get("sources", [])
        })

    except Exception as e:
        print("ASK ERROR:", e)
        return jsonify({
            "answer": "❌ Error occurred",
            "sources": []
        })


@app.route("/health")
def health():
    return jsonify({"status": "running"})



if __name__ == "__main__":
    app.run(debug=True)
