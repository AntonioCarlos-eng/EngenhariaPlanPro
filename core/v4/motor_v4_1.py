# core/v4/motor_v4_1.py  (V4.1.1)
import os
import re
import csv
import math
import sys
from collections import defaultdict

from reader_dxf import ler_textos_dxf


# -----------------------------
# CONFIG
# -----------------------------
ACO_KG_M = {
    5.0: 0.154,
    6.3: 0.245,
    8.0: 0.395,
    10.0: 0.617,
    12.5: 0.963,
    16.0: 1.578,
    20.0: 2.466,
    25.0: 3.853,
    32.0: 6.313,
}
BITOLAS_VALIDAS = set(ACO_KG_M.keys())

# Labels
RE_VIGA = re.compile(r'^(V(M)?\d+)$', re.IGNORECASE)      # V8, V10, VM1, VM2...
RE_POS  = re.compile(r'\bN(\d{1,3})\b', re.IGNORECASE)    # N1..N999

# Diâmetro: Ø 10, %%c 6.3, Φ 12.5, etc
RE_DIA = re.compile(r'(?:Ø|Φ|φ|%%C|%%c)\s*([0-9]+(?:[.,][0-9]+)?)', re.IGNORECASE)

# Comprimento: C=295 / L=295 / C/22 / (320)
RE_LEN_CEQ = re.compile(r'\b[CL]\s*=\s*([0-9]+(?:[.,][0-9]+)?)\b', re.IGNORECASE)
RE_LEN_CSL = re.compile(r'\bC\s*[/\\]\s*([0-9]+(?:[.,][0-9]+)?)\b', re.IGNORECASE)
RE_LEN_PAR = re.compile(r'\(([0-9]{2,5})\)')  # (320) (295) (141) etc.

# Quantidade (forma clássica: "15 N10 ...")
RE_QTD_BEFORE_N = re.compile(r'(^|\s)(\d{1,4})(?=\s+N\d{1,3}\b)', re.IGNORECASE)

# Quantidade fallback: se vier "N10 ... qtd 15" (raro)
RE_QTD_WORD = re.compile(r'\bQTD\s*[:=]?\s*(\d{1,4})\b', re.IGNORECASE)


def _to_float(s: str):
    s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None


def detectar_vigas(textos):
    vigas = {}
    for t in textos:
        s = (t.get("texto") or "").strip().upper()
        m = RE_VIGA.match(s)
        if m:
            nome = m.group(1).upper()
            if nome not in vigas:
                vigas[nome] = {"x": float(t["x"]), "y": float(t["y"])}
    return vigas


def _tem_bitola_por_numero(texto: str):
    """
    Fallback: procura um número que seja exatamente uma bitola válida
    (ex: '6.3', '10', '12.5', '20')
    """
    up = texto.upper().replace(",", ".")
    nums = re.findall(r'(?<!\d)(\d+(?:\.\d+)?)(?!\d)', up)
    for n in nums:
        v = _to_float(n)
        if v is None:
            continue
        v = round(v, 1)
        if v in BITOLAS_VALIDAS:
            return v
        vi = float(int(round(v)))
        if vi in BITOLAS_VALIDAS:
            return vi
    return None


def detectar_chamadas(textos):
    """
    Melhor filtro pra não tentar parse em qualquer texto com 'N'.
    Regras mínimas:
      - tem posição Nxx
      - e tem indício de diâmetro (%%c/Ø/Φ) OU um número que bate em bitola válida
      - e tem indício de comprimento (C=, L=, C/, ou (nnn))
    """
    out = []
    for t in textos:
        s = (t.get("texto") or "").strip()
        if not s:
            continue
        up = s.upper()

        if not RE_POS.search(up):
            continue

        tem_dia = bool(RE_DIA.search(up)) or (_tem_bitola_por_numero(up) is not None)
        if not tem_dia:
            continue

        tem_len = bool(RE_LEN_CEQ.search(up) or RE_LEN_CSL.search(up) or RE_LEN_PAR.search(up))
        if not tem_len:
            continue

        out.append({"texto": s, "x": float(t["x"]), "y": float(t["y"])})
    return out


def extrair_qtd(texto: str):
    up = texto.upper()

    m = RE_QTD_BEFORE_N.search(up)
    if m:
        try:
            return int(m.group(2))
        except Exception:
            pass

    m = RE_QTD_WORD.search(up)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            pass

    # fallback seguro: se nada encontrado, assume 1 (muitos detalhes vêm sem qtd explícita)
    return 1


def extrair_pos(texto: str):
    m = RE_POS.search(texto.upper())
    if not m:
        return None
    return f"N{int(m.group(1))}"


def extrair_bitola_mm(texto: str):
    up = texto.upper()

    m = RE_DIA.search(up)
    if m:
        val = _to_float(m.group(1))
        if val is None:
            return None
        valr = round(val, 1)
        if valr in BITOLAS_VALIDAS:
            return valr
        vali = float(int(round(val)))
        if vali in BITOLAS_VALIDAS:
            return vali
        return valr

    # fallback: número puro (6.3 / 10 / 12.5 / 20 etc)
    return _tem_bitola_por_numero(up)


def extrair_comp_mm(texto: str):
    up = texto.upper().replace(",", ".")

    m = RE_LEN_CEQ.search(up)
    if m:
        v = _to_float(m.group(1))
        if v is None:
            return None
        # Se vier "295" quase sempre é cm -> 2950 mm
        if v <= 2000:
            return int(round(v * 10))
        return int(round(v))

    m = RE_LEN_CSL.search(up)
    if m:
        v = _to_float(m.group(1))
        if v is None:
            return None
        # "C/22" normalmente é 22 cm -> 220 mm
        if v <= 200:
            return int(round(v * 10))
        # se vier algo maior, converte cm -> mm
        if v <= 2000:
            return int(round(v * 10))
        return int(round(v))

    m = RE_LEN_PAR.search(up)
    if m:
        try:
            v = int(m.group(1))
        except Exception:
            return None
        # (320) normalmente em cm -> 3200 mm
        if 50 <= v <= 2000:
            return v * 10
        return v

    return None


def parse_chamada(ch):
    """
    Retorna (item, err)
    item padronizado:
      viga, pos, bitola_mm, comp_m, qtd, peso_kg
    """
    s = ch["texto"]

    pos = extrair_pos(s)
    if not pos:
        return None, "sem_pos"

    qtd = extrair_qtd(s)
    if not qtd or qtd < 1:
        return None, "sem_qtd"

    bit = extrair_bitola_mm(s)
    if bit is None:
        return None, "sem_bitola"

    comp_mm = extrair_comp_mm(s)
    if comp_mm is None:
        return None, "sem_comp"

    # sanidade: 0.20 m até 30 m
    if not (200 <= comp_mm <= 30000):
        return None, f"comp_fora({comp_mm})"

    comp_m = comp_mm / 1000.0

    kg_m = ACO_KG_M.get(float(bit))
    if kg_m is None:
        return None, "bitola_nao_cadastrada"

    peso_kg = float(qtd) * comp_m * kg_m

    item = {
        "viga": None,
        "pos": pos,
        "bitola_mm": float(bit),
        "comp_m": round(comp_m, 2),
        "qtd": int(qtd),
        "peso_kg": float(peso_kg),
        "_raw": s,
        "_x": ch["x"],
        "_y": ch["y"],
    }
    return item, None


def associar_viga(item, vigas, raio=5000.0):
    px, py = item["_x"], item["_y"]
    melhor = None
    melhor_d = None

    for nome, v in vigas.items():
        d = math.hypot(px - v["x"], py - v["y"])
        if melhor_d is None or d < melhor_d:
            melhor_d = d
            melhor = nome

    if melhor is None:
        return None

    if melhor_d is not None and melhor_d <= raio:
        return melhor
    return None


def agrupar_itens(itens):
    agg = defaultdict(lambda: {"qtd": 0, "peso_kg": 0.0})
    for it in itens:
        k = (it["viga"], it["pos"], it["bitola_mm"], it["comp_m"])
        agg[k]["qtd"] += it["qtd"]
        agg[k]["peso_kg"] += it["peso_kg"]

    saida = []
    for (viga, pos, bit, comp_m), v in agg.items():
        saida.append({
            "viga": viga,
            "pos": pos,
            "bitola_mm": float(bit),
            "qtd": int(v["qtd"]),
            "comp_m": float(comp_m),
            "peso_kg": float(v["peso_kg"]),
        })

    def _posnum(p):
        try:
            return int(p[1:])
        except Exception:
            return 9999

    saida.sort(key=lambda r: (r["viga"] or "", _posnum(r["pos"]), r["bitola_mm"], r["comp_m"]))
    return saida


def salvar_csv(path_csv, linhas):
    os.makedirs(os.path.dirname(path_csv), exist_ok=True)
    campos = ["viga", "pos", "bitola_mm", "qtd", "comp_m", "peso_kg"]
    with open(path_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, delimiter=";")
        w.writeheader()
        for r in linhas:
            w.writerow({k: r.get(k) for k in campos})


def main(caminho_dxf: str):
    textos = ler_textos_dxf(caminho_dxf)
    print(f"[V4.1.1] Textos lidos: {len(textos)}")

    vigas = detectar_vigas(textos)
    print(f"[V4.1.1] Vigas detectadas: {len(vigas)}")
    for k in sorted(vigas.keys()):
        print(f" - {k}")

    chamadas = detectar_chamadas(textos)
    print(f"[V4.1.1] Chamadas candidatas: {len(chamadas)}")
    if len(chamadas) == 0:
        # Mostra exemplos de textos que têm "N" pra enxergar o padrão real do TQS
        ns = [t for t in textos if "N" in (t.get("texto","").upper())]
        print(f"[V4.1.1] DEBUG: textos com 'N': {len(ns)} (mostrando até 30)")
        for t in ns[:30]:
            print("  >", t["texto"])

    raio = 5000.0
    print(f"[V4.1.1] Raio assoc. estimado: {raio}")

    itens_ok = []
    parse_ok = 0
    parse_fail = 0

    fail_reasons = defaultdict(int)
    fail_samples = []

    for ch in chamadas:
        item, err = parse_chamada(ch)
        if item is None:
            parse_fail += 1
            fail_reasons[err] += 1
            if len(fail_samples) < 20:
                fail_samples.append((err, ch["texto"]))
            continue

        viga = associar_viga(item, vigas, raio=raio)
        if not viga:
            parse_fail += 1
            fail_reasons["sem_viga_no_raio"] += 1
            if len(fail_samples) < 20:
                fail_samples.append(("sem_viga_no_raio", ch["texto"]))
            continue

        item["viga"] = viga
        itens_ok.append(item)
        parse_ok += 1

    if fail_samples:
        print("\n[V4.1.1] DEBUG FAIL (amostras):")
        for err, txt in fail_samples:
            print(f"  - {err}: {txt}")

    if fail_reasons:
        print("\n[V4.1.1] FAIL RESUMO:")
        for k, v in sorted(fail_reasons.items(), key=lambda x: -x[1]):
            print(f"  {k}: {v}")

    saida = agrupar_itens(itens_ok)

    barras = sum(x["qtd"] for x in saida) if saida else 0
    peso = sum(x["peso_kg"] for x in saida) if saida else 0.0

    print("\n================ RESULTADO V4.1.1 ================")
    print(f"Itens: {len(saida)} | Barras: {barras} | Peso: {peso:.2f} kg")
    print(f"parse_ok: {parse_ok} | parse_fail: {parse_fail} | raio: {raio}\n")

    for r in saida[:200]:
        print(f"{r['viga']:>3} | {r['pos']:<3} | Ø {r['bitola_mm']:>4} | qtd {r['qtd']:>4} | comp {r['comp_m']:>5} m | {r['peso_kg']:.2f} kg")

    base = os.path.splitext(os.path.basename(caminho_dxf))[0]
    csv_out = os.path.join(os.path.dirname(caminho_dxf), f"{base}_V4_1.csv")
    salvar_csv(csv_out, saida)
    print(f"\n[V4.1.1] CSV gerado: {csv_out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python motor_v4_1.py \"C:\\caminho\\arquivo.dxf\"")
        sys.exit(1)
    main(sys.argv[1])
