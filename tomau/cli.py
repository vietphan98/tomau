"""Dòng lệnh: tô màu 1 ảnh hoặc cả thư mục."""
import argparse
import os
import sys
import time

from .compare import make_comparison
from .core import Colorizer, ModelMissingError, to_gray_bgr
from .io import IMAGE_EXTS, read_image, write_image


def _collect(inp):
    if os.path.isdir(inp):
        return sorted(
            os.path.join(inp, f) for f in os.listdir(inp)
            if os.path.splitext(f)[1].lower() in IMAGE_EXTS
        )
    return [inp]


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="tomau",
        description="Tô màu ảnh đen trắng cũ - chạy offline, miễn phí.",
    )
    ap.add_argument("input", help="Ảnh hoặc thư mục ảnh")
    ap.add_argument("-o", "--output", default="ket_qua", help="Thư mục lưu kết quả (mặc định: ket_qua)")
    ap.add_argument("-s", "--strength", type=float, default=1.0,
                    help="Độ đậm màu: 0 = đen trắng, 1 = mặc định, 1.3 = rực hơn")
    ap.add_argument("--no-compare", action="store_true", help="Không xuất ảnh so sánh Trước/Sau")
    ap.add_argument("--models", default=None, help="Thư mục chứa model (mặc định: ./models)")
    args = ap.parse_args(argv)

    files = _collect(args.input)
    if not files or not os.path.exists(files[0]):
        print(f"Không tìm thấy ảnh ở: {args.input}")
        return 1

    try:
        col = Colorizer(args.models) if args.models else Colorizer()
    except ModelMissingError as e:
        print(e)
        return 2

    os.makedirs(args.output, exist_ok=True)
    t_all = time.time()
    for i, path in enumerate(files, 1):
        stem = os.path.splitext(os.path.basename(path))[0]
        t = time.time()
        try:
            img = read_image(path)
        except ValueError as e:
            print(f"[{i}/{len(files)}] bỏ qua: {e}")
            continue
        out = col.colorize(img, strength=args.strength)
        out_path = os.path.join(args.output, f"{stem}_tomau.jpg")
        write_image(out_path, out)
        msg = f"[{i}/{len(files)}] {path} -> {out_path}"
        if not args.no_compare:
            cmp_path = os.path.join(args.output, f"{stem}_so_sanh.jpg")
            write_image(cmp_path, make_comparison(to_gray_bgr(img), out))
            msg += f" (+ {cmp_path})"
        print(f"{msg}  [{time.time() - t:.1f}s]")
    print(f"Xong {len(files)} ảnh trong {time.time() - t_all:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
