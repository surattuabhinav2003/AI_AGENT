import fitz  # PyMuPDF
import io



def extract_text(file):
    try:
        content = file["content"]
        mime = file.get("mime")
        name = file.get("name", "")

        # -------- PDF --------
        if mime == "application/pdf" or name.endswith(".pdf"):
            doc = fitz.open(stream=content, filetype="pdf")

            text = ""
            for page in doc:
                text += page.get_text()

            return text

        # -------- TEXT / MARKDOWN --------
        elif mime in ["text/plain", "text/markdown"] or name.endswith((".txt", ".md")):
            return content.decode("utf-8", errors="ignore")

        else:
            return ""

    except Exception as e:
        raise Exception(f"Error parsing file {file.get('name')}: {str(e)}")