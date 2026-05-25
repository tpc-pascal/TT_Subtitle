## Hướng dẫn sử dụng TT_Subtitle

### Yêu cầu

- Python 3.10+
- FFmpeg (cài đặt riêng hoặc dùng Hugging Face / Colab)

### Cách 1: Chạy trên Hugging Face Spaces (Khuyên dùng)

Truy cập: [huggingface.co/spaces/tpc-pascal/TT_Subtitle](https://huggingface.co/spaces/tpc-pascal/TT_Subtitle)

1. Chọn **nền tảng** từ dropdown (YouTube, Bilibili, Douyin, TikTok, ...)
2. **Tìm kiếm** video (nếu là YouTube/Bilibili/SoundCloud) hoặc **dán URL** trực tiếp
3. Chọn **ngôn ngữ gốc** và **ngôn ngữ dịch**
4. Chọn **định dạng đầu ra**: SRT, TXT, Sub vào video, Cả hai
5. Bật **Lồng tiếng (TTS)** nếu muốn
6. Nhấn **Xử lý** và chờ kết quả

---

### Cách 2: Chạy trên Google Colab

Mở `colab.ipynb` trên Colab và chạy lần lượt các cell.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tpc-pascal/TT_Subtitle/blob/main/colab.ipynb)

---

### Cách 3: Chạy local

```bash
git clone https://github.com/tpc-pascal/TT_Subtitle.git
cd TT_Subtitle/hf
pip install -r requirements.txt
python app.py
```

Mở trình duyệt tại `http://localhost:7860`.

> **Lưu ý:** Lần đầu chạy, Whisper và NLLB sẽ tải model (~1-2GB). Cần kết nối internet ổn định.

---

### Chi tiết các bước xử lý

| Bước | Mô tả | Công nghệ |
|---|---|---|
| 1. Tải video | Tải audio/video từ URL | yt-dlp |
| 2. ASR | Nhận dạng giọng nói → phụ đề gốc | OpenAI Whisper |
| 3. Dịch | Dịch phụ đề sang ngôn ngữ đích | Meta NLLB-200 |
| 4. Xuất file | SRT / TXT | - |
| 5. Sub video | Ghi phụ đề trực tiếp vào video | FFmpeg |
| 6. Lồng tiếng | Tạo giọng đọc AI + ghép vào video | Edge-TTS + FFmpeg |

---

### Các nền tảng được hỗ trợ

TT_Subtitle hỗ trợ **1800+ trang web** thông qua yt-dlp. Một số nền tảng phổ biến:

| Nền tảng | Tìm kiếm nội bộ | URL trực tiếp |
|---|---|---|
| YouTube | ✅ | ✅ |
| Bilibili | ✅ | ✅ |
| SoundCloud | ✅ | ✅ |
| Douyin (抖音) | ❌ | ✅ |
| TikTok | ❌ | ✅ |
| Facebook | ❌ | ✅ |
| Instagram | ❌ | ✅ |
| Twitter / X | ❌ | ✅ |
| Twitch | ❌ | ✅ |
| Vimeo | ❌ | ✅ |
| Khác | ❌ | ✅ |

Đối với các nền tảng không hỗ trợ tìm kiếm, chỉ cần **dán link video** vào ô URL.

---

### Ngôn ngữ hỗ trợ

| Ngôn ngữ | Mã NLLB | Whisper | Edge-TTS |
|---|---|---|---|
| Tiếng Trung | zho_Hans | ✅ | ✅ |
| Tiếng Anh | eng_Latn | ✅ | ✅ |
| Tiếng Việt | vie_Latn | ✅ | ✅ |
| Tiếng Nhật | jpn_Jpan | ✅ | ✅ |
| Tiếng Hàn | kor_Hang | ✅ | ✅ |

> Có thể mở rộng thêm ngôn ngữ bằng cách chỉnh sửa `translate.py` và `tts.py`.

---

### Triển khai lên Hugging Face

#### Tự động (GitHub Actions)

1. Fork repo về tài khoản của bạn
2. Tạo Space trên Hugging Face: https://huggingface.co/new-space (SDK: Gradio, GPU: T4 small)
3. Thêm secrets vào GitHub repo (Settings → Secrets → Actions):
   - `HF_SPACE_ID`: `username/space-name`
   - `HF_TOKEN`: Token từ https://huggingface.co/settings/tokens
4. Push lên `main` — GitHub Action tự động đồng bộ `hf/` lên HF Space

#### Thủ công

```bash
git clone https://huggingface.co/spaces/<username>/<space-name>
cp -r TT_Subtitle/hf/* <space-name>/
cd <space-name>
git add .
git commit -m "Deploy TT_Subtitle"
git push
```

---

### Xử lý sự cố

| Vấn đề | Nguyên nhân | Giải pháp |
|---|---|---|
| Whisper báo lỗi CUDA | Hết GPU memory | Dùng model `tiny` hoặc `base` thay vì `small` |
| yt-dlp không tải được video | Trang web thay đổi | Cập nhật yt-dlp: `pip install -U yt-dlp` |
| Dịch thuật sai ngôn ngữ | Nhầm mã ngôn ngữ | Kiểm tra `LANG_MAP` trong `translate.py` |
| Lồng tiếng bị lỗi | Mất kết nối Edge-TTS | Kiểm tra internet, thử lại |
| FFmpeg not found | Thiếu system package | Cài FFmpeg hoặc dùng HF/Colab |
| Hugging Face hết disk | File tạm quá nhiều | Dùng tính năng Cleanup hoặc đợi session reset |

---

### Tuỳ chỉnh nâng cao

#### Đổi model Whisper

Sửa trong `utils/subtitle.py`:

```python
_model = whisper.load_model("tiny")  # hoặc base, small, medium, large
```

#### Đổi model dịch thuật

Sửa trong `utils/translate.py`:

```python
MODEL_NAME = "facebook/nllb-200-distilled-600M"  # hoặc phiên bản khác
```

#### Đổi giọng TTS

Sửa trong `utils/tts.py`:

```python
VOICE_MAP = {
    "vi": "vi-VN-HoaiMyNeural",
    "en": "en-US-JennyNeural",
    # Thêm giọng khác từ https://speech.microsoft.com/portal/voicegallery
}
```
