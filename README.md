# 🎨 tomau — Tô màu ảnh đen trắng cũ bằng AI, miễn phí, chạy trên máy bạn

**tomau** biến ảnh đen trắng cũ (ảnh ông bà, ảnh gia đình, ảnh lịch sử) thành ảnh màu chỉ trong vài giây.
Chạy trên máy của bạn: **lần đầu cần Internet để tải model (~125 MB)**, sau đó chạy offline hoàn toàn — không gửi ảnh lên server nào, không tốn phí, không giới hạn số ảnh.

> ⚠️ Màu là do AI **đoán**, có thể sai và **không chính xác về mặt lịch sử** (màu áo, màu tóc, màu đồ vật… có thể khác hoàn toàn thực tế). Hãy xem kết quả là bản minh hoạ tham khảo, không phải tư liệu.

![Trước / Sau](examples/ket_qua/migrant_mother_so_sanh.jpg)

## Tính năng

- Tô màu tự động bằng mạng nơ-ron (OpenCV DNN, chạy bằng CPU, thường vài giây/ảnh tuỳ máy và kích thước ảnh).
- Dòng lệnh: tô **1 ảnh** hoặc **cả thư mục** một lần.
- Giao diện web nhỏ: kéo ảnh vào, bấm "Tô màu", tải kết quả về.
- Tự xuất **ảnh so sánh Trước | Sau** đặt cạnh nhau (nhãn tiếng Việt có dấu) — đăng mạng xã hội ngay.
- Nút chỉnh **độ đậm màu** (`--strength`): 0 = giữ đen trắng, 1 = mặc định, 1.3–1.5 = màu rực hơn.
- Giữ nguyên độ phân giải và chi tiết của ảnh gốc (chỉ thêm màu, không làm mờ ảnh).

## Cài đặt

Yêu cầu: Python 3.9+ (Windows / macOS / Linux).

```bash
git clone https://github.com/vietphan98/tomau.git
cd tomau
python -m venv .venv
# Windows: .venv\Scripts\activate    |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Tải model (~125 MB, cần Internet, chỉ 1 lần; có kiểm tra SHA-256)
python download_models.py
```

Script ưu tiên nguồn chính thức của tác giả (Berkeley). Hiện (30/10/2026) link chính thức của file `colorization_release_v2.caffemodel` đã hỏng (404/500), nên script sẽ tự dùng **mirror bên thứ ba** trên Hugging Face Space [BilalSardar/Black-N-White-To-Color](https://huggingface.co/spaces/BilalSardar/Black-N-White-To-Color) — đây không phải nguồn chính thức, nhưng file được đối chiếu SHA-256 (`f5af1e60…37b1`) trước khi dùng. Hai file nhỏ còn lại tải trực tiếp từ repo GitHub chính thức `richzhang/colorization`.

Model được lưu vào thư mục `models/` (đổi chỗ khác bằng `python download_models.py --dir <thư mục>` và đặt biến môi trường `TOMAU_MODELS=<thư mục>`).

> Lưu ý: cần `opencv-python(-headless)` bản 4.x (OpenCV 5 bỏ hỗ trợ đọc model Caffe) — `requirements.txt` đã ghim sẵn.

## Cách dùng

### Dòng lệnh

```bash
# Tô màu 1 ảnh -> ket_qua/anh_ong_ba_tomau.jpg + ket_qua/anh_ong_ba_so_sanh.jpg
python -m tomau anh_ong_ba.jpg

# Tô màu cả thư mục, lưu vào thư mục khác
python -m tomau album_cu/ -o album_mau/

# Màu đậm hơn một chút
python -m tomau anh_ong_ba.jpg -s 1.3

# Không cần ảnh so sánh
python -m tomau album_cu/ --no-compare
```

| Tuỳ chọn | Ý nghĩa |
|---|---|
| `-o, --output` | Thư mục lưu kết quả (mặc định `ket_qua`) |
| `-s, --strength` | Độ đậm màu (mặc định `1.0`) |
| `--no-compare` | Không xuất ảnh so sánh Trước/Sau |
| `--models` | Thư mục chứa model |

### Giao diện web

```bash
python app.py            # hoặc: python app.py --port 8080
```

Mở trình duyệt tại <http://127.0.0.1:5000>, chọn ảnh, kéo thanh "Độ đậm màu", bấm **Tô màu**. Kết quả hiện ngay dạng Trước | Sau, có nút tải ảnh màu và ảnh so sánh.

### Dùng trong code Python

```python
import cv2
from tomau import Colorizer, make_comparison
from tomau.core import to_gray_bgr

col = Colorizer()
img = cv2.imread("anh_cu.jpg")
mau = col.colorize(img, strength=1.2)
cv2.imwrite("anh_mau.jpg", mau)
cv2.imwrite("so_sanh.jpg", make_comparison(to_gray_bgr(img), mau))
```

## Ví dụ

| Ảnh gốc | Kết quả |
|---|---|
| [examples/dau_vao/migrant_mother.jpg](examples/dau_vao/migrant_mother.jpg) | [examples/ket_qua/migrant_mother_so_sanh.jpg](examples/ket_qua/migrant_mother_so_sanh.jpg) |
| [examples/dau_vao/lincoln_1863.jpg](examples/dau_vao/lincoln_1863.jpg) | [examples/ket_qua/lincoln_1863_so_sanh.jpg](examples/ket_qua/lincoln_1863_so_sanh.jpg) |

![Lincoln Trước / Sau](examples/ket_qua/lincoln_1863_so_sanh.jpg)

(Màu trong các ảnh mẫu là AI đoán, không phải màu thật.)

Nguồn ảnh mẫu (Wikimedia Commons, đã kiểm tra trang file ngày 30/10/2026; ảnh được thu nhỏ):

| File | Tác giả | Nguồn | Giấy phép (theo Commons) |
|---|---|---|---|
| `migrant_mother.jpg` | Dorothea Lange (1895–1965), cho Farm Security Administration, 6/3/1936 | Library of Congress — <https://commons.wikimedia.org/wiki/File:Lange-MigrantMother02.jpg> | Public domain: `PD-USGov-FSA` (tác phẩm của chính phủ Mỹ) + `PD-old-auto` (tác giả mất 1965) |
| `lincoln_1863.jpg` | Alexander Gardner (1821–1882), 8/11/1863 | Mead Art Museum — <https://commons.wikimedia.org/wiki/File:Abraham_Lincoln_O-77_matte_collodion_print.jpg> | Public domain: `PD-scan` / `PD-old-auto-1923` (tác giả mất 1882, public domain trên toàn thế giới) |

> Ảnh Einstein 1947 (Orren Jack Turner) từng dùng trước đây đã bị **gỡ bỏ**: Commons ghi nó public domain tại Mỹ (không gia hạn bản quyền) nhưng có thẻ `Urheberrechtlich geschützt` (vẫn còn bản quyền ở Đức), tức không chắc chắn public domain toàn cầu.

## Demo (quay video 20–30 giây)

Mục tiêu: người xem thấy rõ ảnh **đen trắng → có màu** trong vài giây đầu.

1. **Chuẩn bị**: 2–3 ảnh đen trắng cũ thật (ảnh ông bà, ảnh gia đình xưa — chụp lại bằng điện thoại cũng được) để trong thư mục `album_cu/`. Mở sẵn `python app.py` trên trình duyệt, phóng to cửa sổ.
2. **0–3s (hook)**: cầm tấm ảnh đen trắng thật trên tay đưa vào khung hình, chèn chữ câu hook.
3. **3–12s**: trên web, chọn ảnh → bấm **Tô màu** → ảnh Trước | Sau hiện ra (quay cận màn hình, để thấy chỉ mất vài giây).
4. **12–20s**: kéo thanh "Độ đậm màu" lên 1.4 và bấm lại để thấy màu rực hơn; hoặc mở terminal chạy `python -m tomau album_cu/` để tô cả album một lần.
5. **20–30s**: lướt nhanh qua các ảnh `*_so_sanh.jpg` trong thư mục kết quả (hiệu ứng trượt/zoom từ trái sang phải), kết bằng chữ: "Miễn phí, chạy trên máy bạn — link GitHub ở bình luận". Nên thêm dòng nhỏ: "Màu do AI đoán, có thể không đúng thực tế".

**Câu hook gợi ý cho Reel:**
> "Ảnh đen trắng của ông bà, vài giây là AI tô màu xong. Miễn phí, chạy ngay trên máy bạn."

## Cách hoạt động (tóm tắt)

1. Chuyển ảnh sang không gian màu **Lab**; kênh **L** (độ sáng) chính là ảnh đen trắng.
2. Thu nhỏ kênh L về 224×224 và đưa vào mạng nơ-ron; mạng dự đoán 2 kênh màu **a, b**.
3. Phóng kênh a, b về kích thước gốc, nhân với hệ số độ đậm, ghép lại với kênh L **gốc** → ảnh màu giữ nguyên chi tiết.

## Giấy phép & ghi công

- Mã nguồn **tomau**: MIT © 2026 Việt Phan — xem [LICENSE](LICENSE).
- **Model tô màu không thuộc về dự án này.** Model là của các tác giả bài báo
  *"Colorful Image Colorization"* — Richard Zhang, Phillip Isola, Alexei A. Efros (ECCV 2016),
  bài báo: <https://arxiv.org/abs/1603.08511> (arXiv:1603.08511).
  Repo gốc: <https://github.com/richzhang/colorization>. File [LICENSE](https://github.com/richzhang/colorization/blob/master/LICENSE)
  của repo đó là giấy phép **BSD 2-Clause** ("Simplified BSD"), *Copyright (c) 2016, Richard Zhang, Phillip Isola, Alexei A. Efros*
  (đã kiểm tra trực tiếp ngày 30/10/2026). Khi phân phối lại phải giữ thông báo bản quyền này.
  Repo này không chứa file model; `download_models.py` tải chúng khi bạn chạy (nguồn chính thức trước, mirror bên thứ ba dự phòng — xem phần Cài đặt).
- Màu do AI đoán nên có thể sai, không chính xác về lịch sử — chỉ là bản minh hoạ tham khảo.

Tác giả: **Việt Phan**
