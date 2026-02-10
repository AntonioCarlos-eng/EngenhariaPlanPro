# core/v4/associador.py
import math
from collections import defaultdict

def dist2(a, b):
    dx = a["x"] - b["x"]
    dy = a["y"] - b["y"]
    return dx*dx + dy*dy

def raio_automatico(labels):
    """
    Define um raio de associação que corta contaminação entre vigas.
    Estratégia:
      - calcula distância média ao vizinho mais próximo entre labels
      - usa 45% dessa distância como raio
    """
    if len(labels) < 2:
        return 999999.0

    nearest = []
    for i, a in enumerate(labels):
        best = None
        for j, b in enumerate(labels):
            if i == j:
                continue
            d = dist2(a, b)
            if best is None or d < best:
                best = d
        if best is not None:
            nearest.append(math.sqrt(best))

    if not nearest:
        return 999999.0

    avg = sum(nearest) / len(nearest)
    return max(150.0, avg * 0.45)  # mínimo 150 unidades do DXF

def associar(chamadas, labels):
    """
    Para cada chamada (2 N1 Ø10 C=295), acha a label de viga mais próxima
    dentro de um raio automático. Se não couber, descarta.
    """
    if not labels:
        return []

    R = raio_automatico(labels)
    R2 = R * R

    out = []
    for c in chamadas:
        best = None
        best_d2 = None
        for lb in labels:
            d2 = dist2(c, lb)
            if best_d2 is None or d2 < best_d2:
                best_d2 = d2
                best = lb

        if best is not None and best_d2 is not None and best_d2 <= R2:
            c2 = dict(c)
            c2["viga"] = best["viga"]
            c2["d_assoc"] = math.sqrt(best_d2)
            out.append(c2)
        # fora do raio => lixo global (evita “N que não existe na viga”)
    return out

def agregar(itens):
    """
    Soma por (viga, N, bitola, comprimento_cm)
    """
    acc = defaultdict(lambda: {"q": 0})
    for it in itens:
        key = (it["viga"], it["n"], float(it["d"]), float(it["L_cm"]))
        acc[key]["q"] += int(it["q"])

    rows = []
    for (viga, n, d, L_cm), v in sorted(acc.items(), key=lambda k: (k[0][0], int(k[0][1][1:]), k[0][2], k[0][3])):
        rows.append({
            "viga": viga,
            "posicao": n,
            "bitola_mm": d,
            "comprimento_cm": L_cm,
            "quantidade": v["q"],
        })
    return rows
