import os
import base64
import cv2
import time
import torch
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, logging
from TrOCR import segment_into_lines, run_trOCR

# Suppress transformer warnings
logging.set_verbosity_error()

# Flask setup
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Model initialization
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_NAME = "microsoft/trocr-large-handwritten"
processor = TrOCRProcessor.from_pretrained(MODEL_NAME, use_fast=True)
model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME)
model.to(DEVICE)
print(f"Model loaded on {DEVICE}")

ALLOWED_EXT = {"png", "jpg", "jpeg", "bmp"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@app.route("/", methods=["GET", "POST"])
def index():
    ocr_text = None
    img_data = None
    proj_data = None
    elapsed = None

    if request.method == "POST":
        file = request.files.get("image")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            start = time.time()
            lines = segment_into_lines(filepath)
            # Annotate lines
            img = cv2.imread(filepath)
            texts = []
            colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,255,255),(255,0,255)]
            for i, (line_img, (x1, y1, x2, y2)) in enumerate(lines):
                txt = run_trOCR(line_img, processor, model, DEVICE)
                texts.append(txt)
                cv2.rectangle(img, (x1, y1), (x2, y2), colors[i % len(colors)], 2)
            elapsed = round(time.time() - start, 2)

            # Encode annotated image
            _, buf = cv2.imencode(".png", img)
            img_data = base64.b64encode(buf).decode()

            # Load and remove projection plot
            proj_path = os.path.join(UPLOAD_FOLDER, "hpp.png")
            if os.path.exists(proj_path):
                with open(proj_path, "rb") as f:
                    proj_data = base64.b64encode(f.read()).decode()
                os.remove(proj_path)

            ocr_text = "\n".join(texts)
            os.remove(filepath)

    return render_template("index.html",
                           ocr_text=ocr_text,
                           img_data=img_data,
                           proj_data=proj_data,
                           elapsed=elapsed)

if __name__ == "__main__":
    app.run(debug=False)