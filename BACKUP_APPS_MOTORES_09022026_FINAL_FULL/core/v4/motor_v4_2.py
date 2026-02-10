# core/v4/motor_v4_2.py  (V4.2.1 ROBUSTO)
import os
import sys
import csv

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

from reader_dxf import ler_textos_dxf
from detector_vigas import detectar_vigas
from associador import associar_textos_a_vigas
from parser_chamadas import parse_chamada

def kg_por_metro(bitola_mm: float) -> float:
    d = float(bitola_mm)
    return (d * d) / 162.0

def _cluster_linhas(textos, y_tol=6.0):
    """
    Junta textos por "linha" (mesmo Y) para resolver DXF que quebra tokens.
    Retorna lista de strings já concatenadas.
    """
    # ordena por y desc (topo->baixo) e x asc
    pts = sorted(textos, key=lambda t: (-float(t["y"]), float(t["x"])))

    linhas = []  # cada item: {"y": y_ref, "tokens": [ (x, text) ... ]}
    for t in pts:
        s = (t.get("text") or "").strip()
        if not s:
            continue

        y = float(t["y"])
        x = float(t["x"])

        # tenta encaixar na linha existente
        placed = False
        for ln in linhas:
            if abs(ln["y"] - y) <= y_tol:
                ln["tokens"].append((x, s))
                placed = True
                break
        if not placed:
            linhas.append({"y": y, "tokens": [(x, s)]})

    # monta string final por linha (ordenando por x)
    out = []
    for ln in linhas:
        toks = [tx for _, tx in sorted(ln["tokens"], key=lambda a: a[0])]
        joined = " ".join(toks)
        out.append(joined)

    return out

def main(caminho_dxf: str):
    if not os.path.exists(caminho_dxf):
        raise FileNotFoundError(f"DXF não encontrado: {caminho_dxf}")

    textos = ler_textos_dxf(caminho_dxf)
    print(f"[V4.2] Textos lidos: {len(textos)}")

    vigas = detectar_vigas(textos)
    print(f"[V4.2] Vigas detectadas: {len(vigas)}")
    for v in vigas:
        print(f" - {v['viga']}")

    if not vigas:
        print("[V4.2] Nenhuma viga detectada. Abortando.")
        return

    max_dist = 1200.0
    mapa = associar_textos_a_vigas(textos, vigas, max_dist=max_dist)

    itens = []
    parse_ok = 0
    parse_fail = 0
    mostrados_debug = 0

    for viga_nome, lista in mapa.items():
        # junta tokens por linha dentro da viga
        linhas = _cluster_linhas(lista, y_tol=6.0)

        for linha in linhas:
            # só tenta parsear coisa com cara de chamada
            up = linha.upper()
            if ("N" not in up) or (("C" not in up) and ("L" not in up)):
                continue

            p = parse_chamada(linha)
            if not p:
                parse_fail += 1

                # DEBUG: mostra umas falhas pra você ver o formato real
                if mostrados_debug < 12:
                    print(f"[DEBUG FAIL] {viga_nome}: {linha}")
                    mostrados_debug += 1
                continue

            parse_ok += 1
            itens.append({
                "viga": viga_nome,
                "pos": p["pos"],
                "bitola_mm": p["bitola_mm"],
                "comp_m": p["comp_m"],
                "qtd": p["qtd"],
                "raw": p["raw"],
            })

    print(f"[V4.2] Chamadas parse_ok: {parse_ok} | parse_fail: {parse_fail}")

    # agrega
    agg = {}
    for it in itens:
        k = (it["viga"], it["pos"], round(it["bitola_mm"], 2), round(it["comp_m"], 3))
        if k not in agg:
            agg[k] = {"viga": it["viga"], "pos": it["pos"], "bitola_mm": it["bitola_mm"], "comp_m": it["comp_m"], "qtd": 0}
        agg[k]["qtd"] += int(it["qtd"])

    saida = []
    total_barras = 0
    total_peso = 0.0

    for _, r in sorted(agg.items(), key=lambda x: (x[1]["viga"], x[1]["pos"], x[1]["bitola_mm"], x[1]["comp_m"])):
        qtd = int(r["qtd"])
        comp_m = float(r["comp_m"])
        bit = float(r["bitola_mm"])
        peso = qtd * comp_m * kg_por_metro(bit)

        total_barras += qtd
        total_peso += peso

        saida.append({
            "viga": r["viga"],
            "pos": r["pos"],
            "bitola_mm": round(bit, 2),
            "qtd": qtd,
            "comp_m": round(comp_m, 3),
            "peso_kg": round(peso, 3),
        })

    print("\n================ RESULTADO V4.2.1 ================")
    print(f"Itens: {len(saida)} | Barras: {total_barras} | Peso: {total_peso:.2f} kg\n")
    for r in saida[:60]:
        print(f"{r['viga']:>4} | {r['pos']:<4} | Ø {r['bitola_mm']:>5} | qtd {r['qtd']:>4} | comp {r['comp_m']:>6} m | {r['peso_kg']:>7} kg")
    if len(saida) > 60:
        print(f"... +{len(saida)-60} linhas")

    # CSV
    base = os.path.splitext(os.path.basename(caminho_dxf))[0]
    out_csv = os.path.join(os.path.dirname(caminho_dxf), f"{base}_V4_2_1.csv")

    fieldnames = ["viga", "pos", "bitola_mm", "qtd", "comp_m", "peso_kg"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", delimiter=";")
        w.writeheader()
        w.writerows(saida)

    print(f"\n[V4.2] CSV gerado: {out_csv}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:\n  python core\\v4\\motor_v4_2.py \"C:\\caminho\\arquivo.dxf\"")
        raise SystemExit(2)
    main(sys.argv[1])
