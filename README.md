# CSE 481 P: Human tagging


# Running the Web UI
## Install dependencies
```bash
cd user_interface
npm run install:frontend
```
## Running the frontend user interface
`frontend` is the actual web UI and the server is for receiving images. The latter is implemented in Python with flask in `backend/handle_image_upload.py` which will automatically spawn a new thread to send the image to the face search engine.

Assuming we're already in the `user_interface` directory.

- Then you can run the actual web UI with `npm run start:frontend`

# Running the Python backend
## Install conda environment
Run `conda env create -f environment.yml` from project root directory.

## Running the backend server
`python backend/handle_image_upload.py`

