#!/usr/bin/env python3
"""Tải 3 file model tô màu (Zhang et al., 2016 - BSD-2) về thư mục models/.

Dùng:  python download_models.py            # tải vào ./models
       python download_models.py --dir D:/models
"""
import argparse
import hashlib
import os
import sys
import urllib.request

FILES = {
    "colorization_deploy_v2.prototxt": {
        "sha256": "d16418cef8df4ccd703a55ae0ef3960861d5010418f77c90d0a47689998a7169",
        "urls": [
            "https://raw.githubusercontent.com/richzhang/colorization/caffe/colorization/models/colorization_deploy_v2.prototxt",
        ],
    },
    "pts_in_hull.npy": {
        "sha256": "b5dec01315c34f43f1c8c089e84c45ae35d1838d8e77ed0e7ca930f79ffa450e",
        "urls": [
            "https://raw.githubusercontent.com/richzhang/colorization/caffe/colorization/resources/pts_in_hull.npy",
        ],
    },
    "colorization_release_v2.caffemodel": {
        "sha256": "f5af1e602646328c792e1094f9876fe9cd4c09ac46fa886e5708a1abc89137b1",
        "urls": [
            "https://huggingface.co/spaces/BilalSardar/Black-N-White-To-Color/resolve/main/colorization_release_v2.caffemodel",
            "http://eecs.berkeley.edu/~rich.zhang/projects/2016_colorization/files/demo_v2/colorization_release_v2.caffemodel",
        ],
    },
}

DEFAULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "tomau-downloader/1.0"})
    tmp = dest + ".part"
    with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as out:
        total = int(resp.headers.get("Content-Length") or 0)
        done = 0
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
            done += len(chunk)
            if total:
                sys.stdout.write(f"\r   {done / 1e6:6.1f} / {total / 1e6:.1f} MB")
                sys.stdout.flush()
    if total:
        print()
    os.replace(tmp, dest)


def main():
    ap = argparse.ArgumentParser(description="Tải model tô màu ảnh cho tomau")
    ap.add_argument("--dir", default=os.environ.get("TOMAU_MODELS", DEFAULT_DIR))
    args = ap.parse_args()
    os.makedirs(args.dir, exist_ok=True)

    ok = True
    for name, info in FILES.items():
        dest = os.path.join(args.dir, name)
        if os.path.exists(dest) and sha256_of(dest) == info["sha256"]:
            print(f"[đã có] {name}")
            continue
        for url in info["urls"]:
            print(f"[tải]   {name}\n   từ {url}")
            try:
                fetch(url, dest)
            except Exception as e:  # noqa: BLE001
                print(f"   lỗi: {e}")
                continue
            if sha256_of(dest) == info["sha256"]:
                print("   OK (checksum khớp)")
                break
            print("   checksum không khớp, thử nguồn khác...")
            os.remove(dest)
        else:
            ok = False
            print(f"[THẤT BẠI] Không tải được {name}")

    if ok:
        print(f"\nXong! Model nằm ở: {args.dir}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
