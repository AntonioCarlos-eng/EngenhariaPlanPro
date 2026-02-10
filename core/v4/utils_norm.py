# core/v4/utils_norm.py
import re

def norm_text(s: str) -> str:
    if not s:
        return ""
    s = s.replace("\n", " ").replace("\t", " ")
    s = s.replace("%%C", "Ø").replace("%%c", "Ø")
    s = s.replace("Φ", "Ø").replace("φ", "Ø")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def upper_norm(s: str) -> str:
    return norm_text(s).upper()

def safe_float(x: str):
    try:
        return float(x.replace(",", "."))
    except Exception:
        return None

def safe_int(x: str):
    try:
        return int(x)
    except Exception:
        return None
