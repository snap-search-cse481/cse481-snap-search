from flask import Flask, request, jsonify
import flask
import time
import requests
import urllib.request
import sys

app = Flask(__name__)

TESTING_MODE = True
APITOKEN = '' # Your API Token

def search_by_face(file_stream):
    if TESTING_MODE:
        print('****** TESTING MODE search, results are inacurate, and queue wait is long, but credits are NOT deducted ******')

    site = 'https://facecheck.id'
    headers = {'accept': 'application/json', 'Authorization': APITOKEN}
    
    # Use the file stream directly instead of opening a file
    files = {'images': file_stream, 'id_search': None}
    response = requests.post(site+'/api/upload_pic', headers=headers, files=files).json()

    if response.get('error'):
        return f"{response['error']} ({response['code']})", None

    id_search = response['id_search']
    print(response['message'] + ' id_search='+id_search)
    json_data = {'id_search': id_search, 'with_progress': True, 'status_only': False, 'demo': TESTING_MODE}

    while True:
        response = requests.post(site+'/api/search', headers=headers, json=json_data).json()
        if response.get('error'):
            return f"{response['error']} ({response['code']})", None
        if response.get('output'):
            return None, response['output']['items']
        print(f'{response["message"]} progress: {response["progress"]}%')
        time.sleep(1)


@app.route('/face_search', methods=['POST'])
def face_search() -> flask.Response:
    """Search the internet for a face in an image

    Returns:
        Response: JSON response with the search results
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file in request'}), 400
    
    image_file = request.files['image']

    if image_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    files = {'images': (image_file.filename, image_file.stream, image_file.mimetype)}
    search_by_face(files)


image_file = '/Users/alexl/Pictures/logo.png'

# Search the Internet by face
error, urls_images = search_by_face(image_file)

if urls_images:
    for im in urls_images:      # Iterate search results
        score = im['score']     # 0 to 100 score how well the face is matching found image
        url = im['url']         # url to webpage where the person was found
        image_base64 = im['base64']     # thumbnail image encoded as base64 string
        print(f"{score} {url} {image_base64[:32]}...")
else:
    print(error)