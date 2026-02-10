import math
from collections import defaultdict

def _dist2(a, b):
    dx = a["x"] - b["x"]
    dy = a["y"] - b["y"]
    return dx*dx + dy*dy

def associar_texto_a_viga(texto, vigas_xy, max_dist=5000.0):
    """
    Atribui cada texto à viga mais próxima do label (V8, V9, etc).
    Isso evita "contaminação" entre vigas.
    """
    if not vigas_xy:
        return None

    best = None
    best_d2 = None
    for nome, (vx, vy) in vigas_xy.items():
        dx = texto["x"] - vx
        dy = texto["y"] - vy
        d2 = dx*dx + dy*dy
        if best_d2 is None or d2 < best_d2:
            best_d2 = d2
            best = nome

    if best_d2 is not None and best_d2 <= (max_dist * max_dist):
        return best
    return None

def clusterizar_por_proximidade(textos, raio=120.0):
    """
    Clusterização espacial rápida usando grade (grid hashing).
    Retorna lista de clusters, cada cluster = lista de textos.
    """
    if not textos:
        return []

    cell = raio  # tamanho da célula
    grid = defaultdict(list)

    for i, t in enumerate(textos):
        cx = int(t["x"] // cell)
        cy = int(t["y"] // cell)
        grid[(cx, cy)].append(i)

    visited = set()
    clusters = []
    r2 = raio * raio

    for i in range(len(textos)):
        if i in visited:
            continue

        # BFS
        queue = [i]
        visited.add(i)
        comp = []

        while queue:
            idx = queue.pop()
            comp.append(textos[idx])

            cx = int(textos[idx]["x"] // cell)
            cy = int(textos[idx]["y"] // cell)

            for nx in (cx-1, cx, cx+1):
                for ny in (cy-1, cy, cy+1):
                    for j in grid.get((nx, ny), []):
                        if j in visited:
                            continue
                        if _dist2(textos[idx], textos[j]) <= r2:
                            visited.add(j)
                            queue.append(j)

        clusters.append(comp)

    return clusters

def clusterizar_por_viga(textos, vigas_xy, raio_cluster=120.0, max_dist_label=5000.0):
    """
    1) Atribui texto -> viga mais próxima (sem misturar)
    2) Clusteriza por proximidade dentro de cada viga
    Retorna dict: { "V8": [cluster1, cluster2...], ... }
    """
    por_viga = defaultdict(list)

    for t in textos:
        v = associar_texto_a_viga(t, vigas_xy, max_dist=max_dist_label)
        if v is not None:
            por_viga[v].append(t)

    saida = {}
    for viga, lista in por_viga.items():
        saida[viga] = clusterizar_por_proximidade(lista, raio=raio_cluster)

    return saida
