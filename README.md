# Handwritten Text Recognition (HTR) Application

This project is a web-based application for **Handwritten Text Recognition (HTR)**, allowing users to upload images containing handwritten text and obtain the extracted digital text. It utilizes the **TrOCR (Transformer-based Optical Character Recognition)** model for accurate text recognition and includes image processing steps for line segmentation and visualization.

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

## Technologies Used

  * **Backend**:
      * **Python**: The core programming language.
      * **Flask**: Web framework for handling requests and rendering templates.
      * **PyTorch**: Deep learning framework for running the TrOCR model.
      * **Hugging Face Transformers**: Library for easily loading and using pre-trained TrOCR models.
      * **OpenCV (cv2)**: For image processing tasks like thresholding and drawing annotations.
      * **Pillow (PIL)**: For image manipulation.
      * **Numpy**: For numerical operations, especially in image processing.
      * **SciPy**: Used for Gaussian filtering in horizontal projection.
      * **Matplotlib**: For plotting the horizontal projection profile.
      * **Waitress**: Production-ready WSGI server.
  * **Frontend**:
      * **HTML5**: Structure of the web page.
      * **CSS3**: Styling of the application, including a loading animation.
      * **JavaScript**: For interactive elements like file preview, drag-and-drop, search functionality, and loading indicators.

## Setup and Installation

Follow these steps to set up and run the project locally:

### 1\. Clone the Repository

```bash
git clone <repository_url>
cd <repository_directory>
```

### 2\. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3\. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4\. Run the Application

#### Development Mode (for testing)

```bash
python app.py
```

This will start the Flask development server, usually accessible at `http://0.0.0.0:5000/`.

#### Production Mode (using Waitress)

For a more robust deployment, use Waitress:

```bash
serve(app, host="0.0.0.0", port=5000)
```

This line is already present in `app.py` within the `if __name__ == "__main__":` block, so simply running `python app.py` will use Waitress for production-like deployment if the `app.run` line is commented out.

## Usage

1.  **Open your web browser** and navigate to the address where the application is running (e.g., `http://localhost:5000`).
2.  **Upload an Image**:
      * Click the "Drop files here or click to upload" area.
      * Alternatively, drag and drop an image file into the designated area.
      * An image preview will appear.
3.  **Click "Upload"**: The application will process the image. A loading animation will be displayed along with a timer indicating the processing duration.
4.  **View Results**:
      * **Processing Time**: The time taken for OCR will be displayed.
      * **Annotated Image**: The original image with bounding boxes around detected text lines will be shown.
      * **Projection Plot**: A graph illustrating the horizontal projection profile used for line segmentation will be displayed.
      * **Extracted Text**: The recognized handwritten text will appear in a dedicated section.
5.  **Search Text**: Use the "Search text..." input field above the extracted text to find specific words or phrases within the OCR output. Matching text will be highlighted.

## Project Structure

```
.
├── app.py              # Flask application, handles routes, OCR logic, and image processing.
├── TrOCR.py            # Contains core OCR functions (segmentation, TrOCR execution).
├── static/
│   ├── style.css       # Stylesheets for the web application.
│   └── script.js       # JavaScript for client-side interactions (file handling, search).
├── templates/
│   └── index.html      # HTML template for the main page.
└── uploads/            # Directory for temporarily storing uploaded images.
└── README.md           # This README file.
```

## Code Overview

### `app.py`

  * Initializes the Flask app, defines upload folder, and loads the TrOCR processor and model.
  * The `index()` route handles both GET and POST requests.
  * On POST, it saves the uploaded image, calls `segment_into_lines` to get text line crops, runs `run_trOCR` on each line, annotates the original image with bounding boxes, encodes images for display, and cleans up temporary files.
  * Renders `index.html` with OCR results, annotated image data, projection plot data, and processing time.

### `TrOCR.py`

  * `plot_horizontal_projection(projection, output_path)`: Saves a plot of the horizontal projection profile of the image.
  * `segment_into_lines(image_path, height_ratio_threshold)`:
      * Reads an image, converts it to grayscale, and applies Otsu's thresholding to create a binary inverted image.
      * Computes the horizontal projection (sum of black pixels per row).
      * Applies Gaussian smoothing to the projection profile.
      * Identifies segments (potential text lines) where the smoothed projection exceeds a threshold.
      * Filters segments based on height deviation from the mean to refine line detection.
      * Crops each detected line from the original image and returns a list of PIL Images along with their bounding box coordinates.
  * `run_trOCR(image_input, processor, model, device)`:
      * Takes a PIL Image or image path.
      * Processes the image using the TrOCR processor.
      * Generates text using the TrOCR model.
      * Decodes the generated IDs back into human-readable text.

### `static/script.js`

  * Handles client-side logic for file input:
      * Displays selected file name and image preview.
      * Implements drag-and-drop functionality for image uploads.
      * Manages the loading overlay with a processing timer during image submission.
      * Clears previous results when a new image is selected.
  * Implements the search functionality for the extracted OCR text, dynamically highlighting matches.

### `static/style.css`

  * Provides the styling for the web interface, including responsive design, custom file upload area, results display, and the hamster-wheel loading animation.

### `templates/index.html`

  * The main HTML template that defines the structure of the web page.
  * Includes elements for file upload, image preview, and display areas for the annotated image, projection plot, and OCR text.
  * Uses Jinja2 templating to dynamically display results from the Flask backend.

## Acknowledgments

  * The TrOCR model is provided by Microsoft and accessible through the Hugging Face Transformers library.
  * Some of the UI components are adapted from [Uiverse](https://uiverse.io/).

## Credit
- This project is vibe-coded with ChatGPT o4-mini and Gemini 2.5 Flash and Pro.

- This README file is generated by Google Gemini 2.5 Flash.

# Time spent
$3$ days