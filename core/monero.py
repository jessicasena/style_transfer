import torch
import torch.nn as nn
from pathlib import Path
from torchvision import transforms
from core import net
from core.utils import adaptive_instance_normalization, coral


class Monero:
    def __init__(self):
        self.vgg_model = Path(__file__).parent / "../models/vgg.pth"
        self.decoder_model = Path(__file__).parent / "../models/decoder.pth.tar"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.decoder = None
        self.vgg = None

    def load_model(self):

        self.decoder = net.decoder
        self.vgg = net.vgg

        self.decoder.eval()
        self.vgg.eval()

        self.decoder.load_state_dict(torch.load(self.decoder_model))
        self.vgg.load_state_dict(torch.load(self.vgg_model))
        self.vgg = nn.Sequential(*list(self.vgg.children())[:31])

        self.vgg.to(self.device)
        self.decoder.to(self.device)

    def create_painting(self, content, style, preserve_color=False, alpha=1.0,
                        content_new_size=0, style_new_size=0, crop=False):

        content_tf = self._transform(content_new_size, crop)
        style_tf = self._transform(style_new_size, crop)

        content = content.convert("RGB")
        style = style.convert("RGB")

        content = content_tf(content)
        style = style_tf(style)
        if preserve_color:
            style = coral(style, content)
        style = style.to(self.device).unsqueeze(0)
        content = content.to(self.device).unsqueeze(0)
        with torch.no_grad():
            output = self._style_transfer(content, style, alpha)
            output = output.clamp(0, 1)
        output = output.cpu().clone().squeeze(0)
        image = transforms.ToPILImage()(output)

        return image

    @staticmethod
    def _transform(size, crop):
        transform_list = []
        if size != 0:
            transform_list.append(transforms.Resize(size))
        if crop:
            transform_list.append(transforms.CenterCrop(size))
        transform_list.append(transforms.ToTensor())
        transform = transforms.Compose(transform_list)
        return transform

    def _style_transfer(self, content, style, alpha=1.0):
        assert (0.0 <= alpha <= 1.0)
        content_f = self.vgg(content)
        style_f = self.vgg(style)

        feat = adaptive_instance_normalization(content_f, style_f)
        feat = feat * alpha + content_f * (1 - alpha)
        return self.decoder(feat)
