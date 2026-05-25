from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re

MODEL_NAME = "facebook/nllb-200-distilled-600M"

LANG_MAP = {
    "tiếng trung": "zho_Hans",
    "tiếng anh": "eng_Latn",
    "tiếng việt": "vie_Latn",
    "tiếng nhật": "jpn_Jpan",
    "tiếng hàn": "kor_Hang",
    "chinese": "zho_Hans",
    "english": "eng_Latn",
    "vietnamese": "vie_Latn",
    "japanese": "jpn_Jpan",
    "korean": "kor_Hang",
}

_cache = {}

def _get_model():
    if "model" not in _cache:
        _cache["tokenizer"] = AutoTokenizer.from_pretrained(MODEL_NAME)
        _cache["model"] = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    return _cache["tokenizer"], _cache["model"]

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    src_code = LANG_MAP.get(source_lang.lower().strip())
    tgt_code = LANG_MAP.get(target_lang.lower().strip())

    if not src_code or not tgt_code:
        return f"[Unsupported language: {source_lang} -> {target_lang}]"

    if src_code == tgt_code:
        return text

    tokenizer, model = _get_model()
    tokenizer.src_lang = src_code

    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    forced_bos_token_id = tokenizer.convert_tokens_to_ids(tgt_code)
    translated = model.generate(**inputs, forced_bos_token_id=forced_bos_token_id, max_length=512)
    result = tokenizer.decode(translated[0], skip_special_tokens=True)
    return result

def translate_segments(segments: list[dict], source_lang: str, target_lang: str) -> list[dict]:
    translated = []
    for seg in segments:
        translated_text = translate_text(seg["text"], source_lang, target_lang)
        translated.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": translated_text,
        })
    return translated
