from pathlib import Path
import re
import sqlite3
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "notes.db"
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_FILE_BYTES = 10 * 1024 * 1024

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-before-deployment"
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_BYTES
UPLOAD_DIR.mkdir(exist_ok=True)


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                stored_name TEXT NOT NULL,
                content TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def extract_text(path):
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    return path.read_text(encoding="utf-8", errors="replace").strip()


def split_text(text, chunk_size=900, overlap=150):
    text = re.sub(r"\s+", " ", text).strip()
    chunks, start = [], 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start + chunk_size // 2, end)
            if boundary > start:
                end = boundary
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def terms(text):
    return set(re.findall(r"[a-zA-Z0-9_+#.-]{2,}", text.lower()))


def search_documents(query):
    query_terms = terms(query)
    with get_db() as db:
        rows = db.execute("SELECT id, filename, content FROM documents ORDER BY uploaded_at DESC").fetchall()
    results = []
    for row in rows:
        for number, chunk in enumerate(split_text(row["content"]), start=1):
            matched = query_terms & terms(chunk)
            score = len(matched) / (len(query_terms) ** 0.5) if query_terms else 0
            if score:
                results.append({
                    "document_id": row["id"], "filename": row["filename"],
                    "chunk": chunk, "score": score,
                    "matched_terms": sorted(matched), "chunk_number": number
                })
    results.sort(key=lambda result: result["score"], reverse=True)
    return results[:10]


@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    results = search_documents(query) if query else []
    with get_db() as db:
        documents = db.execute(
            "SELECT id, filename, uploaded_at, LENGTH(content) AS characters "
            "FROM documents ORDER BY uploaded_at DESC"
        ).fetchall()
    return render_template("index.html", query=query, results=results, documents=documents)


@app.route("/upload", methods=["POST"])
def upload():
    uploaded = request.files.get("document")
    if not uploaded or not uploaded.filename:
        flash("Choose a PDF, TXT, or Markdown file first.", "error")
        return redirect(url_for("index"))
    filename = Path(uploaded.filename).name
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        flash("Unsupported file type. Please upload PDF, TXT, or MD.", "error")
        return redirect(url_for("index"))

    stored_name = f"{uuid.uuid4().hex}{suffix}"
    destination = UPLOAD_DIR / stored_name
    uploaded.save(destination)
    try:
        content = extract_text(destination)
        if not content:
            raise ValueError("No selectable text found. Scanned/image-only PDFs need OCR first.")
        with get_db() as db:
            db.execute(
                "INSERT INTO documents (filename, stored_name, content) VALUES (?, ?, ?)",
                (filename, stored_name, content)
            )
    except Exception as exc:
        destination.unlink(missing_ok=True)
        flash(f"Could not process that file: {exc}", "error")
        return redirect(url_for("index"))
    flash(f"Uploaded and indexed: {filename}", "success")
    return redirect(url_for("index"))


@app.route("/delete/<int:document_id>", methods=["POST"])
def delete_document(document_id):
    with get_db() as db:
        row = db.execute("SELECT stored_name FROM documents WHERE id = ?", (document_id,)).fetchone()
        if row:
            db.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            (UPLOAD_DIR / row["stored_name"]).unlink(missing_ok=True)
            flash("Document deleted.", "success")
        else:
            flash("Document not found.", "error")
    return redirect(url_for("index"))


@app.errorhandler(413)
def file_too_large(_error):
    flash("File is too large. Maximum upload size is 10 MB.", "error")
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    # Development server for local use only.
    app.run(debug=True)
