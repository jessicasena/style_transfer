from pathlib import Path
import torch
import torch.nn as nn
from torchvision import transforms
import net
from function import adaptive_instance_normalization, coral
import time


def test_transform(size, crop):
    transform_list = []
    if size != 0:
        transform_list.append(transforms.Resize(size))
    if crop:
        transform_list.append(transforms.CenterCrop(size))
    transform_list.append(transforms.ToTensor())
    transform = transforms.Compose(transform_list)
    return transform


def style_transfer(device, vgg, decoder, content, style, alpha=1.0,
                   interpolation_weights=None):
    assert (0.0 <= alpha <= 1.0)
    content_f = vgg(content)
    style_f = vgg(style)
    if interpolation_weights:
        _, C, H, W = content_f.size()
        feat = torch.FloatTensor(1, C, H, W).zero_().to(device)
        base_feat = adaptive_instance_normalization(content_f, style_f)
        for i, w in enumerate(interpolation_weights):
            feat = feat + w * base_feat[i:i + 1]
        content_f = content_f[0:1]
    else:
        feat = adaptive_instance_normalization(content_f, style_f)
    feat = feat * alpha + content_f * (1 - alpha)
    return decoder(feat)


def stylize(content, style, preserve_color=False, alpha=1.0):
    vgg_model = 'models/vgg_normalised.pth'
    decoder_model = 'models/decoder_iter_160000.pth.tar'
    output = ''
    content_size = 512
    style_size = 512
    crop = False

    start = time.time()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    output_dir = Path(output)
    output_dir.mkdir(exist_ok=True, parents=True)

    decoder = net.decoder
    vgg = net.vgg

    decoder.eval()
    vgg.eval()

    decoder.load_state_dict(torch.load(decoder_model))
    vgg.load_state_dict(torch.load(vgg_model))
    vgg = nn.Sequential(*list(vgg.children())[:31])

    vgg.to(device)
    decoder.to(device)

    content_tf = test_transform(content_size, crop)
    style_tf = test_transform(style_size, crop)

    content = content_tf(content)
    style = style_tf(style)
    if preserve_color:
        style = coral(style, content)
    style = style.to(device).unsqueeze(0)
    content = content.to(device).unsqueeze(0)
    with torch.no_grad():
        output = style_transfer(device, vgg, decoder, content, style,
                                alpha)
    output = output.cpu().clone()
    image = output.squeeze(0)
    image = transforms.ToPILImage()(image)

    end = time.time()
    print(end - start)

    return image
