# Backend Workflow

## Overview
This backend processes uploaded images for facial similarity searches using the FaceCheck API and classifies results via sentence embeddings.

### Workflow:
1. **Image Upload** → Saved in `uploads/` directory.
2. **Face Search** → Image sent to FaceCheck API, returning URLs & similarity scores.
3. **URL Extraction** → Relevant URLs extracted and sorted.
4. **Text Classification** → Sentence embeddings classify matches as "Yes" or "No."
5. **Response Generation** → Categorized results sent to frontend.

## Technologies
- **Flask** (API backend)  
- **Flask-CORS** (Cross-origin requests)  
- **Werkzeug** (File handling)  
- **Threading** (Concurrent processing)  
- **Requests** (API & web scraping)  
- **BeautifulSoup** (HTML parsing)  
- **NLTK** (Text tokenization & filtering)  

## API Endpoints
### `/uploadphoto` (POST)
Handles image upload and processing.

#### Request:
```json
{
  "image": <uploaded_file>
}
```

#### Response:
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
