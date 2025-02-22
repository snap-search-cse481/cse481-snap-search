# Backend Workflow

## Overview
This backend system processes images uploaded by users to perform facial similarity searches using the FaceCheck API. The system then categorizes the search results based on text similarity using sentence embeddings. The primary workflow is structured as follows:

1. **Image Upload:** Users upload an image via the frontend. The image is stored in the backend's `uploads` directory.
2. **Face Search Processing:** The uploaded image is sent to the FaceCheck API, which returns URLs and similarity scores of matching faces.
3. **URL Extraction:** Extract relevant URLs and similarity scores from the API response.
4. **Sentence Embedding Processing:** Classify extracted URLs into "Yes" (likely matches) and "No" (unlikely matches) using sentence embeddings and text similarity analysis.
5. **Response Generation:** Return categorized search results to the frontend.

## Technologies Used
- **Flask**: Backend framework for handling API requests.
- **Flask-CORS**: Enables cross-origin requests from the frontend.
- **Werkzeug**: Securely handles file uploads.
- **Threading**: Optimizes face search and text processing.
- **Requests**: Sends API requests to FaceCheck and fetches webpage content.
- **BeautifulSoup**: Parses webpage text for sentence embedding processing.
- **NLTK**: Tokenizes and filters text data for signature matching.

## Workflow Details
### 1. Image Upload
- The user uploads an image via the `/uploadphoto` API endpoint.
- The image is validated and securely saved in the `uploads` directory.
- The backend initiates a new thread for the FaceCheck API search.

### 2. Face Search
- The system calls `search_by_face()` from `facecheck_api.py`, which sends the image to FaceCheck.
- The API returns URLs and similarity scores for matching images.
- Extracted data is stored in a results container for further processing.

### 3. URL Extraction
- `extract_facecheck_url.py` extracts and decodes URLs from the FaceCheck API response.
- Extracted URLs and similarity scores are sorted by relevance.

### 4. Sentence Embedding Processing
- `sentence_embedding.py` processes the top 5 URLs to create a "signature" based on common words.
- Other URLs are compared against this signature to classify them as "Yes" or "No."
- The classification is performed based on text similarity and predefined thresholds.

### 5. Response Generation
- The backend compiles the categorized results (`top5`, `yes_list`, `no_list`).
- The processed data is returned as a JSON response to the frontend.

## API Endpoints
### `/uploadphoto` (POST)
Handles image upload and processing.
#### Request
```json
{
  "image": <uploaded_file>
}
```
#### Response
```json
{
  "message": "Image successfully uploaded",
  "filename": "uploaded_image.jpg",
  "results": [[score, url], ...],
  "top5": ["url1", "url2", ...],
  "yes_list": ["url3", "url4", ...],
  "no_list": ["url5", "url6", ...]
}
```
