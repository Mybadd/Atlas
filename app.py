import os
import uuid
import json
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS

from pipeline.step_processor import load_step, export_svg_view, get_view_configs
from pipeline.image_styler import svg_to_image, apply_style, add_title_block, save_image

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {".step", ".stp"}


def allowed_file(filename):
    return os.path.splitext(filename.lower())[1] in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/views", methods=["GET"])
def list_views():
    """Return available view modes."""
    return jsonify(get_view_configs())


@app.route("/upload", methods=["POST"])
def upload_file():
    """Accept a STEP file upload and return a temp filename."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file. Please upload a .step or .stp file."}), 400

    unique_name = f"{uuid.uuid4().hex}{os.path.splitext(file.filename)[1]}"
    save_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(save_path)

    return jsonify({
        "success": True,
        "filename": unique_name,
        "original_name": file.filename,
    })


@app.route("/process", methods=["POST"])
def process_file():
    """Run the full pipeline: STEP → SVG → PNG/JPEG."""
    data = request.get_json()
    filename = data.get("filename")
    view = data.get("view", "isometric")
    fmt = data.get("format", "png").lower()
    style = data.get("style", "technical")
    title = data.get("title", "Technical Illustration")
    callout = data.get("callout", "")

    if not filename:
        return jsonify({"error": "No filename provided"}), 400

    step_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(step_path):
        return jsonify({"error": "File not found. Please upload again."}), 404

    try:
        # Step 1: Load STEP file
        shape = load_step(step_path)

        # Step 2: Export to SVG
        svg_name = f"{os.path.splitext(filename)[0]}_{view}.svg"
        svg_path = os.path.join(OUTPUT_FOLDER, svg_name)
        export_svg_view(shape, svg_path, view=view)

        # Step 3: Convert SVG → PIL Image
        img = svg_to_image(svg_path, width=1200)

        # Step 4: Apply visual style
        img = apply_style(img, style=style)

        # Step 5: Add title block
        img = add_title_block(img, title=title, view=view, style=style, callout=callout)

        # Step 6: Save as PNG or JPEG
        ext = "jpg" if fmt in ("jpg", "jpeg") else "png"
        out_name = f"{os.path.splitext(filename)[0]}_{view}_{style}.{ext}"
        out_path = os.path.join(OUTPUT_FOLDER, out_name)
        save_image(img, out_path, fmt=ext)

        return jsonify({
            "success": True,
            "output_file": out_name,
            "download_url": f"/download/{out_name}",
            "preview_url": f"/download/{out_name}",
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/<filename>")
def download_file(filename):
    """Serve a generated output image."""
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    mime = "image/jpeg" if filename.lower().endswith((".jpg", ".jpeg")) else "image/png"
    return send_file(file_path, mimetype=mime, as_attachment=False)


if __name__ == "__main__":
    print("=" * 55)
    print("  STEP -> PNG/JPEG Illustration Generator")
    print("  Open: http://localhost:5000")
    print("=" * 55)
    app.run(debug=True, port=5000)
