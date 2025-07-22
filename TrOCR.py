import os
import cv2
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

# Enable plotting for web display
ENABLE_PLOTTING = True


def plot_horizontal_projection(projection, output_path: str):
    """
    Save a plot of the horizontal projection profile.
    """
    plt.figure(figsize=(8, 4))
    plt.plot(projection, np.arange(len(projection)))
    plt.gca().invert_yaxis()
    plt.xlabel("Sum of inverted-binary pixels")
    plt.ylabel("Row index")
    plt.title("Horizontal Projection Profile")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


# MODIFIED: Added proj_output_path to the function signature
def segment_into_lines(image_path: str, height_ratio_threshold: float = 0.75, proj_output_path: str = None) -> list:
    """
    Segment the input image into text lines using horizontal projection.
    Returns a list of (PIL.Image, (x1, y1, x2, y2)).
    Accepts proj_output_path to save the projection plot with a specific filename.
    """
    image = cv2.imread(image_path)
    if image is None:
        return []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Compute and smooth projection
    projection = np.sum(thresh, axis=1)
    smoothed = gaussian_filter1d(projection, sigma=3)

    # Optionally save projection plot with the provided unique path
    if ENABLE_PLOTTING and proj_output_path:
        os.makedirs(os.path.dirname(proj_output_path), exist_ok=True)
        plot_horizontal_projection(smoothed, proj_output_path)

    # Identify segments where projection > threshold
    threshold = smoothed.max() * 0.2
    indices = np.where(smoothed > threshold)[0]
    if indices.size == 0:
        return []

    # Group consecutive indices into segments
    segments, start = [], int(indices[0])
    for i in range(1, len(indices)):
        if indices[i] > indices[i - 1] + 1:
            segments.append((start, indices[i - 1]))
            start = int(indices[i])
    segments.append((start, int(indices[-1])))

    # Filter by height deviation and crop
    heights = [y1 - y0 for y0, y1 in segments]
    mean_height = float(np.mean(heights)) if heights else 0
    h, w = thresh.shape
    results = []
    for y0, y1 in segments:
        height = y1 - y0
        if abs(height - mean_height) > height_ratio_threshold * mean_height:
            continue
        strip = thresh[y0:y1 + 1, :]
        cols = np.where(strip.sum(axis=0) > 0)[0]
        if cols.size == 0:
            continue
        x0, x1 = cols[0], cols[-1] + 1
        pad = max(10, height // 2)
        xa, ya = max(0, x0 - pad), max(0, y0 - pad)
        xb, yb = min(w, x1 + pad), min(h, y1 + pad)
        crop = image[ya:yb, xa:xb]
        if crop.size:
            pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
            results.append((pil_img, (xa, ya, xb, yb)))
    return results


def run_trOCR(image_input, processor, model, device) -> str:
    """
    Perform OCR on a PIL.Image or image path using TrOCR.
    """
    if isinstance(image_input, str):
        image = Image.open(image_input).convert('RGB')
    else:
        image = image_input
    inputs = processor(images=image, return_tensors='pt').pixel_values.to(device)
    generated_ids = model.generate(inputs, max_new_tokens=1000)
    return processor.batch_decode(generated_ids, skip_special_tokens=True)[0]