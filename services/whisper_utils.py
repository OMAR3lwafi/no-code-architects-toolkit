# Utility helpers for Whisper model creation and language validation
import whisper

try:
    import torch
except Exception:  # pragma: no cover
    torch = None

from whisper.tokenizer import LANGUAGES, TO_LANGUAGE_CODE

SUPPORTED_LANGUAGE_CODES = set(TO_LANGUAGE_CODE.values()) | set(TO_LANGUAGE_CODE.keys()) | set(LANGUAGES.keys()) | set(LANGUAGES.values())


def get_default_language() -> str:
    return "ar"


def normalize_language(lang: str | None) -> str:
    """Return a normalized 2-letter language code if possible, defaulting to 'ar'.
    Accepts both names like 'Arabic' and codes like 'ar'. Raises ValueError if unsupported.
    """
    if not lang:
        lang = get_default_language()
    lang = str(lang).strip().lower()
    # Map full language name to code if needed
    if lang in TO_LANGUAGE_CODE:
        code = TO_LANGUAGE_CODE[lang]
    else:
        code = lang
    if code not in SUPPORTED_LANGUAGE_CODES:
        raise ValueError(f"Unsupported language: {lang}. Please provide a valid Whisper language code, e.g. 'ar'.")
    return code


def validate_language(lang: str | None) -> str:
    """Alias to normalize_language for external callers."""
    return normalize_language(lang)


def detect_device_has_gpu() -> bool:
    try:
        return bool(torch and torch.cuda.is_available())
    except Exception:
        return False


def get_whisper_model(language: str | None = None, size: str | None = "large"):
    """Factory Method for creating a Whisper model.
    - Validates and normalizes language (defaults to Arabic 'ar').
    - Picks model size. If size is None, selects 'large' when GPU is available else 'medium'.
    """
    _ = normalize_language(language)  # ensure early validation, value not used by load_model

    if not size:
        size = "large" if detect_device_has_gpu() else "medium"

    # Always prefer the requested size; caller can choose to pass None to auto-pick
    model = whisper.load_model(size)
    return model
