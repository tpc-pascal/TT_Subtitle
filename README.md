# TT_Subtitle
Extract, translate subtitles and dub videos from any platform

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tpc-pascal/TT_Subtitle/blob/main/colab.ipynb)
[![Open in Hugging Face](https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-hf-spaces-md-dark.svg)](https://huggingface.co/spaces/tpc-pascal/TT_Subtitle)

> Công cụ trích xuất phụ đề từ video (ASR), dịch thuật đa ngôn ngữ, sub trực tiếp vào video và lồng tiếng tự động bằng AI.

**Lý do ra đời:** Bạn muốn dịch phim Trung Quốc, video nước ngoài sang tiếng Việt nhưng không biết bắt đầu từ đâu? TT_Subtitle cho phép bạn tìm kiếm video từ nhiều nền tảng, tự động nhận dạng giọng nói, dịch phụ đề, và thậm chí lồng tiếng — tất cả trong một giao diện web.

---

## Tính năng

- Hỗ trợ **1800+ nền tảng** qua yt-dlp: YouTube, Bilibili, Douyin, TikTok, Facebook, Instagram, Twitter, Twitch, Vimeo...
- **ASR** (Automatic Speech Recognition) với OpenAI Whisper — nhận dạng giọng nói thành phụ đề
- **Dịch thuật** đa ngôn ngữ với Meta NLLB-200 (hỗ trợ Trung ↔ Việt, Anh, Nhật, Hàn...)
- **Xuất file** phụ đề: SRT, TXT
- **Sub trực tiếp** vào video (hardcode subtitle)
- **Lồng tiếng** tự động bằng Edge-TTS (giọng AI tự nhiên)
- Tìm kiếm nội bộ cho YouTube, Bilibili, SoundCloud
- Dán URL trực tiếp cho các nền tảng khác

---

## Cấu trúc thư mục

```
TT_Subtitle/
├── hf/                          # Hugging Face Spaces deployment
│   ├── app.py                   # Entry point — Gradio UI
│   ├── requirements.txt         # Python dependencies
│   ├── packages.txt             # System packages (FFmpeg, fonts)
│   ├── utils/
│   │   ├── search.py            # Multi-platform search & download (yt-dlp)
│   │   ├── subtitle.py          # Whisper ASR engine
│   │   ├── translate.py         # NLLB-200 translation engine
│   │   ├── tts.py               # Edge-TTS dubbing engine
│   │   └── video_editor.py      # FFmpeg video processing
│   └── README.md                # HF Space metadata
├── colab.ipynb                  # Google Colab notebook
├── .github/workflows/
│   └── sync.yml                 # GitHub Action → HF Spaces
├── CONTRIBUTING.md              # Hướng dẫn đóng góp
├── CREDITS.md                   # Credits & tham khảo
└── LICENSE                      # MIT
```

---

## Tech Stack

| Layer | Công nghệ |
|---|---|
| Language | Python 3.10+ |
| Web UI | Gradio |
| Downloader | yt-dlp (1800+ sites) |
| Speech-to-Text | OpenAI Whisper |
| Translation | Meta NLLB-200-distilled-600M |
| Text-to-Speech | Microsoft Edge-TTS |
| Video Processing | FFmpeg |
| CI/CD | GitHub Actions → Hugging Face Spaces |

---

## Pipeline xử lý

```
Video URL → yt-dlp tải audio → Whisper ASR → Phụ đề gốc
                                           ↓
                              NLLB-200 dịch thuật → Phụ đề dịch
                                           ↓
                          ┌── Xuất SRT/TXT
                          ├── FFmpeg sub vào video
                          └── Edge-TTS → Ghép giọng đọc → Video lồng tiếng
```

---

## Tác giả

**tpc-pascal** — [GitHub](https://github.com/tpc-pascal)

---

## License

MIT — xem file [LICENSE](./LICENSE).
