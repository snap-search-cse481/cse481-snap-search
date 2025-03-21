<div align="center">
  <h1>📸 SnapSearch</h1>
  <h3>CSE 481 Wi 2025 Capstone Project at University of Washington (Prof Gollakota)</h3>
  <p>Contributors: Alex Luo, Rudra Prakash Singh, Angie Suwitono</p>
</div>

## Purpose 🎯
- **USA Data:**  
  - 10-20M attendees at scientific conferences  
  - 5-10M attendees of recruiting events  
- **Issue:**  
  - It’s impossible to remember the information of everyone you meet.
- **Solution:**  
  - Use our app to take a picture of the people you meet.
- **Output:**  
  - Instantly retrieve that person's information at your fingertips (email, workplace, etc.)


## Technologies Used 🛠️
- **Frontend:** JavaScript, HTML, CSS  
- **Backend:** Python (Flask)
- **APIs:** FaceCheck.id, DuckDuckGo search, GitHub
- **Link Sorting:** BeautifulSoup, NLTK  
- **LLM Integration:** Ollama, DSPy, Qwen


## Workflow 🔄

1. **User Input:**  
   - Take or upload a photo.

2. **Backend Processing:**  
   - Send image to FaceCheck.id API.  
   - Retrieve and analyze search results.  
   - Sort links using text similarity analysis.
   - Fetch additional information from the web if necessary.
   - Query LLM to distill person information and generate summary.

3. **Output:**  
   - Display personal details and relevant links.


## Try It Out 🚀
Get started by following steps below to use Snap Search!

### Running the Web UI
#### Install dependencies
```bash
cd user_interface
npm run install:frontend
```
#### Running the frontend user interface
`frontend` is the actual web UI and the server is for receiving images. The latter is implemented in Python with flask in `backend/handle_image_upload.py` which will automatically spawn a new thread to send the image to the face search engine.

Assuming we're already in the `user_interface` directory, then we can run the actual web UI with `npm run start:frontend`

### Running the Python backend
#### Install conda environment
Run `conda env create -f environment.yml` from project root directory.

#### Running the backend server
Activate the above conda environment. Then run the flask backend with 
`python backend/handle_image_upload.py`

## Contribution & Credits 🎖️
**Alex:** Flask, Ollama LLM client & server setup, Extract URL, Link filtering quality & performance optimization, Code Cleanup

**Rudra:** Link Sorting, Extract URL, DSPy integration for LLM, Gemini Model Testing, Testing, Documentation/PPTs

**Angie:** Frontend development, Testing, Evaluation, Documentation/PPT

### Open source component
- [Facecheck.id-Extractor](https://github.com/quantumthe0ry/Facecheck.id-Extractor) (MIT License)
