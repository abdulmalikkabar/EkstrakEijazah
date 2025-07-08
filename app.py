import os
import re
import shutil
from flask import Flask, request, send_file, render_template
from PyPDF2 import PdfReader, PdfWriter
from werkzeug.utils import secure_filename
from zipfile import ZipFile

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def extract_name_from_text(text):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "Dengan ini menyatakan bahwa" in line:
            if i + 1 < len(lines):
                name = lines[i + 1].strip()
                invalid_chars = r'<>:"/\\|?*'
                for ch in invalid_chars:
                    name = name.replace(ch, "")
                return name.replace(" ", "_")
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["pdf_file"]
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        shutil.rmtree(OUTPUT_FOLDER)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        reader = PdfReader(filepath)
        result_paths = []

        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            name = extract_name_from_text(text)
            if not name:
                name = f"halaman_{i+1}"
            output_path = os.path.join(OUTPUT_FOLDER, f"{name}.pdf")
            writer = PdfWriter()
            writer.add_page(page)
            with open(output_path, "wb") as f:
                writer.write(f)
            result_paths.append(output_path)

        zip_path = "hasil_ijazah.zip"
        with ZipFile(zip_path, "w") as zipf:
            for file_path in result_paths:
                zipf.write(file_path, os.path.basename(file_path))

        return send_file(zip_path, as_attachment=True)

    return render_template("index.html")
