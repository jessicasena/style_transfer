from flask import Flask, flash, request, redirect, jsonify
from PIL import Image
from io import BytesIO
import base64
from core.monero import Monero
from distutils.util import strtobool


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


@app.route('/', methods=['GET', 'POST'])
def style_transfer():
    if request.method == 'POST':
        json = request.json
        base64_content = json['content']
        base64_style = json['style']
        p_c = str(json['preserve_color'])
        preserve_color = strtobool(p_c)
        alpha = float(json['alpha'])

        content_img = from_base64(base64_content)
        style_img = from_base64(base64_style)

        artist = Monero()
        artist.load_model()

        painting = artist.create_painting(content_img, style_img, preserve_color=preserve_color, alpha=alpha,
                                          content_new_size=512, style_new_size=512,)
        out_base64 = to_base64(painting)

        return jsonify({'image': str(out_base64)})
    return '''
           <!doctype html>
           <title>Make your own painting</title>
           '''


if __name__ == '__main__':
    app.run(debug=True)
