from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
import tempfile
import PyPDF2
from docx import Document
from groq import Groq
import uuid

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
UPLOAD_FOLDER = tempfile.gettempdir()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = Groq(api_key="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")

# Helper to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper to extract text from files
def extract_text(filepath, ext):
    if ext == 'pdf':
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif ext == 'docx':
        doc = Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs])
    elif ext == 'txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return ""

# Summarize endpoint
@app.route('/summarize', methods=['POST'])
def summarize():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        ext = filename.rsplit('.', 1)[1].lower()
        text = extract_text(filepath, ext)
        # Summarize using Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes documents."},
                {"role": "user", "content": f"Summarize the following document:\n{text}"}
            ],
            model="llama-3.3-70b-versatile"
        )
        summary = chat_completion.choices[0].message.content
        return jsonify({'summary': summary, 'document_text': text})
    else:
        return jsonify({'error': 'Invalid file type'}), 400

# Q&A endpoint
@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    document_text = data.get('document_text')
    if not question or not document_text:
        return jsonify({'error': 'Missing question or document text'}), 400
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions about a document."},
            {"role": "user", "content": f"Document: {document_text}\nQuestion: {question}"}
        ],
        model="llama-3.3-70b-versatile"
    )
    answer = chat_completion.choices[0].message.content
    return jsonify({'answer': answer})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True)