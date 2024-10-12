from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, send_file
from cryptography.fernet import Fernet
import secrets
import os
from werkzeug.utils import secure_filename
from tempfile import NamedTemporaryFile

app = Flask(__name__)

app.config['SECRET_KEY'] = 'OMG_I_LOVE_INFORMATION_SECURITY'
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the request', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and file.filename:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Assuming there's a function to encrypt the file
        key = encrypt_file(file_path)
        # Convert the key to a string for user
        key_str = key.decode()
        return 'File uploaded successfully.\nKey: ' + key_str, 200

@app.route('/download/<key>/<filename>')
def download_file(key, filename):
    # Convert the key string back to bytes for decryption
    key_bytes = key.encode()
    # Assuming there's a function to decrypt the file
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # catch error cryptography.fernet.InvalidToken
    try:
        decrypted_data = decrypt_file(path, key_bytes)
    except Exception as e:
        return "Invalid decryption key", 500

    # Write decrypted data to a temporary file
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(decrypted_data)
        temp_file_path = temp_file.name

    # Specify the download name for the file
    return send_file(temp_file_path, as_attachment=True, download_name=filename)

def encrypt_file(file_path):
    # Generate a key using secrets.token_bytes and ensure it's 32 url-safe base64-encoded bytes
    key = Fernet.generate_key()
    fernet = Fernet(key)
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    encrypted_data = fernet.encrypt(data)
    
    with open(file_path, 'wb') as f:
        f.write(encrypted_data)
    
    # Return the key for future use (store it securely)
    return key

def decrypt_file(file_path, key):
    fernet = Fernet(key)
    
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    
    decrypted_data = fernet.decrypt(encrypted_data)
    
    # Return the decrypted data directly without writing it back to the file
    return decrypted_data

if __name__ == '__main__':
    app.run(debug=True)