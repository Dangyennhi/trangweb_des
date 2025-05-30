from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
from werkzeug.utils import secure_filename
import os
import io

app = Flask(__name__)
app.secret_key = "secret"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def pad(data):
    pad_len = 8 - len(data) % 8
    return data + bytes([pad_len] * pad_len)

def unpad(data):
    return data[:-data[-1]]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        key = request.form.get("key", "").encode()
        if len(key) != 8:
            flash("Khóa DES phải dài đúng 8 ký tự!", "error")
            return redirect(url_for("index"))

        file = request.files.get("file")
        if not file:
            flash("Bạn cần chọn file để mã hóa/giải mã!", "error")
            return redirect(url_for("index"))

        operation = request.form.get("operation")
        filename = secure_filename(file.filename)
        data = file.read()

        if operation == "encrypt":
            cipher = DES.new(key, DES.MODE_CBC)
            encrypted = cipher.encrypt(pad(data))
            out_data = cipher.iv + encrypted
            out_name = f"encrypted_{filename}.bin"
        elif operation == "decrypt":
            iv = data[:8]
            encrypted = data[8:]
            cipher = DES.new(key, DES.MODE_CBC, iv=iv)
            out_data = unpad(cipher.decrypt(encrypted))
            out_name = f"decrypted_{filename}"
        else:
            flash("Lỗi: Chưa chọn thao tác.", "error")
            return redirect(url_for("index"))

        return send_file(
            io.BytesIO(out_data),
            as_attachment=True,
            download_name=out_name,
            mimetype="application/octet-stream"
        )
    return render_template("index.html")
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)