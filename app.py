from flask import Flask, flash, request, redirect, jsonify
from PIL import Image
from io import BytesIO
import base64
from test import stylize


def from_base64(base64_str):
    byte_data = base64.b64decode(base64_str)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    return img


def to_base64(img):
    im_file = BytesIO()
    img.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()
    im_b64 = base64.b64encode(im_bytes)
    return im_b64


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def style_transfer():
    if request.method == 'POST':
        if 'content' and 'style' not in request.files:
            flash('No file part')
            return redirect(request.url)
        base64_content = request.files['content'].read()
        base64_style = request.files['style'].read()

        content_img = from_base64(base64_content)
        style_img = from_base64(base64_style)

        out_img = stylize(content_img, style_img)
        out_base64 = to_base64(out_img)

        return jsonify({'image': str(out_base64)})
    return '''
        <!doctype html>
        <title>Make your own painting</title>
        <h1>Upload a content and a style image</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=content>
          <input type=file name=style>
          <input type=submit value=Upload>
        </form>
        '''