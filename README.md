# CSE 481 P: Human tagging


# Running the Web UI
## Install dependencies
```bash
cd user_interface
npm run install:frontend
npm run install:backend
```
## Running the frontend user interface
It's current broken up into 2 parts. `frontend` is the actual web UI and `backend` is the server for receiving images. The latter is now directly in Python with flask in `backend/handle_image_upload.py` which will automatically spawn a new thread to send the image to the face search engine, so it's probably not necessary in the future.

Assuming we're already in the `user_interface` directory.

- To launch the current UI backend use `npm run start:server`.
- Then you can run the actual web UI with `npm run start:frontend`

# Running the Python backend
## Install conda environment
Run `conda env create -f environment.yml` from project root directory.

## Running the backend server
`python backend/handle_image_upload.py`

