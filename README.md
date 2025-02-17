# CSE 481 P: Human tagging


# Running the Web UI
## Install dependencies
```bash
cd user_interface
npm run install:frontend
npm run install:backend
```
## Running the frontend user interface
It's current broken up into 2 parts. `frontend` is the actual web UI and `backend` is the server for receiving images. We might be able to implement the latter directly in Python with flask, so it might not be necessary in the future.

Assuming we're already in the `user_interface` directory.

- To launch the current UI backend use `npm run start:server`.
- Then you can run the actual web UI with `npm run start:frontend`


# Install conda environment
Run `conda env create -f environment.yml` from project root directory.
