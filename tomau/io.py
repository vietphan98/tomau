"""Đọc/ghi ảnh an toàn với đường dẫn có dấu tiếng Việt (kể cả trên Windows)."""
import os

import cv2
import numpy as np

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def read_image(path):
    data = np.fromfile(path, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Không đọc được ảnh: {path}")
    if img.dtype != np.uint8:  # ảnh 16-bit (scan) -> 8-bit
        img = (img / 257).astype(np.uint8)
    return img


def write_image(path, img, quality=95):
    ext = os.path.splitext(path)[1].lower() or ".jpg"
    params = [cv2.IMWRITE_JPEG_QUALITY, quality] if ext in (".jpg", ".jpeg") else []
    ok, buf = cv2.imencode(ext, img, params)
    if not ok:
        raise ValueError(f"Không ghi được ảnh: {path}")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    buf.tofile(path)


def encode_jpg(img, quality=92):
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise ValueError("Không mã hoá được ảnh")
    return buf.tobytes()


def decode_bytes(data):
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("File tải lên không phải ảnh hợp lệ")
    if img.dtype != np.uint8:
        img = (img / 257).astype(np.uint8)
    return img
