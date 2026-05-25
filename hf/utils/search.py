import subprocess
import json
from pathlib import Path

OUTPUT_DIR = Path("downloads")
OUTPUT_DIR.mkdir(exist_ok=True)

PLATFORMS = [
    "YouTube",
    "Bilibili",
    "Douyin",
    "TikTok",
    "Facebook",
    "Twitter / X",
    "Instagram",
    "Twitch",
    "Vimeo",
    "Dailymotion",
    "SoundCloud",
    "Rumble",
    "Odysee",
    "Reddit",
    "LinkedIn",
    "Pinterest",
    "Snapchat",
    "Triller",
    "VK",
    "Youku",
    "IQIYI",
    "Tencent Video",
    "NetEase",
    "Kuaishou",
    "Huya",
    "Douyu",
    "Weibo",
    "Mixcloud",
    "Rutube",
    "Bandcamp",
]

SEARCH_PREFIX = {
    "YouTube": "ytsearch",
    "Bilibili": "bilisearch",
    "SoundCloud": "scsearch",
    "Dailymotion": "dailymotionsearch",
    "NicoNico": "nicosearch",
    "Google Video": "gvsearch",
}

def search_videos(platform: str, keyword: str, max_results: int = 10) -> list[dict]:
    prefix = SEARCH_PREFIX.get(platform)
    if not prefix:
        return []

    cmd = [
        "yt-dlp",
        f"{prefix}{max_results}:{keyword}",
        "--dump-json",
        "--no-download",
        "--flat-playlist",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    videos = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        data = json.loads(line)
        url = data.get("url") or data.get("webpage_url") or f"https://youtube.com/watch?v={data.get('id', '')}"
        videos.append({
            "id": data.get("id", ""),
            "title": data.get("title", ""),
            "channel": data.get("channel", "") or data.get("uploader", ""),
            "duration": data.get("duration", 0),
            "thumbnail": data.get("thumbnail", ""),
            "url": url,
            "view_count": data.get("view_count", 0),
            "platform": platform,
        })
    return videos

def download_audio(video_url: str) -> str:
    output_path = str(OUTPUT_DIR / "%(id)s.%(ext)s")
    cmd = [
        "yt-dlp",
        "-x", "--audio-format", "wav",
        "--audio-quality", "0",
        "--no-playlist",
        "-o", output_path,
        video_url,
    ]
    subprocess.run(cmd, check=True, timeout=600)
    for f in OUTPUT_DIR.iterdir():
        if f.suffix == ".wav":
            return str(f)
    raise FileNotFoundError("Could not find downloaded audio file")

def download_video(video_url: str) -> str:
    output_path = str(OUTPUT_DIR / "%(id)s.%(ext)s")
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--no-playlist",
        "-o", output_path,
        video_url,
    ]
    subprocess.run(cmd, check=True, timeout=600)
    for f in OUTPUT_DIR.iterdir():
        if f.suffix in (".mp4", ".mkv", ".webm"):
            return str(f)
    raise FileNotFoundError("Could not find downloaded video file")

def get_video_info(video_url: str) -> dict:
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-download",
        video_url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    data = json.loads(result.stdout.strip())
    return {
        "id": data.get("id", ""),
        "title": data.get("title", ""),
        "channel": data.get("channel", "") or data.get("uploader", ""),
        "duration": data.get("duration", 0),
        "description": data.get("description", ""),
        "thumbnail": data.get("thumbnail", ""),
        "url": video_url,
        "extractor": data.get("extractor", ""),
    }

def cleanup():
    for f in OUTPUT_DIR.iterdir():
        f.unlink()
