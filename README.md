# Handwritten Text Recognition (HTR) Web Application

This repository hosts a robust web application designed for **Handwritten Text Recognition (HTR)**, leveraging state-of-the-art deep learning models and advanced image processing techniques. Users can upload handwritten image files and receive digitized text outputs, with features like dynamic text highlighting and a user-friendly interface.

-----

## ✨ Features

  * **Accurate HTR**: Utilizes **Microsoft TrOCR** (Transformer-based Optical Character Recognition) for highly accurate transcription of handwritten content.
  * **Image Preprocessing Pipeline**: Incorporates sophisticated image processing steps, including **binarization** and **horizontal projection profile analysis**, to robustly segment text lines from complex handwritten documents.
  * **User Authentication**: Secure user registration and login system, managing user sessions for personalized interactions.
  * **Interactive OCR Output**: Displays processed images with bounding boxes around detected text, along with searchable OCR text output.
  * **Dynamic Text Highlighting**: Real-time highlighting of search terms within the extracted text for enhanced readability and analysis.
  * **Dark Mode**: A toggleable dark mode interface for improved visual comfort.
  * **Responsive Web Design**: Ensures a seamless experience across various devices.
  * **Drag-and-Drop File Upload**: Convenient image submission via drag-and-drop or traditional file input.
  * **Performance Metrics**: Displays the processing time for each OCR operation.

-----

## 🛠️ Technologies Used

  * **Backend**:

      * **Flask**: A micro web framework for Python, used for routing, request handling, and rendering templates.
      * **PyTorch**: An open-source machine learning framework, providing the underlying tensor computations for the TrOCR model.
      * **Hugging Face Transformers**: Leverages pre-trained `TrOCRProcessor` and `VisionEncoderDecoderModel` for robust HTR capabilities.
      * **OpenCV (`cv2`)**: Employed for advanced image manipulation and preprocessing tasks, including image loading, thresholding, and drawing bounding boxes.
      * **NumPy**: Essential for numerical operations, particularly in image processing and horizontal projection calculations.
      * **SQLite3**: A lightweight, file-based database used for managing user credentials.
      * **Werkzeug Security**: For secure password hashing and checking.
      * **Waitress**: A production-quality pure-Python WSGI server.

  * **Frontend**:

      * **HTML5**: Structures the web content.
      * **CSS3**: Styles the application, including custom themes and responsive design.
      * **JavaScript**: Handles client-side interactivity, dynamic content updates, and user experience enhancements.

-----

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

  * Python 3.8+
  * `pip` (Python package installer)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/LongIsHandsome/trocr-webapp.git
    cd trocr-webapp
    ```

2.  **Create a virtual environment** (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    ```

3.  **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database:**
    The `app.py` script automatically initializes the SQLite database and creates the `users` table on startup using `create.sql`.

-----

## 🏃 Running the Application

To run the Flask application:

```bash
python app.py
```

The application will typically be accessible at `http://127.0.0.1:5000/`.

-----

## 📈 OCR Process Explained

The core of this application lies in its OCR pipeline, particularly the `TrOCR.py` module which orchestrates the following sequential image processing and recognition steps:

1.  **Image Loading and Grayscale Conversion**: The input handwritten image is initially loaded using `cv2.imread` and then converted from its original color format (e.g., BGR) to a single-channel **grayscale** image using `cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)`. Grayscale conversion simplifies subsequent processing by reducing dimensionality.

2.  **Binarization via Otsu's Method**: The grayscale image undergoes **binarization**, a critical step to convert it into a binary (black and white) image. This application specifically employs **Otsu's method** (`cv2.THRESH_OTSU`). Otsu's method automatically determines an optimal global threshold value by minimizing the intra-class variance of the foreground and background pixels. This robust statistical approach effectively separates text (foreground) from the document background, resulting in a cleaner image for analysis. The image is also inverted (`cv2.THRESH_BINARY_INV`) so that text pixels are white on a black background, which is often preferred for projection-based analysis.

3.  **Horizontal Projection Profile Generation**: A **horizontal projection profile** is computed by summing the pixel intensities along each row of the binarized image (`np.sum(thresh, axis=1)`). This profile is a 1D array where each element represents the total number of white (text) pixels in that row. Peaks in this profile indicate regions of text, while valleys suggest spaces between text lines.

4.  **Noise Reduction with Gaussian Filter**: To smooth the horizontal projection profile and reduce spurious noise that might lead to erroneous line segmentation, a **Gaussian filter** (`gaussian_filter1d`) is applied. The Gaussian filter is a linear smoothing filter that uses a Gaussian function to calculate the transformation of each pixel. In this context, it blurs the projection profile, making the peaks and valleys more distinct and less susceptible to minor pixel variations, thereby improving the accuracy of line detection.

5.  **Text Line Segmentation**: By analyzing the smoothed horizontal projection profile, the `segment_into_lines` function precisely identifies and segments the image into individual text lines. This process typically involves detecting significant valleys (low pixel sums) that correspond to the spaces between lines. The segmented regions are then cropped from the original image.

6.  **TrOCR Model Inference**: Each segmented text line, now an individual image, is prepared for inference. It is converted to a PIL Image object and then processed by the `TrOCRProcessor` and fed into the pre-trained **Microsoft TrOCR** (`VisionEncoderDecoderModel`). TrOCR, a state-of-the-art Transformer-based model, treats OCR as an image-to-text sequence generation task, leveraging the power of attention mechanisms to transcribe handwritten content with high accuracy.

7.  **Result Aggregation and Annotation**: The transcribed text from each line is aggregated to form the complete OCR output for the document. Concurrently, the original image is annotated with **bounding boxes** (`cv2.rectangle`) around the detected text lines, visually representing the segmentation and recognition areas. Both the annotated image and the extracted textual content are then prepared for display on the web interface.

-----

## 🔗 GitHub Repository

This project is open-source and available on GitHub:
[LongIsHandsome/trocr-webapp](https://www.google.com/search?q=https://github.com/LongIsHandsome/trocr-webapp)

-----

## Acknowledgments

  * The TrOCR model is provided by Microsoft and accessible through the Hugging Face Transformers library.
  * Some of the UI components are adapted from [Uiverse](https://uiverse.io/).

-----

## Credit

  * This project is vibe-coded with ChatGPT 4o-mini and Gemini 2.5 Flash and Pro.
  * This README file is generated by Google Gemini 2.5 Flash.