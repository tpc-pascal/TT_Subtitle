import gradio as gr
from pathlib import Path

from utils.search import (
    PLATFORMS, SEARCH_PREFIX, search_videos,
    download_audio, download_video, get_video_info,
)
from utils.subtitle import transcribe, segments_to_srt, segments_to_txt, save_srt, save_txt
from utils.translate import translate_segments
from utils.tts import generate_dub
from utils.video_editor import burn_subtitles, merge_audio_dub, burn_and_dub

OUTPUT_DIR = Path("downloads")
OUTPUT_DIR.mkdir(exist_ok=True)

LANGUAGES = [
    "Tiếng Trung", "Tiếng Anh", "Tiếng Việt", "Tiếng Nhật", "Tiếng Hàn",
]

PLATFORM_LIST = PLATFORMS + ["Khác (dán link)"]

def on_platform_change(platform):
    can_search = platform in SEARCH_PREFIX
    return (
        gr.update(visible=can_search),
        gr.update(visible=not can_search),
        gr.update(visible=can_search),
    )

def search_videos_fn(platform, keyword, max_results):
    if not keyword.strip():
        return [], "Vui lòng nhập từ khóa"
    try:
        videos = search_videos(platform, keyword.strip(), int(max_results))
        if not videos:
            return [], f"Không tìm thấy video nào cho {platform}"
        choices = []
        for v in videos:
            dur = v["duration"]
            label = f"{v['title'][:70]} - {v['channel']} ({dur//60}:{dur%60:02d})"
            choices.append((label, v["url"]))
        return choices, f"Tìm thấy {len(videos)} video"
    except Exception as e:
        return [], f"Lỗi tìm kiếm: {str(e)}"

def process_video(video_url, source_lang, target_lang, output_format, enable_dub, progress=gr.Progress()):
    if not video_url:
        return None, "", None, "Vui lòng nhập URL hoặc chọn video"

    try:
        progress(0.05, desc="Đang lấy thông tin video...")
        info = get_video_info(video_url)

        progress(0.1, desc="Đang tải âm thanh...")
        audio_path = download_audio(video_url)

        progress(0.2, desc="Đang nhận dạng giọng nói (ASR)...")
        segments = transcribe(audio_path, source_lang)
        sub_srt = segments_to_srt(segments)

        if target_lang != source_lang:
            progress(0.5, desc="Đang dịch phụ đề...")
            segments = translate_segments(segments, source_lang, target_lang)
            sub_srt = segments_to_srt(segments)

        progress(0.7, desc="Đang xuất file...")
        srt_path = save_srt(segments)
        txt_path = save_txt(segments)

        result_file = srt_path if output_format in ("SRT", "Cả hai") else txt_path

        if output_format in ("Sub vào video", "Cả hai"):
            progress(0.75, desc="Đang tải video...")
            video_path = download_video(video_url)
            progress(0.8, desc="Đang sub phụ đề vào video...")
            result_file = burn_subtitles(video_path, segments)

        if enable_dub:
            progress(0.85, desc="Đang tạo giọng đọc (TTS)...")
            audio_segs = generate_dub(segments, target_lang)
            progress(0.9, desc="Đang ghép giọng đọc vào video...")

            if output_format in ("Sub vào video", "Cả hai"):
                video_path = download_video(video_url)
                result_file = burn_and_dub(video_path, segments, audio_segs)
            else:
                video_path = download_video(video_url)
                result_file = merge_audio_dub(video_path, audio_segs)

        progress(1.0, desc="Hoàn tất!")
        is_video = result_file and Path(result_file).suffix in (".mp4", ".mkv", ".webm")
        return result_file, sub_srt, result_file if is_video else None, "✅ Xử lý thành công!"

    except Exception as e:
        return None, "", None, f"❌ Lỗi: {str(e)}"

def build_ui():
    with gr.Blocks(title="TT_Subtitle - Công cụ dịch phim", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🎬 TT_Subtitle
            ### Công cụ trích xuất, dịch phụ đề và lồng tiếng đa nền tảng

            **Quy trình:** Chọn nền tảng → Tìm kiếm / Dán link → Chọn ngôn ngữ → Xử lý
            """
        )

        platform = gr.Dropdown(
            label="🎯 Nền tảng",
            choices=PLATFORM_LIST,
            value="YouTube",
        )

        with gr.Row():
            with gr.Column(scale=1):
                keyword_input = gr.Textbox(
                    label="Từ khóa tìm kiếm",
                    placeholder="Nhập từ khóa...",
                    visible=True,
                )
                max_results = gr.Slider(3, 20, 10, step=1, label="Số kết quả", visible=True)
                search_btn = gr.Button("🔍 Tìm kiếm", variant="primary", visible=True)
                search_status = gr.Textbox(label="Trạng thái", interactive=False)

            with gr.Column(scale=2):
                video_selector = gr.Dropdown(label="Chọn video", choices=[], interactive=True)

        url_input = gr.Textbox(
            label="URL video",
            placeholder="Dán link video từ bất kỳ nền tảng nào...",
            visible=False,
        )

        with gr.Row():
            with gr.Column():
                source_lang = gr.Dropdown(label="Ngôn ngữ gốc", choices=LANGUAGES, value="Tiếng Trung")
                target_lang = gr.Dropdown(label="Ngôn ngữ dịch", choices=LANGUAGES, value="Tiếng Việt")
                output_format = gr.Radio(
                    label="Định dạng đầu ra",
                    choices=["SRT", "TXT", "Sub vào video", "Cả hai"],
                    value="SRT",
                )
                enable_dub = gr.Checkbox(label="Lồng tiếng (TTS)", value=False)

            with gr.Column():
                process_btn = gr.Button("🚀 Xử lý", variant="primary", size="lg")
                process_status = gr.Textbox(label="Trạng thái", interactive=False)

        with gr.Row():
            subtitle_output = gr.Textbox(label="Phụ đề", lines=10, interactive=False)

        with gr.Row():
            output_file = gr.File(label="📥 Tải file kết quả")
            preview_video = gr.Video(label="▶️ Xem trước video", autoplay=False)

        # --- Events ---
        platform.change(
            on_platform_change,
            platform,
            [keyword_input, url_input, search_btn],
        )

        search_btn.click(
            search_videos_fn,
            [platform, keyword_input, max_results],
            [video_selector, search_status],
        )

        url_state = gr.State("")

        def update_url_state(video_url, direct_url, platform):
            if platform in SEARCH_PREFIX:
                return video_url
            return direct_url

        video_selector.change(update_url_state, [video_selector, url_input, platform], url_state)
        url_input.change(update_url_state, [video_selector, url_input, platform], url_state)

        process_btn.click(
            process_video,
            [url_state, source_lang, target_lang, output_format, enable_dub],
            [output_file, subtitle_output, preview_video, process_status],
        )

        gr.Markdown(
            """
            ---
            **Lưu ý:**
            - Hỗ trợ **tất cả nền tảng** mà yt-dlp hỗ trợ (1800+ site): YouTube, Bilibili, Douyin, TikTok, Facebook, Instagram, Twitter, Twitch, Vimeo, SoundCloud...
            - Tìm kiếm nội bộ có sẵn cho: YouTube, Bilibili, SoundCloud. Các nền tảng khác dán link trực tiếp.
            - ASR (Whisper), dịch thuật (NLLB-200), TTS (Edge-TTS) hoạt động trên mọi nguồn video.
            - File tự động xóa khi session kết thúc.
            """
        )

    return demo

demo = build_ui()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
