from flask import Flask, request, render_template, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import io

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff'}

app = Flask(__name__)
app.secret_key = 'replace-this-with-a-secret-key'  # 建议用环境变量替代

def allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    files = request.files.getlist('photos')
    if not files or all(f.filename == '' for f in files):
        flash('请至少选择一张图片。')
        return redirect(url_for('index'))

    images = []
    for f in files:
        if f and allowed(f.filename):
            try:
                img = Image.open(f.stream)
                img = ImageOps.exif_transpose(img).convert('RGB')  # 自动旋转
                images.append(img)
            except Exception as e:
                flash(f'无法处理 {secure_filename(f.filename)}: {e}')
                return redirect(url_for('index'))
        else:
            flash(f'不支持的文件类型: {f.filename}')
            return redirect(url_for('index'))

    pdf_io = io.BytesIO()
    images[0].save(pdf_io, format='PDF', save_all=True, append_images=images[1:])
    pdf_io.seek(0)
    return send_file(pdf_io, as_attachment=True, download_name='photos_merged.pdf')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
