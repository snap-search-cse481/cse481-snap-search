import time
import requests
import urllib.request
import os
from tqdm import tqdm

TESTING_MODE = True
APITOKEN = '' # Your API Token

def search_by_face(image_file, debug=False):
    if TESTING_MODE:
        print('****** TESTING MODE search, results are inacurate, and queue wait is long, but credits are NOT deducted ******')

    assert APITOKEN, 'You must set your API token in the APITOKEN variable'

    site='https://facecheck.id'
    headers = {'accept': 'application/json', 'Authorization': APITOKEN}
    files = {'images': open(image_file, 'rb'), 'id_search': None}
    response = requests.post(site+'/api/upload_pic', headers=headers, files=files).json()

    if response['error']:
        return f"{response['error']} ({response['code']})", None

    id_search = response['id_search']
    print(response['message'] + ' id_search='+id_search)
    json_data = {'id_search': id_search, 'with_progress': True, 'status_only': False, 'demo': TESTING_MODE}


    # Create a progress bar to indicate position in queue & progress
    posn = -1
    max_posn = -1

    with tqdm(
        total=0,  # Setting total to 0 makes it indeterminate
        desc="Initializing"
    ) as pbar:

        while True:
            response = requests.post(site+'/api/search', headers=headers, json=json_data).json()
            if response['error']:
                return f"{response['error']} ({response['code']})", None
            if response['output']:
                if posn > 0:
                    pbar.set_description(f'Position in queue: {0}')
                    pbar.update(1)
                links_with_scores = [(img['score'], img['url']) for img in response['output']['items']]
                links_with_scores.sort(reverse=True, key=lambda x: x[0])
                # Debug prints
                if debug:
                    print_result(response['output']['items'])
                return None, links_with_scores
            
            # Handle progress response & update progress bar accordingly
            if response["message"].startswith('Waiting in queue. '):
                try:
                    new_posn = int(response["message"][len('Waiting in queue. '):-8])
                    if new_posn != posn:
                        posn = new_posn
                        pbar.set_description(f'Position in queue [{posn}]')
                        if new_posn > max_posn:
                            max_posn = new_posn
                            pbar.total = max_posn
                            pbar.refresh()
                        else:
                            pbar.update(1)
                        # print(f'Position in queue: {posn}')
                except ValueError:
                    pass
            else:
                # if response["message"].startswith('Submitted') or response["message"].startswith('Downloading'):
                if posn > 0:
                    posn -= 1
                    pbar.set_description(f'Position in queue: {posn}')
                    pbar.update(1)
                    pbar.close()
                print(f'{response["message"]} progress: {response["progress"]}%')
            
            time.sleep(1)

def print_result(urls_images):
    print(f'DEBUG: Found {len(urls_images)} images')

    if urls_images:
        links_with_scores = [(img['score'], img['url']) for img in urls_images]
        links_with_scores.sort(reverse=True, key=lambda x: x[0])

        print(links_with_scores)

# Main method for demonstration & debug purpose
if __name__ == '__main__':
    # Test photo
    image_file = './photo.jpg'
    assert os.path.exists(image_file), f'File {image_file} does not exist'

    # Run lookup on test photo
    search_by_face(image_file, debug=True)