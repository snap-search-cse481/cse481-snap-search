<div align="center">
  <h1>📸 SnapSearch</h1>
  <h3>CSE 481 Wi 2025 Capstone Project at University of Washington</h3>
  <p>Contributors: Alex Luo, Rudra Prakash Singh, Angie Suwitono</p>
</div>

## Purpose 🎯
- **USA Data:**  
  - 10-20M attendees at scientific conferences  
  - 5-10M attendees of recruiting events  
- **Issue:**  
  - It’s impossible to remember the information of everyone you meet.  
- **Solution:**  
  - Use our app to take a picture of each person you meet.  
- **Output:**  
  - Instantly retrieve that person's personal details at your fingertips (email, phone #, workplace, etc.)


## Technologies Used 🛠️
- **Frontend:** JavaScript, HTML, CSS  
- **Backend:** Python (Flask)  
- **APIs:** FaceCheck.id  
- **Link Sorting:** BeautifulSoup, NLTK  
- **LLM Integration:** Ollama, DSPy


## Workflow 🔄

1. **User Input:**  
   - Take a photo or search by name.

2. **Backend Processing:**  
   - Send image to FaceCheck.id API.  
   - Retrieve and analyze search results.  
   - Sort links using text similarity analysis.  
   - Query LLM for additional information.

3. **Output:**  
   - Display personal details and relevant links.


## Try It Out 🚀
Get started by following steps below to use Snap Search!

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

