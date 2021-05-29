from PIL import Image
from pathlib import Path
import os
from style_transfer.core.monero import Monero
path = Path(__file__).parent

# Monero only need two images to work with
# a content image where the style will be applyed
# a style image from where the style will be learned
content = Image.open(os.path.join(path, 'images/inputs/download.jpg'))
style1 = Image.open(os.path.join(path, 'images/inputs/asheville.jpg'))
style2 = Image.open(os.path.join(path, 'images/inputs/la_muse.jpg'))
style3 = Image.open(os.path.join(path, 'images/inputs/woman_with_hat_matisse.jpg'))

# create an instance of Monero
artist = Monero()
# load model and weights from HD
artist.load_model()

alpha = 0.1
# create as many paintings as you want
# you can adjust preserve_color (True or False) and alpha (0 <= alpha <= 1) arguments
painting1 = artist.create_painting(content, style1, preserve_color=False, alpha=alpha, content_new_size=0, style_new_size=0)
painting1.save(os.path.join(path, 'images/outputs/gwei_style1_a_{}.jpg'.format(alpha)))

painting2 = artist.create_painting(content, style2, preserve_color=False, alpha=alpha, content_new_size=0, style_new_size=0)
painting2.save(os.path.join(path, 'images/outputs/gwei_style2_a_{}.jpg'.format(alpha)))

painting3 = artist.create_painting(content, style3, preserve_color=False, alpha=alpha, content_new_size=0, style_new_size=0)
painting3.save(os.path.join(path, 'images/outputs/gwei_style3_a_{}.jpg'.format(alpha)))
