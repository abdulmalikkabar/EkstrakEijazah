import os
import re
import shutil
from flask import Flask, request, send_file, render_template_string
from PyPDF2 import PdfReader, PdfWriter
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head><title>Upload Ijazah</title></head>
<body>
  <h2>Upload File PDF Ijazah</h2>
  <form action="/" method="post" enctype="multipart/form-data">
    <input type="file" name="pdf_file" required><br><br>
    <button type="submit">Proses PDF</button>
  </form>
</body>
</html>
'''

def extract_name_from_text(text):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "Dengan ini menyatakan bahwa" in line:
            if i + 1 < len(lines):
                name = lines[i + 1].strip()
                # Hapus karakter tidak valid
                invalid_chars = r'<>:"/\|?*'
                for ch in invalid_chars:
                    name = name.replace(ch, "")
                name = name.replace("\n", " ").replace("\r", " ").strip()
                return name.replace(" ", "_")
    return None

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        uploaded_file = request.files["pdf_file"]
        filename = secure_filename(uploaded_file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        uploaded_file.save(filepath)

        shutil.rmtree(OUTPUT_FOLDER)
        os.makedirs(OUTPUT_FOLDER)

        reader = PdfReader(filepath)
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

        shutil.make_archive("hasil_ijazah", "zip", OUTPUT_FOLDER)
        return send_file("hasil_ijazah.zip", as_attachment=True)

    return render_template_string(HTML_FORM)

if __name__ == "__main__":
    app.run(debug=True)
