from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from threading import Thread
import os

from facecheck_api import search_by_face
from sentence_embedding import build_signature_from_top5, compute_signature_overlap, get_page_text

def threaded_face_search(file_path, results_container):
    """Runs the face search in a separate thread and stores results."""
    error_msg, results = search_by_face(file_path, False)
    results_container["error"] = error_msg
    results_container["results"] = results


def threaded_sentence_embedding(results_container):
    """Runs sentence embedding processing in a separate thread and stores categorized links."""
    links_with_scores = results_container.get("results", [])
    links_with_scores.sort(key=lambda x: x[0], reverse=True)
    
    top5 = [x[1] for x in links_with_scores[:5]]
    the_rest = [x[1] for x in links_with_scores[5:]]
    
    signature = build_signature_from_top5(top5)
    
    yes_list = []
    no_list = []
    
    for url in the_rest:
        page_text = get_page_text(url)
        if page_text:
            if compute_signature_overlap(signature, page_text):
                yes_list.append(url)
            else:
                no_list.append(url)
        else:
            no_list.append(url)
    
    results_container["top5"] = top5
    results_container["yes_list"] = yes_list
    results_container["no_list"] = no_list

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

    results_container = {}

    # Start the search in a separate thread
    face_search_worker = Thread(target=threaded_face_search, args=(file_path, results_container))
    face_search_worker.start()
    face_search_worker.join()  # Wait for thread to finish
    
    if "error" in results_container and results_container["error"]:
        return jsonify({"error": results_container["error"]}), 500

    embedding_worker = Thread(target=threaded_sentence_embedding, args=(results_container,))
    embedding_worker.start()
    embedding_worker.join()

    # debugging
    # print("top 5")
    # print(results_container["top5"])
    # print("yes list")
    # print(results_container["yes_list"])
    # print("no list")
    # print(results_container["no_list"])

    
    return jsonify({
        "message": "Image successfully uploaded",
        "filename": filename,
        "results": results_container.get("results", []),
        "top5": results_container.get("top5", []),
        "yes_list": results_container.get("yes_list", []),
        "no_list": results_container.get("no_list", [])
    }), 200

if __name__ == '__main__':
    app.run(port=3001, debug=False)