from flask import Flask, flash, request, redirect, jsonify
from PIL import Image
from io import BytesIO
import base64
from test import stylize


def from_base64(base64_str):
    plain_text = str(base64_str).split(",")[1]
    byte_data = base64.b64decode(plain_text)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    return img


def to_base64(img):
    im_file = BytesIO()
    img.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()
    im_b64 = base64.b64encode(im_bytes).decode()
    data_uri = 'data:image/jpeg;base64,{}'.format(im_b64)
    return data_uri


app = Flask(__name__)


@app.route('/', methods=['POST'])
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
    return

# if __name__ == '__main__':
#     app.run(debug=True)