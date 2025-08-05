from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sqlite3

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
DB_FILE = 'file.db'

# Create uploads folder
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Create DB table
def setup_database():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            filepath TEXT
        )''')
setup_database()

# Upload
@app.route('/documents/upload', methods=['POST'])

def upload():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({"message": "Only PDF files allowed"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO documents (filename, filepath) VALUES (?, ?)", (file.filename, filepath))
        conn.commit()

    return jsonify({"message": "Uploaded Successfully"})
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# List Files
@app.route('/documents', methods=['GET'])
def list_files():
    with sqlite3.connect(DB_FILE) as conn:
        files = conn.execute("SELECT id, filename FROM documents").fetchall()
    return jsonify([{"id": f[0], "filename": f[1]} for f in files])

# Download
@app.route('/documents/<int:file_id>', methods=['GET'])
def download(file_id):
    with sqlite3.connect(DB_FILE) as conn:
        row = conn.execute("SELECT filepath FROM documents WHERE id = ?", (file_id,)).fetchone()
    return send_file(row[0], as_attachment=True) if row else jsonify({"message": "File not found"}), 404

# Delete
@app.route('/documents/<int:file_id>', methods=['DELETE'])
def delete(file_id):
    with sqlite3.connect(DB_FILE) as conn:
        row = conn.execute("SELECT filepath FROM documents WHERE id = ?", (file_id,)).fetchone()
        if row:
            os.remove(row[0])
            conn.execute("DELETE FROM documents WHERE id = ?", (file_id,))
            conn.commit()
            return jsonify({"message": "Deleted"})
        return jsonify({"message": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
