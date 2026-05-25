import whisper
import re
from pathlib import Path

OUTPUT_DIR = Path("downloads")
OUTPUT_DIR.mkdir(exist_ok=True)

_model = None

def get_model(model_size: str = "small"):
    global _model
    if _model is None:
        _model = whisper.load_model(model_size)
    return _model

def transcribe(audio_path: str, source_lang: str = "zh") -> list[dict]:
    model = get_model()
    lang_code = {"tiếng trung": "zh", "tiếng anh": "en", "tiếng việt": "vi",
                 "chinese": "zh", "english": "en", "vietnamese": "vi"}.get(source_lang.lower(), source_lang)
    result = model.transcribe(audio_path, language=lang_code, task="transcribe")
    segments = []
    for seg in result.get("segments", []):
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip(),
        })
    return segments

def segments_to_srt(segments: list[dict]) -> str:
    def fmt_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for i, seg in enumerate(segments, 1):
        start = fmt_time(seg["start"])
        end = fmt_time(seg["end"])
        lines.append(f"{i}\n{start} --> {end}\n{seg['text']}\n")
    return "\n".join(lines)

def segments_to_txt(segments: list[dict]) -> str:
    return "\n".join(seg["text"] for seg in segments)

def save_srt(segments: list[dict], filename: str = "subtitle.srt") -> str:
    path = OUTPUT_DIR / filename
    path.write_text(segments_to_srt(segments), encoding="utf-8")
    return str(path)

def save_txt(segments: list[dict], filename: str = "subtitle.txt") -> str:
    path = OUTPUT_DIR / filename
    path.write_text(segments_to_txt(segments), encoding="utf-8")
    return str(path)
