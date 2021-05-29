from PIL import Image
import os
from core.monero import Monero
import sys
import time

path_content = sys.argv[1]
path_style = sys.argv[2]
preserve_color = int(sys.argv[3])
alpha = float(sys.argv[4])
content_new_size = int(sys.argv[5])
style_new_size = int(sys.argv[6])

content_name = os.path.split(path_content)[-1].split(".")[0]
style_name = os.path.split(path_style)[-1].split(".")[0]
output_name = content_name + "_" + style_name


# Monero only need two images to work with
# a content image where the style will be applyed
# a style image from where the style will be learned
content = Image.open(path_content)
style1 = Image.open(path_style)

# create an instance of Monero
artist = Monero()
# load model and weights from HD
artist.load_model()

# create as many paintings as you want
# you can adjust preserve_color (True or False) and alpha (0 <= alpha <= 1) arguments
painting1 = artist.create_painting(content, style1, preserve_color, alpha, content_new_size, style_new_size)
painting1.save(os.path.join('./images/outputs', '{}_a_{}_p{}_{}.png'.format(output_name, alpha, preserve_color, time.time())))

