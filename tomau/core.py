"""Lõi tô màu: OpenCV DNN + model Colorful Image Colorization (Zhang et al.)."""
import os

import cv2
import numpy as np

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MODEL_DIR = os.environ.get("TOMAU_MODELS", os.path.join(PROJECT_DIR, "models"))

PROTOTXT = "colorization_deploy_v2.prototxt"
WEIGHTS = "colorization_release_v2.caffemodel"
HULL = "pts_in_hull.npy"

NET_SIZE = 224  # mạng nhận ảnh kênh L kích thước 224x224


class ModelMissingError(RuntimeError):
    pass


class Colorizer:
    """Tô màu một ảnh BGR (hoặc xám) và trả về ảnh BGR có màu."""

    def __init__(self, model_dir=DEFAULT_MODEL_DIR):
        paths = [os.path.join(model_dir, n) for n in (PROTOTXT, WEIGHTS, HULL)]
        missing = [p for p in paths if not os.path.isfile(p)]
        if missing:
            raise ModelMissingError(
                "Thiếu file model:\n  " + "\n  ".join(missing)
                + "\nHãy chạy:  python download_models.py"
            )
        self.net = cv2.dnn.readNetFromCaffe(paths[0], paths[1])

        # 313 cụm màu (a,b) được lượng tử hoá -> gắn vào lớp 1x1 conv cuối
        centers = np.load(paths[2]).astype(np.float32)  # (313, 2)
        kernel = centers.T.reshape(2, 313, 1, 1)
        self.net.getLayer(self.net.getLayerId("class8_ab")).blobs = [kernel]
        # "annealed mean": nhân 2.606 để màu tươi hơn, theo bài báo gốc
        self.net.getLayer(self.net.getLayerId("conv8_313_rh")).blobs = [
            np.full((1, 313), 2.606, dtype=np.float32)
        ]

    @staticmethod
    def _to_bgr(img):
        if img.ndim == 2:
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        if img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def colorize(self, img, strength=1.0):
        """img: ảnh uint8 (BGR/xám). strength: 0 = giữ đen trắng, 1 = mặc định, >1 = rực hơn."""
        bgr = self._to_bgr(img)
        f = bgr.astype(np.float32) / 255.0
        lab = cv2.cvtColor(f, cv2.COLOR_BGR2Lab)
        L = lab[:, :, 0]

        small = cv2.resize(f, (NET_SIZE, NET_SIZE), interpolation=cv2.INTER_AREA)
        L_small = cv2.cvtColor(small, cv2.COLOR_BGR2Lab)[:, :, 0] - 50.0

        self.net.setInput(cv2.dnn.blobFromImage(L_small))
        ab = self.net.forward()[0].transpose(1, 2, 0)  # (56, 56, 2)
        h, w = L.shape
        ab = cv2.resize(ab, (w, h), interpolation=cv2.INTER_CUBIC) * float(strength)

        out = np.dstack([L, ab]).astype(np.float32)
        out = cv2.cvtColor(out, cv2.COLOR_Lab2BGR)
        return (np.clip(out, 0, 1) * 255).round().astype(np.uint8)


def to_gray_bgr(img):
    """Bản đen trắng của ảnh (để hiển thị phần 'Trước')."""
    if img.ndim == 2:
        g = img
    else:
        g = cv2.cvtColor(Colorizer._to_bgr(img), cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
