"""Giao diện web nhỏ (Flask): tải ảnh lên -> nhận ảnh đã tô màu + ảnh so sánh."""
import argparse
import base64
import threading

from flask import Flask, render_template_string, request

from .compare import make_comparison
from .core import Colorizer, to_gray_bgr
from .io import decode_bytes, encode_jpg

PAGE = """<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>tomau - Tô màu ảnh cũ</title>
<style>
 body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:#141414;color:#eee;margin:0;padding:24px}
 .box{max-width:1100px;margin:auto}
 h1{margin:0 0 4px} p.sub{color:#aaa;margin:0 0 20px}
 form{background:#1f1f1f;padding:18px;border-radius:12px;display:flex;gap:16px;flex-wrap:wrap;align-items:center}
 input[type=file]{color:#ddd} button{background:#e8a33d;border:0;padding:10px 22px;border-radius:8px;font-size:16px;font-weight:600;cursor:pointer}
 label{color:#ccc} .err{background:#5a1f1f;padding:12px;border-radius:8px;margin-top:16px}
 img{max-width:100%;border-radius:10px;margin-top:18px;display:block}
 a.dl{color:#e8a33d;margin-right:18px}
</style></head><body><div class="box">
<h1>🎨 tomau</h1>
<p class="sub">Tô màu ảnh đen trắng cũ trong vài giây — chạy hoàn toàn trên máy bạn, không gửi ảnh đi đâu.</p>
<form method="post" enctype="multipart/form-data">
 <input type="file" name="photo" accept="image/*" required>
 <label>Độ đậm màu: <input type="range" name="strength" min="0" max="2" step="0.1" value="{{ strength }}"
   oninput="this.nextElementSibling.textContent=this.value"> <b>{{ strength }}</b></label>
 <button type="submit">Tô màu</button>
</form>
{% if error %}<div class="err">{{ error }}</div>{% endif %}
{% if compare %}
 <img src="data:image/jpeg;base64,{{ compare }}" alt="Trước / Sau">
 <p><a class="dl" download="{{ name }}_tomau.jpg" href="data:image/jpeg;base64,{{ result }}">⬇ Tải ảnh đã tô màu</a>
 <a class="dl" download="{{ name }}_so_sanh.jpg" href="data:image/jpeg;base64,{{ compare }}">⬇ Tải ảnh so sánh</a>
 <span style="color:#888">({{ secs }} giây)</span></p>
{% endif %}
</div></body></html>"""


def create_app(colorizer=None):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 40 * 1024 * 1024
    state = {"col": colorizer}
    lock = threading.Lock()

    def get_col():
        with lock:
            if state["col"] is None:
                state["col"] = Colorizer()
            return state["col"]

    @app.route("/", methods=["GET", "POST"])
    def index():
        ctx = {"strength": 1.0}
        if request.method == "POST":
            import time
            f = request.files.get("photo")
            try:
                strength = max(0.0, min(2.0, float(request.form.get("strength", 1.0))))
            except ValueError:
                strength = 1.0
            ctx["strength"] = strength
            if not f or not f.filename:
                ctx["error"] = "Chưa chọn ảnh."
                return render_template_string(PAGE, **ctx)
            try:
                img = decode_bytes(f.read())
                t = time.time()
                out = get_col().colorize(img, strength=strength)
                cmp_img = make_comparison(to_gray_bgr(img), out)
                ctx.update(
                    result=base64.b64encode(encode_jpg(out)).decode(),
                    compare=base64.b64encode(encode_jpg(cmp_img)).decode(),
                    name=(f.filename.rsplit(".", 1)[0] or "anh"),
                    secs=f"{time.time() - t:.1f}",
                )
            except Exception as e:  # noqa: BLE001
                ctx["error"] = f"Lỗi: {e}"
        return render_template_string(PAGE, **ctx)

    return app


def main(argv=None):
    ap = argparse.ArgumentParser(description="Giao diện web của tomau")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5000)
    args = ap.parse_args(argv)
    col = Colorizer()  # nạp model trước để báo lỗi sớm nếu thiếu
    print(f"Mở trình duyệt: http://{args.host}:{args.port}")
    create_app(col).run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
