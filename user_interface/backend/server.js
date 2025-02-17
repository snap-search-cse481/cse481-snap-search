const express = require('express');
const multer = require('multer');
const fs = require('fs');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3001;

app.use(cors());

// Ensure 'uploads' folder exists
const uploadDir = 'uploads';
if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir);
}

// Function to clear the 'uploads' directory **before uploading a new file**
const clearUploadsDirectory = () => {
    fs.readdirSync(uploadDir).forEach((file) => {
        fs.unlinkSync(path.join(uploadDir, file)); // Synchronous delete to ensure it's done before saving the new file
    });
};

// Multer Storage Configuration
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        clearUploadsDirectory(); // **Delete existing file(s) before saving the new one**
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        const ext = path.extname(file.originalname); // Get file extension
        cb(null, `photo${ext}`); // Always save as "photo.jpg" or "photo.png"
    }
});

const upload = multer({ storage: storage });

// Image Upload Endpoint
app.post('/uploadphoto', upload.single('image'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ message: 'No file uploaded' });
    }

    console.log('File uploaded:', req.file.filename);

    res.json({ message: 'File uploaded successfully', filePath: `/uploads/photo${path.extname(req.file.originalname)}` });
});

// Serve Uploaded Images Statically
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

app.listen(PORT, () => {
    console.log(`Server started on port ${PORT}`);
});
