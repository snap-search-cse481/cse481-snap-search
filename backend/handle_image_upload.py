from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from threading import Thread
import os
from tqdm import tqdm

from facecheck_api import search_by_face
from sentence_embedding import build_signature_from_top5, compute_signature_overlap, get_page_text
from typing import Dict

def threaded_face_search(file_path, results_container):
    """Runs the face search & sentence embedding processing in a separate thread and stores categorized links."""
    error_msg, results = search_by_face(file_path, bypass=False)
    results_container["error"] = error_msg
    results_container["results"] = results

    links_with_scores = results_container.get("results", [])
    links_with_scores.sort(key=lambda x: x[0], reverse=True)
    
    top5 = [x[1] for x in links_with_scores[:5]]
    the_rest = [x[1] for x in links_with_scores[5:]]
    
    # Process top5 signatures
    print("Building top 5 signatures...")
    signature = build_signature_from_top5(top5)
    
    yes_list = []
    no_list = []
    
    web_content: Dict[str, str] = {}

    # Filter the rest of the links
    for url in tqdm(the_rest, desc="Filtering relevant sources signatures"):
        page_text = get_page_text(url)
        if page_text:
            if compute_signature_overlap(signature, page_text):
                yes_list.append(url)
                web_content[url] = page_text
            else:
                no_list.append(url)
        else:
            no_list.append(url)
    
    # Caches content from top 5
    for url in top5:
        page_text = get_page_text(url)
        if page_text:
            web_content[url] = page_text

    results_container["top5"] = top5
    results_container["yes_list"] = yes_list
    results_container["no_list"] = no_list

    ##### Make calls to LLM
    for url, text in web_content.items():
        print(f"Processed {url} with text {text[:200]}...\n")


app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

# Configure upload folder and allowed extensions if necessary
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'uploads')
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
    
    # if "error" in results_container and results_container["error"]:
    #     return jsonify({"error": results_container["error"]}), 500

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