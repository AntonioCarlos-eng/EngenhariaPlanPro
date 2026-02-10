# core/v4/detector_vigas.py
import re
from typing import List, Dict, Any

# Aceita: V8, V10, VM1, VM2, VIGA V8 etc (bem conservador)
RE_VIGA = re.compile(r"^(V(M)?\s*\d{1,3})$")  # V8, VM1, V 10

def detectar_vigas(textos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Retorna lista de labels de vigas:
    [{"viga":"V8","x":..,"y":..,"text":..}]
    """
    vigas = []
    for t in textos:
        s = t.get("text", "").upper().strip()
        s = s.replace(" ", "")
        m = RE_VIGA.match(s)
        if not m:
            continue
        v = m.group(1)
        # Normaliza "VM1" e "V10"
        v = v.replace(" ", "")
        vigas.append({"viga": v, "x": t["x"], "y": t["y"], "text": t.get("text", "")})
    return vigas
