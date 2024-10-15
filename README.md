# Report
### app.py
This code is a Flask-built Python web application. It offers standard file upload and download capabilities together with an extra layer of protection via encryption and decryption.

1. App initialization
   ```py
   app = Flask(__name__)
   ```
   This line initializes the app
   ```py
   app.config['SECRET_KEY'] = 'OMG_I_LOVE_INFORMATION_SECURITY'
   app.config['UPLOAD_FOLDER'] = 'uploads'
   ```
   `SECRET_KEY` is used to protect CSRF. Here, the string is hardcoded into the application.
   `UPLOAD_FOLDER` is used to define the folder where the files that are going to be uploaded are stored
   
2. Index Route
   ```py
   @app.route('/')
    def index():
    return render_template('index.html')
    ```
   This initializes `/` as the homepage of the app and it gives us `index.html`
   
3. File Upload Route
   ```py
   @app.route('/upload', methods=['POST'])
    def upload_file():
   ```
   The route `/upload` handles the file uploads using the method `POST`
   ```py
       if 'file' not in request.files:
        return 'No file part in the request', 400
   ```
   This checks if there is no file uploaded, it will return a 400 HTTP error
   ```py
       file = request.files['file']
   ```
   uses the `file` input to retrieve the file from the incoming request
   ```py
       if file.filename == '':
        return 'No selected file', 400
   ```
   Checks whether the filename is empty or not. If it is empty, the function returns to an error 400
   ```py
     if file and file.filename:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
   ```
   This part verifies that the file is legitimate and safely stored. It begins by verifying that the file is present and has a valid filename. Next, in order to guard against security threats such directory traversal attacks, secure_filename sanitizes the filename. The sanitized filename and the upload folder are joined to create the file path. Ultimately, the file is saved at that path on the server.
   ```py
   key = encrypt_file(file_path)
   ```
   This encrypts the file that is uploaded. It takes the file path as an input, encrypts the content, then returns as encryption key
   ```py
   key_str = key.decode()
    return 'File uploaded successfully.\nKey: ' + key_str, 200
   ```
   This converts and returns the encryption key. If the file is uploaded successfully, it will display a 200 OK code.

4. Download Route
   ```py
   @app.route('/download/<key>/<filename>')
   ```
   Defines the route where the URL includes `key` and `filename` as path parameters
   ```py
   key_bytes = key.encode()
   path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    ```
  Converts key back to bytes and then constructs the file path where the uploaded file is stored.
  ```py
  try:
    decrypted_data = decrypt_file(path, key_bytes)
except Exception as e:
    return "Invalid decryption key", 500
  ```
  Decryption process with error handling. If it fails, the function returns the message `Invalide decryption key` with Error message 500
  ```py
  with NamedTemporaryFile(delete=False) as temp_file:
    temp_file.write(decrypted_data)
    temp_file_path = temp_file.name
  ```
  Write the decrypted data to temporsry file
  ```py
  return send_file(temp_file_path, as_attachment=True, download_name=filename)
  ```
  Sends the decrypted file to uaser
5. Encryptuon Function
  ```py
  key = Fernet.generate_key()
  fernet = Fernet(key)
  ```
  Generates the key
  ```py
  with open(file_path, 'rb') as f:
    data = f.read()
  encrypted_data = fernet.encrypt(data)

  ```
  Reads the file contents and encryps the data
  ```py
  with open(file_path, 'wb') as f:
    f.write(encrypted_data)
  return key
  ```
Writes the encrypted data back to file and returns the key

5. Decryption Function
   ```py
   fernet = Fernet(key)
    with open(file_path, 'rb') as f:
    encrypted_data = f.read()
    ```
  Sets up Fernet with the key then reads the encrypted file
  ```py
  decrypted_data = fernet.decrypt(encrypted_data)
  return decrypted_data
  ```
  Decrypting the encrypted data then returns the decrypted data

6. Running the app
   ```py
   if __name__ == '__main__':
    app.run(debug=True)
    ```
  This ensures that the app will run in debug mode

   
