# 📚 NoteNest — College Notes Search Assistant

NoteNest is a student-friendly web app for uploading lecture notes and searching the text inside them. It uses Flask, SQLite, and Python to store documents and retrieve relevant excerpts.

**Important:** This starter version uses keyword-based search. It does not call an AI model or generate answers yet. You can extend it with embeddings, semantic search, and retrieval-augmented generation (RAG).

## Features
- Upload text-based PDF, TXT, and Markdown (`.md`) notes
- Extract text from PDFs
- Search uploaded notes with keyword matching
- Display relevant text excerpts and matched terms
- Store document metadata and extracted text in SQLite
- Delete uploaded documents
- Responsive dark-themed interface
- 10 MB per-file upload limit
- No paid API key required

## Project structure
```text
ai-college-notes-assistant/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/index.html
├── static/style.css
└── uploads/.gitkeep
```

## Run locally (Windows / VS Code)
1. Install Python 3.10 or newer.
2. Open this folder in VS Code and open its terminal.
3. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install packages:
   ```powershell
   python -m pip install -r requirements.txt
   ```
5. Run:
   ```powershell
   python app.py
   ```
6. Open `http://127.0.0.1:5000` in your browser.

If PowerShell blocks activation, run `.venv\Scripts\python.exe -m pip install -r requirements.txt`, then `.venv\Scripts\python.exe app.py`.

## Run locally (macOS / Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```
Then visit `http://127.0.0.1:5000`.

## Try it
1. Upload a PDF with selectable text, TXT, or MD file.
2. Search for terms such as `inheritance`, `neural networks`, or `database`.
3. Read matching excerpts and matched keywords.
4. Delete a document from the uploaded notes list if needed.

Scanned PDFs made only of images need OCR before text can be extracted.

## Upload to GitHub
Create a repository named `ai-college-notes-assistant`, then upload the source files and folders. Do not upload private lecture notes, `notes.db`, `.env` files, or real contents of the `uploads/` directory.

## Deployment and security notes
This is a local learning project. The Flask development server is not for production. Before public deployment, set a strong secret key through an environment variable, disable debug mode, add authentication, and use persistent storage for uploaded files and the database. Cloud hosts may erase local files when an app restarts.

## Future improvements
- Semantic search with sentence embeddings
- AI-generated answers with citations to source excerpts
- OCR for scanned PDFs
- User accounts and separate private libraries
- Subject/semester tags, flashcards, and summaries
- Automated tests and deployment configuration

## Tech stack
Python · Flask · SQLite · pypdf · HTML · CSS
