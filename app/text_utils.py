import re
import unicodedata


def normalize_text(value: str) -> str:
    """Normalize text for deterministic matching."""
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def extract_class_numbers(value: str) -> list[int]:
    classes = []
    for token in re.findall(r"\b\d{1,2}\b", value or ""):
        parsed = int(token)
        if 1 <= parsed <= 45:
            classes.append(parsed)
    return sorted(set(classes))
