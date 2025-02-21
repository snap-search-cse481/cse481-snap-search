import React, {Component, createRef} from 'react';
import { Helmet, HelmetProvider } from "react-helmet-async";
import axios from 'axios';

const serverPort = 3001; 
const serverURL = `http://localhost:${serverPort}/`;

class CustomerApp extends Component {
  constructor() {
    super();
    this.state = {
      file: null
    };

    this.fileInputRef = createRef();
    this.dragAreaRef = createRef();
    this.resultsContainerRef = createRef();
    this.submitButton = createRef();
    this.picButton = createRef();
    this.or = createRef();
    this.popup = createRef();
    this.popupBg = createRef();
    this.capture = createRef();
    this.video = createRef();
    this.canvas = createRef();
  }

  componentDidMount() {
    console.log("Component Mounted");

    (function(i, s, o, g, r, a, m) {
        i['GoogleAnalyticsObject'] = r;
        i[r] = i[r] || function() {
            (i[r].q = i[r].q || []).push(arguments);
        };
        i[r].l = 1 * new Date();
        a = s.createElement(o);
        m = s.getElementsByTagName(o)[0];
        a.async = 1;
        a.src = g;
        m.parentNode.insertBefore(a, m);
    })(window, document, 'script', 'https://www.google-analytics.com/analytics.js', 'ga');

    window.ga = window.ga || function() {
        console.warn("Google Analytics is not available yet.");
    };

    if (typeof window.ga === "function") {
        window.ga('create', 'UA-48530561-1', 'auto');
        window.ga('send', 'pageview');
    } else {
        console.error("Google Analytics (ga) is not available.");
    }
}



  handleInputClick = () => {
    this.fileInputRef.current.click();
  }

  handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      this.setState({ file }, this.displayFile);
    }
  }

  handleDragOver = (event) => {
    event.preventDefault();
    this.dragAreaRef.current.classList.add("active");
  };

  handleDragLeave = () => {
    this.dragAreaRef.current.classList.remove("active");
  };

  handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      this.setState({ file }, this.displayFile);
    }
  };

  displayFile = () => {
    const { file } = this.state;
    if (!file) return;

    const validExtensions = ['image/jpeg', 'image/jpg', 'image/png'];

    if (validExtensions.includes(file.type)) {
      const fileReader = new FileReader();
      fileReader.onload = () => {
        this.dragAreaRef.current.innerHTML = `<img src="${fileReader.result}" alt="">`;
        this.submitButton.current.style.display = 'inline-block';
      };
      fileReader.readAsDataURL(file);
    } else {
      alert('This file is not an image.');
      this.dragAreaRef.current.textContent = 'Drag & Drop';
      this.dragAreaRef.current.classList.remove('active');
    }
  };

  handleTakePic = () => {
    this.or.current.style.display = 'none';
    this.picButton.current.style.display = 'none';
    this.popupBg.current.classList.add('open');
    this.popup.current.classList.add('open');

    const constraints = {
        audio: false,
        video: true
    };

    const handleSuccess = (stream) => {
        console.log("Camera stream received:", stream);
        window.stream = stream;

        if (this.video.current) {
            this.video.current.srcObject = stream;
            this.video.current.play();
        } else {
            console.error("Video element is not available yet.");
        }
    };

    const handleError = (error) => {
        console.error("Camera access error:", error.message);
        alert("Error accessing camera: " + error.message);
    };

    navigator.mediaDevices.getUserMedia(constraints)
        .then(handleSuccess)
        .catch(handleError);
};


handleCapture = () => {
  if (!this.video.current || !this.canvas.current) {
      console.error("Video or Canvas reference is not available");
      return;
  }

  this.canvas.current.width = this.video.current.videoWidth;
  this.canvas.current.height = this.video.current.videoHeight;
  const ctx = this.canvas.current.getContext('2d');

  if (ctx) {
      ctx.drawImage(this.video.current, 0, 0, this.canvas.current.width, this.canvas.current.height);
      const imageData = this.canvas.current.toDataURL('image/png');

      // Convert Base64 to File
      fetch(imageData)
          .then(res => res.blob())
          .then(blob => {
              const file = new File([blob], "captured_image.png", { type: "image/png" });
              this.setState({ file }, this.displayFile);
          });

      // Stop the camera stream
      if (this.video.current.srcObject) {
          const tracks = this.video.current.srcObject.getTracks();
          tracks.forEach(track => track.stop()); 
          this.video.current.srcObject = null; 
      }

      this.popupBg.current.classList.remove('open');
      this.popup.current.classList.remove('open');
  } else {
      console.error("Canvas context is not available");
  }
};



  handleSubmit = () => {
    const handleUpload = async () => {

        const formData = new FormData();
        formData.append('image', this.state.file);  // Ensure key matches backend

        try {
            const response = await axios.post('http://localhost:3001/uploadphoto', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            console.log('Upload success:', response.data);
            alert('Image uploaded successfully!');
        } catch (error) {
            console.error('Error uploading image:', error);
            alert('Upload failed.');
        }
    };

    handleUpload();
    this.submitButton.current.style.display = 'none';
    this.loadingGif();
  };

  loadingGif = () => {
    this.resultsContainerRef.current.innerHTML = `<img src="https://i.gifer.com/ZKZg.gif" alt="Loading..." class="img">`;
  };

  render() {
    console.log("rendering...")
    return (
      <>
      <Helmet>
        <meta charSet="UTF-8" />
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Human Tagging</title>
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/icon?family=Material+Icons"
        />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="true" />
        <link
          href="https://fonts.googleapis.com/css2?family=Economica:wght@400;700&family=Outfit:wght@100..900&family=Pacifico&display=swap"
          rel="stylesheet"
        />
        <link
          rel="stylesheet"
          href="https://unicons.iconscout.com/release/v4.0.0/css/line.css"
        />
        <link rel="stylesheet" href="styles.css" />
      </Helmet>

      <div className="split left">
        <div className="content">
          <div className="container">
            <h3>Who do you want to find?</h3>
            <div 
              className="drag-area" 
              ref={this.dragAreaRef} 
              onDragOver={this.handleDragOver} 
              onDragLeave={this.handleDragLeave} 
              onDrop={this.handleDrop}
            >
              <i className="material-icons">image</i>
              <span className="header"> Drag & Drop </span>
              <span className="header">
                or <span className="button" onClick={this.handleInputClick}>browse</span>
              </span>
              <input type="file" hidden ref={this.fileInputRef} onChange={this.handleFileChange}/>
              <span className="support">Supports: JPEG, JPG, PNG</span>
            </div>
            <span className="header1" ref={this.or}>OR</span> <button class="button2" ref={this.picButton} onClick={this.handleTakePic}>Take a Photo</button>
            <button class="button1" ref={this.submitButton} onClick={this.handleSubmit}>Submit</button>
          </div>
        </div>
      </div>

      <div className="split right">
        <div className="content">
          <div className="container1">
            <h2>Results...</h2>
            <div className="results-container" ref={this.resultsContainerRef}></div>
          </div>
        </div>
      </div>

      <div className="modal" ref={this.popup}>
        <div className="modal-inner">
          {/* <h2>Slide the puzzle to the correct spot</h2>
          <div className="img">
            <img src="test.png" alt="Puzzle" style={{ width: "405px" }} />
          </div>
          <div className="range">
            <input type="range" id="slider" min="0" max="250.4" value="0" step="0.1" />
          </div>
          <div className="val"></div> */}
          <video playsInline autoPlay ref={this.video}></video>
          <canvas ref={this.canvas}></canvas> 
          <button className="capture" ref={this.capture} onClick={this.handleCapture}>Capture</button>
        </div>
      </div>

      <div className="modal-bg" ref={this.popupBg}></div>
    </>
    )
  }
}

function App() {
  return (
    <HelmetProvider>
      <CustomerApp/>
    </HelmetProvider>
  );
}

export default App;