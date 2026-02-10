# core/v4/reader_dxf.py  (ROBUSTO: TEXT + MTEXT)
import ezdxf
import re

def _norm(s: str) -> str:
    if s is None:
        return ""
    # remove quebras e excesso de espaços
    s = s.replace("\r", " ").replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _mtext_to_str(e) -> str:
    # ezdxf MTEXT: tenta pegar texto "plain"
    try:
        return e.plain_text()
    except Exception:
        pass
    try:
        return e.text
    except Exception:
        pass
    try:
        return e.dxf.text
    except Exception:
        return ""

def ler_textos_dxf(caminho_dxf: str):
    """
    Retorna lista de dicts:
      {"texto": str, "x": float, "y": float}
    Lê TEXT + MTEXT (e ignora resto).
    """
    doc = ezdxf.readfile(caminho_dxf)
    msp = doc.modelspace()

    out = []

    for e in msp:
        t = e.dxftype()

        if t == "TEXT":
            try:
                texto = _norm(e.dxf.text)
                x, y = float(e.dxf.insert.x), float(e.dxf.insert.y)
            except Exception:
                continue

        elif t == "MTEXT":
            try:
                texto = _norm(_mtext_to_str(e))
                # MTEXT usa insert também
                x, y = float(e.dxf.insert.x), float(e.dxf.insert.y)
            except Exception:
                continue

        else:
            continue

        if texto:
            out.append({"texto": texto, "x": x, "y": y})

    return out
