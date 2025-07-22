import os
import base64
import cv2
import time
import torch
from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.utils import secure_filename
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, logging as tr_logging
from TrOCR import segment_into_lines, run_trOCR
from waitress import serve
import logging
import uuid # Import uuid for unique filenames
from functools import wraps
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Configure global logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
# Turn on waitress logs
logging.getLogger("waitress").setLevel(logging.INFO)
logging.getLogger("waitress").propagate = True

# Suppress transformer warnings
tr_logging.set_verbosity_error()

# Flask setup
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set a secret key for session management
app.secret_key = str(uuid.uuid4())
app.logger.info(f"Flask secret key set: {app.secret_key}")

# Database setup
DATABASE = os.path.join(BASE_DIR, 'database.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        with open('create.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()
        db.close()

# Initialize the database on startup
with app.app_context():
    init_db()

# Model initialization
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_NAME = "microsoft/trocr-large-handwritten"
processor = TrOCRProcessor.from_pretrained(MODEL_NAME)
model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME)
model.to(DEVICE)
app.logger.info(f"Model loaded on {DEVICE}")

ALLOWED_EXT = {"png", "jpg", "jpeg", "bmp"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        db = get_db()
        try:
            db.execute("INSERT INTO users (username, hashed_password) VALUES (?, ?)", (username, hashed_password))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            # Username already exists
            return render_template("register.html", error_message="Username already taken. Please choose another.")
        finally:
            db.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    
    error_message = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        db.close()

        if user and check_password_hash(user["hashed_password"], password):
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            # Invalid credentials
            error_message = "Invalid username or password."
            
    return render_template("login.html", error_message=error_message)

@app.route("/logout")
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    ocr_text = None
    img_data = None
    proj_data = None
    elapsed = None
    error_message = None

    username = session.get('username', 'UnknownUser')

    if request.method == "POST":
        file = request.files.get("image")
        if file and allowed_file(file.filename):
            # Generate a unique ID for this session/upload to prevent race conditions
            unique_id = str(uuid.uuid4())
            original_filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}_{original_filename}")
            file.save(filepath)

            # Construct unique filename for the horizontal projection plot
            proj_plot_filename = f"{unique_id}_hpp.png"
            proj_path = os.path.join(app.config["UPLOAD_FOLDER"], proj_plot_filename)

            app.logger.info(f"[{username}] Image processing started for: {original_filename} (unique ID: {unique_id})")
            start = time.time()
            # Pass the unique projection plot path to segment_into_lines
            lines = segment_into_lines(filepath, proj_output_path=proj_path)
            
            # Annotate lines
            img = cv2.imread(filepath)
            texts = []
            colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,255,255),(255,0,255)]
            for i, (line_img, (x1, y1, x2, y2)) in enumerate(lines):
                txt = run_trOCR(line_img, processor, model, DEVICE)
                texts.append(txt)
                cv2.rectangle(img, (x1, y1), (x2, y2), colors[i % len(colors)], 2)
            elapsed = round(time.time() - start, 2)
            app.logger.info(f"[{username}] Image processing finished for: {original_filename}. Processed time: {elapsed} seconds.")

            # Encode annotated image
            _, buf = cv2.imencode(".png", img)
            img_data = base64.b64encode(buf).decode()

            # Load and remove unique projection plot
            if os.path.exists(proj_path):
                with open(proj_path, "rb") as f:
                    proj_data = base64.b64encode(f.read()).decode()
                os.remove(proj_path) # Delete the unique plot file

            ocr_text = "\n".join(texts)
            os.remove(filepath) # Delete the unique uploaded image file
        elif file:
            error_message = "Only support PNG, JPG, JPEG, BMP file types."
            app.logger.warning(f"[{username}] Invalid file type uploaded: {file.filename}")
        else:
            error_message = "No file selected or an unexpected error occurred."
            app.logger.error(f"[{username}] No file selected or upload error.")


    return render_template("index.html",
                           ocr_text=ocr_text,
                           img_data=img_data,
                           proj_data=proj_data,
                           elapsed=elapsed,
                           error_message=error_message)

if __name__ == "__main__":
    # development
    # app.run(debug=True, host="0.0.0.0")

    # production
    serve(app, host="0.0.0.0", port=5000)