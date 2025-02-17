from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from threading import Thread
import os

from facecheck_api import search_by_face

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes


# Configure upload folder and allowed extensions if necessary
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploadphoto', methods=['POST'])
def upload_photo():
    # Check if the request contains the file part
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400
    
    image = request.files['image']
    
    # Check if a file was selected
    if image.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Optionally validate the file extension
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    if '.' in image.filename and \
       image.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({"error": "File type not allowed"}), 400

    # Save the file securely
    filename = secure_filename(image.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(file_path)

    # Start a thread to process the image with facecheck ID
    face_search_worker = Thread(target=search_by_face, args=(file_path, True))
    face_search_worker.start()

    return jsonify({"message": "Image successfully uploaded", "filename": filename}), 200

if __name__ == '__main__':
    app.run(port=3001, debug=False)
