# core/v4/associador.py
import math

def dist(a, b):
    dx = a["x"] - b["x"]
    dy = a["y"] - b["y"]
    return math.hypot(dx, dy)

def associar_textos_a_vigas(textos, vigas, max_dist=1200.0):
    """
    Associa cada texto à VIGA mais próxima (sem contaminação).
    Retorna dict: { "V8": [textos...], "V9": [...], ... }
    """
    mapa = {v["viga"]: [] for v in vigas}

    for t in textos:
        s = (t.get("text") or "").strip()
        if not s:
            continue

        # pula o próprio label de viga
        if s.strip().upper().replace(" ", "") in mapa:
            continue

        best = None
        bestd = 1e18
        for v in vigas:
            d = dist(t, v)
            if d < bestd:
                bestd = d
                best = v

        if best and bestd <= max_dist:
            mapa[best["viga"]].append(t)

    return mapa
