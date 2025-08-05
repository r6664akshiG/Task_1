#app.py

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

import os 
import sqlite3

app = Flask(__name__)

CORS(app)



def setup_database():
        with sqlite3.connect('file.db') as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS documents(
                             id integer primary key autoincrement,
                             filename text,
                             filepath text)''')

setup_database()


#upload pdf 

@app.route('/documents/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file: 
        return jsonify({"message":"Please select the file"}),400
    
    if not file.filename.endswith('.pdf'):
        return jsonify({"message":"Only pdf files are accepted"}),400

    filepath = 'uploads/'+file.filename
    file.save(filepath)

    with sqlite3.connect('file.db') as conn:
        conn.execute("INSERT INTO documents(filename,filepath) values(?,?)",(file.filename,filepath))
    return jsonify({"message":"Uploaded Successfully"})
if not os.path.exists('uploads'):
    os.makedirs('uploads')
#get all the pdfs

@app.route('/documents',methods=['GET'])
def list_files():
    with sqlite3.connect('file.db')as conn:
        files = conn.execute("Select id,filename from documents").fetchall()
    return jsonify([{"id":f[0],"filename":f[1]} for f in files])
        

#down;oad

@app.route('/documents/<int:file_id>',methods=['GET'])
def download(file_id):
    with sqlite3.connect('file.db') as conn:
        row = conn.execute("Select filepath from documents where id = ?",(file_id)).fetchone()
    return send_file(row[0],as_attachment=True) if row else jsonify({"message":"File notfound"}),404

#DELETE

@app.route('/documents/<int:file_id>',methods=['DELETE'])

def delete(file_id):
    with sqlite3.connect('file.db') as conn:
        row = conn.execute("select filepath from documents where id = ?",(file_id,)).fetchone()
        if row:
            os.remove(row[0])
            conn.execute("delete from documents where id = ?",(file_id,))
            return jsonify({"message":"Deleted"})
        return jsonify({"message":"File is not found"}),404
    

if __name__== 'main_':
    app.run(debug=True)
