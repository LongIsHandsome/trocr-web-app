# Handwritten Text Recognition (HTR) Application

This project is a web-based application for **Handwritten Text Recognition (HTR)**, allowing users to upload images containing handwritten text and obtain the extracted digital text. It utilizes the **TrOCR (Transformer-based Optical Character Recognition)** model for accurate text recognition and includes image processing steps for line segmentation and visualization.

**GitHub Repository**: [https://github.com/LongIsHandsome/trocr-webapp](https://github.com/LongIsHandsome/trocr-webapp)

## Features

* **Upload Images**: Easily upload handwritten image files (PNG, JPG, JPEG, BMP).
* **Automatic Line Segmentation**: The application automatically segments the uploaded image into individual text lines using horizontal projection.
* **TrOCR Integration**: Leverages the `microsoft/trocr-large-handwritten` model for high-accuracy handwritten text recognition.
* **Annotated Image Output**: Displays the uploaded image with detected text lines highlighted by bounding boxes.
* **Horizontal Projection Profile Plot**: Visualizes the horizontal projection profile used for line segmentation.
* **Extracted Text Display**: Shows the recognized text, organized by lines.
* **Search Functionality**: Allows searching within the extracted text with highlighting.
* **Processing Time Indicator**: Provides feedback on how long the OCR process takes.
* **Responsive and User-Friendly Interface**: Built with Flask and a clean, modern front-end design.

---

## Technologies Used

* **Backend**:
    * **Python**: The core programming language.
    * **Flask**: A micro web framework for the backend API.
    * **Transformers (Hugging Face)**: For loading and using the TrOCR model.
    * **PyTorch**: The deep learning framework underlying the TrOCR model.
    * **OpenCV (`cv2`)**: For image processing tasks like loading, grayscale conversion, thresholding, and drawing annotations.
    * **Pillow (PIL)**: For image manipulation, especially converting between OpenCV and PIL formats.
    * **Numpy**: For numerical operations, particularly in image processing.
    * **Matplotlib**: For generating the horizontal projection profile plot.
    * **Waitress**: A production-quality pure-Python WSGI server.
* **Frontend**:
    * **HTML5**: Structure of the web pages.
    * **CSS3**: Styling and responsive design.
    * **JavaScript**: Client-side interactivity, including file upload handling, drag-and-drop, loading animations, and search functionality.
* **Deployment**:
    * **Docker**: For containerizing the application, ensuring consistent environments and easy deployment.
    * **Docker Compose**: For defining and running multi-container Docker applications (though currently, it defines a single service).

---

## Core OCR Logic Explained

### 1. Overall Workflow

When a user uploads an image, the application follows these high-level steps:

1.  **Image Pre-processing**: The uploaded image undergoes transformations to enhance text clarity.
2.  **Line Segmentation**: The pre-processed image is analyzed to separate individual lines of text.
3.  **Optical Character Recognition (OCR)**: Each segmented line is fed to the TrOCR deep learning model for recognition.
4.  **Result Aggregation & Display**: Recognized text from all lines is combined, and the original image is annotated with bounding boxes, then displayed to the user.

<br>

### 2. Image Pre-processing for Line Segmentation

Before line identification, the image is cleaned and prepared. This occurs in the `segment_into_lines` function within `TrOCR.py`:

* **Grayscale Conversion**: The input image is converted to **grayscale** (`cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)`). This simplifies the image, focusing on intensity rather than color.
* **Otsu's Method (Binarization)**: The grayscale image is then **binarized**, turning each pixel into pure black (0) or pure white (255). **Otsu's method** automatically finds the optimal threshold by minimizing variance between foreground (text) and background pixels, adapting to varying conditions. `cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)` applies this, with `THRESH_BINARY_INV` ensuring text pixels are white for subsequent projection. 

<br>

### 3. Horizontal Projection Profile (HPP) and Gaussian Filtering

The HPP is critical for identifying spaces between text lines:

* **Generating the HPP**: For each row of the binarized image, pixel values (0 or 255) are summed. Rows with text (white pixels) yield higher sums, while white spaces between lines yield lower sums. This creates a 1D array representing pixel sum per row: `projection = np.sum(thresh, axis=1)`. 
* **Gaussian Filter**: To reduce noise and make peaks/valleys more distinct, a **Gaussian filter** is applied to smooth the HPP. This averages local variations using a bell-shaped curve, improving the robustness of gap detection. `projection = gaussian_filter1d(projection.astype(float), sigma=3)` performs this smoothing.

<br>

### 4. Line Segmentation

Using the smoothed HPP, individual text lines are precisely segmented:

* **Identifying Valleys**: The core idea is to find "valleys" in the HPP, which correspond to horizontal blank spaces between text lines, indicating low text density.
* **Thresholding the Profile**: A threshold is applied to distinguish text-dense areas from inter-line spaces.
* **Grouping and Cropping**: Continuous regions of high projection values are grouped as potential text lines. The original image is then cropped for each identified line, and their bounding box coordinates are recorded.
* **Filtering by Height**: Segments are filtered by height to discard noise or artifacts, ensuring only plausible text lines are passed to the OCR model.

<br>

### 5. TrOCR Model Inference

Finally, the text recognition occurs:

* **Model Loading**: `app.py` loads the pre-trained `microsoft/trocr-large-handwritten` model and processor from Hugging Face. The model automatically moves to "cuda" (GPU) if available, or defaults to "cpu" for faster inference.
* **Per-Line Processing**: Each segmented line image is passed to the `run_trOCR` function.
* **TrOCR Processor**: The `TrOCRProcessor` (combining a tokenizer and feature extractor) prepares the image by resizing, normalizing, and converting it to the model's required format.
* **TrOCR Model**: The prepared features are fed into the `VisionEncoderDecoderModel`. This model's **Encoder** (a Vision Transformer) extracts visual features, and its **Decoder** (a Transformer-based language model) generates the corresponding text sequence.
* **Text Decoding**: The model outputs token IDs, which the `TrOCRProcessor` decodes into human-readable text strings.

This modular pipeline efficiently handles image preparation and accurate handwritten text recognition using a powerful deep learning model.

---

## Getting Started

Follow these instructions to set up and run the project locally using Docker.

### Prerequisites

* [**Docker Desktop**](https://www.docker.com/products/docker-desktop) (for Windows/macOS) or [**Docker Engine**](https://docs.docker.com/engine/install/) (for Linux) installed on your machine.
    * If you have an NVIDIA GPU and want to enable GPU acceleration, ensure you have the latest NVIDIA drivers and the [**NVIDIA Container Toolkit**](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) (for Linux) or [**WSL2 with NVIDIA WSL drivers**](https://developer.nvidia.com/cuda/wsl) (for Windows) properly configured.

### Installation and Running

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/LongIsHandsome/trocr-webapp.git
    cd trocr-webapp
    ```

2.  **Build and Run with Docker Compose:**
    Navigate to the root directory of your project where the `docker-compose.yml` and `Dockerfile` are located.

    ```bash
    docker compose up --build -d
    ```
    * The `--build` flag tells Docker Compose to build the image first.
    * The `-d` flag runs the container in detached mode (in the background).

    **Note on GPU:** If you have an NVIDIA GPU and wish to use it, ensure the `deploy` section is uncommented in `docker-compose.yml`. If you **do not** have an NVIDIA GPU, ensure that section is commented out to avoid errors. The application will automatically fall back to CPU if a GPU is not detected or configured.

3.  **Access the Application:**
    Once the container is running, open your web browser and navigate to:
    ```
    http://localhost:5000
    ```

---

## Project Structure

* `app.py`: The main Flask application file. It handles image uploads, calls the TrOCR model, processes results, and serves the web interface.
* `TrOCR.py`: Contains utility functions for image processing, such as horizontal projection for line segmentation and the `run_trOCR` function for performing OCR with the TrOCR model.
* `requirements.txt`: Lists all Python dependencies required by the project.
* `Dockerfile`: Defines the Docker image for the application, including dependencies and setup instructions.
* `docker-compose.yml`: Defines how to build and run the application services using Docker Compose.
* `static/`:
    * `script.js`: Client-side JavaScript for interactive elements, including file handling, drag-and-drop, and search functionality.
    * `style.css`: Cascading Style Sheets for the application's visual design.
* `templates/`:
    * `index.html`: The main HTML template for the web interface.
* `uploads/` (created at runtime): A directory to temporarily store uploaded images.
* `.gitignore`: Specifies files and directories to be ignored by Git.
* `README.md`: This file.

---

## Acknowledgments

* The TrOCR model is provided by Microsoft and accessible through the Hugging Face Transformers library.
* Some of the UI components are adapted from [Uiverse](https://uiverse.io/).

---

## Credit

* This project is vibe-coded with ChatGPT 4o-mini and Gemini 2.5 Flash and Pro.
* This README file is generated by Google Gemini 2.5 Flash.