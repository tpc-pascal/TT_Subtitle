import subprocess
from pathlib import Path
import srt
from datetime import timedelta

OUTPUT_DIR = Path("downloads")
OUTPUT_DIR.mkdir(exist_ok=True)

def _write_srt(segments: list[dict], srt_path: str):
    subs = []
    for i, seg in enumerate(segments):
        subs.append(srt.Subtitle(
            index=i + 1,
            start=timedelta(seconds=seg["start"]),
            end=timedelta(seconds=seg["end"]),
            content=seg["text"],
        ))
    Path(srt_path).write_text(srt.compose(subs), encoding="utf-8")

def burn_subtitles(video_path: str, segments: list[dict], output_name: str = "output_subbed.mp4") -> str:
    output_path = str(OUTPUT_DIR / output_name)
    srt_path = str(OUTPUT_DIR / "temp_sub.srt")
    _write_srt(segments, srt_path)

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"subtitles={srt_path}",
        "-c:a", "copy",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=600)
    return output_path

def merge_audio_dub(video_path: str, audio_segments: list[dict], output_name: str = "output_dubbed.mp4") -> str:
    output_path = str(OUTPUT_DIR / output_name)

    filter_parts = []
    inputs = [video_path]
    for i, seg in enumerate(audio_segments):
        inputs.extend(["-itsoffset", f"{seg['start']}", "-i", seg["path"]])
        filter_parts.append(f"[{i + 1}:a]")

    if not audio_segments:
        return video_path

    mix_inputs = "".join(filter_parts)
    amix_count = len(audio_segments) + 1
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
    ]
    for seg in audio_segments:
        cmd.extend(["-itsoffset", f"{seg['start']}", "-i", seg["path"]])

    filter_complex = f"[0:a]{mix_inputs}amix=inputs={amix_count}:duration=first[audio]"
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[audio]",
        "-c:v", "copy",
        output_path,
    ])
    subprocess.run(cmd, check=True, capture_output=True, timeout=600)
    return output_path

def burn_and_dub(video_path: str, subtitle_segments: list[dict],
                 audio_segments: list[dict], output_name: str = "output_final.mp4") -> str:
    output_path = str(OUTPUT_DIR / output_name)
    srt_path = str(OUTPUT_DIR / "temp_sub.srt")
    _write_srt(subtitle_segments, srt_path)

    inputs = ["ffmpeg", "-y", "-i", video_path]
    filter_parts = [f"[0:a]"]
    for i, seg in enumerate(audio_segments):
        inputs.extend(["-itsoffset", f"{seg['start']}", "-i", seg["path"]])
        filter_parts.append(f"[{i + 1}:a]")

    mix_inputs = "".join(filter_parts)
    amix_count = len(audio_segments) + 1
    filter_complex = f"[0:a]{mix_inputs}amix=inputs={amix_count}:duration=first[audio]"

    cmd = inputs + [
        "-filter_complex", f"{filter_complex};subtitles={srt_path}",
        "-map", "0:v",
        "-map", "[audio]",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=600)
    return output_path

def cleanup():
    for f in OUTPUT_DIR.iterdir():
        if f.name.startswith("temp_") or f.name.startswith("seg_"):
            f.unlink()
