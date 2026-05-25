import asyncio
import edge_tts
from pathlib import Path

OUTPUT_DIR = Path("downloads")
OUTPUT_DIR.mkdir(exist_ok=True)

VOICE_MAP = {
    "vi": "vi-VN-HoaiMyNeural",
    "en": "en-US-JennyNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
}

LANG_MAP = {
    "tiếng việt": "vi", "tiếng anh": "en", "tiếng trung": "zh",
    "vietnamese": "vi", "english": "en", "chinese": "zh",
}

def _get_voice(lang: str) -> str:
    code = LANG_MAP.get(lang.lower(), lang)
    return VOICE_MAP.get(code, "en-US-JennyNeural")

async def _generate_tts(text: str, voice: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def generate_dub(segments: list[dict], language: str) -> str:
    voice = _get_voice(language)
    audio_segments = []

    for i, seg in enumerate(segments):
        output_path = str(OUTPUT_DIR / f"seg_{i:04d}.mp3")
        asyncio.run(_generate_tts(seg["text"], voice, output_path))
        audio_segments.append({
            "path": output_path,
            "start": seg["start"],
            "end": seg["end"],
        })

    return audio_segments
