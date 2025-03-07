from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from threading import Thread
import os
import os.path as osp
import sys
from tqdm import tqdm
import time
import json

from facecheck_api import search_by_face, ResultEntry
from sentence_embedding import build_signature_from_top5, compute_signature_overlap, get_page_text
from typing import Optional, Dict, List, Tuple

lm_dir = osp.join(osp.abspath(osp.join(osp.dirname(__file__), '..')), "language_models")
sys.path.append(lm_dir)
from lm_client import GeminiClient

lm_client = GeminiClient(api_key="AIzaSyBGmTP8OCrfNXydpQjZxI_OL2VX9XC_VfY")

def filter_links_worker(signature_data,
                results: List[ResultEntry],
                output: List[ResultEntry],
                cache:Optional[Dict[str, str]] = None):
    # Filter the rest of the links
    for res in results:
        url = res[1]
        page_text = get_page_text(url)
        if page_text and compute_signature_overlap(signature_data, page_text):
            output.append(res)
            # Optionally cache web text
            if cache is not None:
                cache[url] = page_text


def filter_links(signature_data,
                 src_results: List[ResultEntry],
                 cache: Optional[Dict[str, str]] = None,
                 limit: int = 10) -> List[ResultEntry]:
    yes_list: List[Tuple[int, str]] = []

    if limit < len(src_results):
        src_results = src_results[:limit]

    start = time.time()

    num_cpus = os.cpu_count()
    assert num_cpus is not None
    NUM_WORKERS = min(len(src_results), num_cpus)
    step = len(src_results) // NUM_WORKERS
    threads = []
    for i in range(NUM_WORKERS):
        start_idx = i * step
        end_idx = (i + 1) * step if i < NUM_WORKERS - 1 else len(src_results)
        thread = Thread(target=filter_links_worker, args=(signature_data, src_results[start_idx:end_idx], yes_list, cache))
        thread.start()
        threads.append(thread)

    
    for thread in threads:
        thread.join()
    
    # Sort in descending score order (Order might've been changed by threading)
    yes_list.sort(key=lambda x: x[0], reverse=True)

    end = time.time()
    print(f"🔎 Filtered links in {end - start:.2f} seconds")
    
    return yes_list

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

# Configure upload folder and allowed extensions if necessary
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploadphoto', methods=['POST'])
def upload_photo():
    start = time.time()
    # Check if the request contains the file part
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400
    
    image = request.files['image']
    
    # Check if a file was selected
    if image.filename is None or image.filename == '':
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

    # The generator function that will yield SSE messages
    def generate():
        # 1) Searching by face
        yield "event: progress\n"
        yield "data: 😄 Running face search\n\n"
        error_msg, search_results = search_by_face(file_path, bypass=True)
        if search_results is None:
            yield "event: error\n"
            yield f"data: Face lookup error\n\"{error_msg}\"\n\n"
            return
        
        # Web text cache
        web_content: Dict[str, str] = {}
        
        # 2) Building signature
        # yield "event: progress\n"
        # yield "data: 🪪 Building profile signatures\n\n"
        search_results.sort(key=lambda x: x[0], reverse=True)
        top5 = [x[1] for x in search_results[:5]]
        remaining_results = search_results[5:]
        signature_data = build_signature_from_top5(top5, cache=web_content)
        yield "event: progress\n"
        yield "data: 🪪 Building profile signatures\n\n"
        
        # 3) Filtering additional links
        yield "event: progress\n"
        yield "data: 🔍 Finding & filtering additional information\n\n"
        yes_list = filter_links(signature_data, remaining_results, cache=web_content)
        
        # 4) Querying LLM
        yield "event: progress\n"
        yield "data: 📝 Summarizing person information\n\n"

        ##### Make calls to LLM #####
        # Prepare the query
        yes_list.extend(search_results[:5])
        query = '.'.join([f"\nSOURCE:\n {web_content[url]}" for _, url in yes_list])
        
        print("🤖 Querying LLM...\n")

        # Retry up to 3 times
        person_info = None
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                person_info = lm_client.extract_person_info(query)
                if person_info is not None and 'raw_response' not in person_info:
                    break
                
                yield "event: progress\n"
                yield f"data: 😥 Attempt {attempt + 1}/{max_attempts}: LLM returned malformatted summary, retrying...\n\n"
                print(f"Attempt {attempt + 1}/{max_attempts} failed with error: LLM returned malformatted summary")
            except Exception as e:
                print(f"Attempt {attempt + 1}/{max_attempts} failed with error: {e}")
        
        if person_info is None or 'raw_response' in person_info:
            yield "event: error\n"
            yield "data: LLM failed to return a valid summary\n\n"
            return
        
        # Print the extracted information
        print(f"Name: {person_info.get('name', '')}")
        print(f"Profession: {person_info.get('profession', '')}")
        print(f"Workplace: {person_info.get('workplace', '')}")
        print(f"Email: {person_info.get('email', '')}")
        print(f"Phone: {person_info.get('phone', '')}")
        print("Fun Facts:")
        print("\n".join([f"- {fact}" for fact in person_info.get('fun_facts', [])]))
        
        # Return the result
        yield "event: result\n"
        yield f"data: {json.dumps(person_info)}\n\n"
        end = time.time()
        print(f"Total time: {end - start:.2f} seconds")
    
    # Return a streaming response (SSE) instead of a single JSON
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(port=3001, debug=False, threaded = True)