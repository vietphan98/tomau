"""Ghép ảnh Trước | Sau với nhãn tiếng Việt (vẽ bằng Pillow để đủ dấu)."""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    os.environ.get("TOMAU_FONT", ""),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/noto/NotoSans-Bold.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
    "DejaVuSans-Bold.ttf",
]


def _font(size):
    for path in FONT_CANDIDATES:
        if not path:
            continue
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    raise RuntimeError(
        "Không tìm thấy font có dấu tiếng Việt. Cài DejaVu Sans / Noto Sans "
        "hoặc đặt biến môi trường TOMAU_FONT=/đường/dẫn/font.ttf"
    )


def _bgr_to_pil(img):
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def make_comparison(before_bgr, after_bgr, labels=("Trước", "Sau"), max_height=900):
    """Trả về ảnh BGR: hai ảnh cạnh nhau, mỗi ảnh có nhãn phía trên."""
    if before_bgr is None or after_bgr is None or before_bgr.size == 0 or after_bgr.size == 0:
        raise ValueError("Ảnh rỗng, không thể ghép so sánh")
    h, w = after_bgr.shape[:2]
    if before_bgr.shape[:2] != (h, w):
        before_bgr = cv2.resize(before_bgr, (w, h))
    if h > max_height:
        scale = max_height / h
        size = (max(1, int(w * scale)), max_height)
        before_bgr = cv2.resize(before_bgr, size, interpolation=cv2.INTER_AREA)
        after_bgr = cv2.resize(after_bgr, size, interpolation=cv2.INTER_AREA)
        h, w = after_bgr.shape[:2]

    gap = max(6, w // 100)
    bar = max(48, h // 12)
    font = _font(int(bar * 0.62))

    canvas = Image.new("RGB", (w * 2 + gap * 3, h + bar + gap * 2), (18, 18, 18))
    draw = ImageDraw.Draw(canvas)
    for i, (img, text) in enumerate(zip((before_bgr, after_bgr), labels)):
        x = gap + i * (w + gap)
        canvas.paste(_bgr_to_pil(img), (x, bar + gap))
        tb = draw.textbbox((0, 0), text, font=font)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        draw.text((x + (w - tw) // 2 - tb[0], (bar + gap - th) // 2 - tb[1] + gap // 2),
                  text, font=font, fill=(255, 255, 255))
    return cv2.cvtColor(np.asarray(canvas), cv2.COLOR_RGB2BGR)
