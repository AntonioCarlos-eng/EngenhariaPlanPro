# -*- coding: utf-8 -*-
"""
EngenhariaPlanPro - Motor V4 FINAL (ROBUSTO)
- Converte automaticamente DXF/DWG usando ODAFileConverter (opcional/automático)
- Lê TEXT/MTEXT/ATTRIB
- Identifica vigas (V10, V8, V9, VM1, VM2, etc.)
- Extrai chamadas no padrão: "2 N1 Ø10 C=295" (também aceita %%c e variações)
- Associa chamada -> viga por proximidade (XY)
- Gera CSV ; com: viga;pos;bitola_mm;qtd;comp_m;peso_kg

Uso:
  python core\\v4\\motor_v4_final.py "C:\\...\\arquivo.dxf"
  python core\\v4\\motor_v4_final.py "C:\\...\\pasta_com_dxf" --debug
  python core\\v4\\motor_v4_final.py "C:\\...\\arquivo.dwg" --oda "C:\\EngenhariaPlanPro\\ODA\\ODAFileConverter.exe"

Observação:
- Se conseguir ler direto com ezdxf, NÃO converte.
- Se falhar (ou se for DWG), converte antes e lê o convertido.
"""

from __future__ import annotations

import os
import re
import csv
import sys
import math
import time
import uuid
import shutil
import hashlib
import argparse
import subprocess
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

import ezdxf


# -----------------------------
# Config / Regex
# -----------------------------

# Viga: V10, V8, V9, VM1, VM2, etc.
RE_VIGA = re.compile(r"^(V(M)?\s*\d+)\s*$", re.IGNORECASE)

# Normalização de diâmetro: "Ø", "∅", "%%c"
RE_DIAM_ANY = re.compile(r"(Ø|∅|%%c)", re.IGNORECASE)

# Padrões de chamada comuns:
#  - "2 N1 Ø10 C=295"
#  - "11 N3 %%c 5 C=141"
#  - tolera espaços e separadores e "C-295" / "C= 295"
RE_CALL_CORE = re.compile(
    r"""
    (?P<qtd>\d+)\s*                # quantidade
    (?P<pos>N\s*\d+)\s*            # posição Nxx (permite 'N 3')
    (?:Ø|∅|%%c)\s*                 # símbolo diâmetro (ODA muitas vezes vira %%c)
    (?P<bitola>\d+(?:[.,]\d+)?)\s* # bitola
    .*?                            # qualquer coisa no meio (curto)
    C\s*[:=\-]\s*                  # C= / C- / C:
    (?P<comp>\d+(?:[.,]\d+)?)      # comprimento numérico (geralmente em cm no desenho)
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Às vezes vem "C=295" sem símbolo Ø explícito (raro) -> tentativa extra
RE_CALL_FALLBACK = re.compile(
    r"(?P<qtd>\d+)\s*(?P<pos>N\s*\d+)\s*(?P<bitola>\d+(?:[.,]\d+)?)\s*C\s*[:=\-]\s*(?P<comp>\d+(?:[.,]\d+)?)",
    re.IGNORECASE,
)

# Coeficiente kg/m por bitola (aprox. aço CA-50)
KG_M = {
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


@dataclass
class TxtItem:
    text: str
    x: float
    y: float


@dataclass
class Callout:
    viga: str
    pos: str
    bitola_mm: float
    qtd: int
    comp_m: float
    peso_kg: float
    src_text: str
    x: float
    y: float


def _to_float(s: str) -> float:
    return float(s.replace(",", ".").strip())


def _clean_text(s: str) -> str:
    s = (s or "").strip()
    # normalize whitespace
    s = re.sub(r"\s+", " ", s)
    # padroniza o símbolo do diâmetro: mantém "%%c" pois pode existir no DXF
    return s


def _dist(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


# -----------------------------
# ODA Converter
# -----------------------------

def _hash_path(p: str) -> str:
    h = hashlib.sha1(p.encode("utf-8", errors="ignore")).hexdigest()
    return h[:18]


def convert_with_oda(
    input_path: str,
    oda_exe: str,
    out_root: str,
    target_ver: str = "ACAD2013",
    out_fmt: str = "DXF",
    audit: str = "0",
    recurse: str = "1",
    debug: bool = False,
) -> str:
    """
    Converte um arquivo (ou pasta) usando ODAFileConverter.
    Retorna o caminho do arquivo convertido (se input for arquivo),
    ou a pasta convertida (se input for pasta).
    """
    if not os.path.exists(oda_exe):
        raise FileNotFoundError(f"ODAFileConverter.exe não encontrado em: {oda_exe}")

    os.makedirs(out_root, exist_ok=True)

    token = _hash_path(os.path.abspath(input_path) + "|" + str(time.time()) + "|" + str(uuid.uuid4()))
    job_dir = os.path.join(out_root, token)
    tmp_in = os.path.join(job_dir, "_tmp_in")
    tmp_out = job_dir

    os.makedirs(tmp_in, exist_ok=True)
    os.makedirs(tmp_out, exist_ok=True)

    if os.path.isdir(input_path):
        # Converter a pasta toda: aponta o input direto para a pasta
        in_arg = os.path.abspath(input_path)
    else:
        # Para arquivo: copia para tmp_in (evita problemas com espaços/encoding/lock)
        src = os.path.abspath(input_path)
        dst = os.path.join(tmp_in, os.path.basename(src))
        shutil.copy2(src, dst)
        in_arg = tmp_in

    cmd = [
        oda_exe,
        in_arg,
        tmp_out,
        target_ver,
        out_fmt,
        audit,
        recurse,
    ]

    if debug:
        print(f"[ODA] CMD: {' '.join(cmd)}")

    p = subprocess.run(cmd, capture_output=True, text=True)
    if debug:
        if p.stdout.strip():
            print("[ODA] STDOUT:", p.stdout.strip())
        if p.stderr.strip():
            print("[ODA] STDERR:", p.stderr.strip())

    if p.returncode != 0:
        raise RuntimeError(f"ODAFileConverter falhou (code={p.returncode}). stderr={p.stderr.strip()}")

    # Se era arquivo, tenta achar o convertido pelo mesmo nome (com .dxf)
    if os.path.isdir(input_path):
        return tmp_out

    base = os.path.splitext(os.path.basename(input_path))[0]
    # procura case-insensitive
    candidates = []
    for root, _, files in os.walk(tmp_out):
        for fn in files:
            if fn.lower().endswith(".dxf") and os.path.splitext(fn)[0].lower() == base.lower():
                candidates.append(os.path.join(root, fn))
    if not candidates:
        # fallback: pega qualquer .dxf gerado
        for root, _, files in os.walk(tmp_out):
            for fn in files:
                if fn.lower().endswith(".dxf"):
                    candidates.append(os.path.join(root, fn))
        if not candidates:
            raise RuntimeError("ODA converteu mas nenhum .DXF foi encontrado na saída.")
    return candidates[0]


# -----------------------------
# Leitura DXF (TEXT/MTEXT/ATTRIB)
# -----------------------------

def read_text_items(dxf_path: str) -> List[TxtItem]:
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    out: List[TxtItem] = []

    for e in msp:
        t = e.dxftype()

        if t == "TEXT":
            txt = _clean_text(getattr(e.dxf, "text", ""))
            ins = e.dxf.insert
            out.append(TxtItem(txt, float(ins.x), float(ins.y)))

        elif t == "MTEXT":
            try:
                txt = _clean_text(e.plain_text())
            except Exception:
                txt = _clean_text(getattr(e.dxf, "text", ""))
            ins = e.dxf.insert
            out.append(TxtItem(txt, float(ins.x), float(ins.y)))

        elif t == "ATTRIB":
            txt = _clean_text(getattr(e.dxf, "text", ""))
            ins = e.dxf.insert
            out.append(TxtItem(txt, float(ins.x), float(ins.y)))

        elif t == "INSERT":
            # Captura ATTRIBs dentro de blocos (muito comum em pranchas)
            try:
                for a in e.attribs:
                    txt = _clean_text(getattr(a.dxf, "text", ""))
                    ins = a.dxf.insert
                    out.append(TxtItem(txt, float(ins.x), float(ins.y)))
            except Exception:
                pass

    return out


def detect_vigas(items: List[TxtItem]) -> Dict[str, Tuple[float, float]]:
    vigas: Dict[str, Tuple[float, float]] = {}
    for it in items:
        m = RE_VIGA.match(it.text.upper().replace(" ", ""))
        if m:
            v = m.group(1).upper().replace(" ", "")
            # se repetir, mantém o primeiro (mais estável)
            if v not in vigas:
                vigas[v] = (it.x, it.y)
    return vigas


def estimate_assoc_radius(items: List[TxtItem]) -> float:
    # raio baseado no "tamanho" do desenho
    xs = [it.x for it in items]
    ys = [it.y for it in items]
    if not xs or not ys:
        return 1500.0
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    diag = math.hypot(w, h)
    # 6% da diagonal costuma funcionar bem para associar textos à viga
    r = max(800.0, min(5000.0, diag * 0.06))
    return r


def parse_callouts(items: List[TxtItem], vigas: Dict[str, Tuple[float, float]], debug: bool = False) -> List[Callout]:
    if not items or not vigas:
        return []

    raio = estimate_assoc_radius(items)
    if debug:
        print(f"[V4 FINAL] raio_assoc_estimado: {raio:.1f}")

    # separar possíveis “chamadas”
    candidates: List[TxtItem] = []
    for it in items:
        tx = it.text
        # precisa ter Nxx e C=algo
        if re.search(r"\bN\s*\d+\b", tx, re.IGNORECASE) and re.search(r"\bC\s*[:=\-]\s*\d", tx, re.IGNORECASE):
            candidates.append(it)

    if debug:
        print(f"[V4 FINAL] candidatos_chamada: {len(candidates)} (de {len(items)})")

    callouts: List[Callout] = []
    parse_fail_samples = 0

    for it in candidates:
        tx = it.text

        m = RE_CALL_CORE.search(tx)
        if not m:
            # tenta fallback (quando não aparece Ø/%%c explícito)
            m = RE_CALL_FALLBACK.search(tx)

        if not m:
            if debug and parse_fail_samples < 8:
                print(f"[PARSE FAIL] {tx}")
                parse_fail_samples += 1
            continue

        qtd = int(m.group("qtd"))
        pos = m.group("pos").upper().replace(" ", "")
        bitola = _to_float(m.group("bitola"))

        comp_raw = _to_float(m.group("comp"))
        # Nos seus exemplos C=295 / C=141 / C=300 (cm). Converte para metros:
        # Se vier um número muito pequeno (ex: 0.94) assume que já está em metros.
        if comp_raw > 20.0:
            comp_m = comp_raw / 100.0
        else:
            comp_m = comp_raw

        # peso
        # pega kg/m pela bitola mais próxima se não estiver exata
        bkeys = sorted(KG_M.keys())
        nearest = min(bkeys, key=lambda k: abs(k - bitola))
        kgm = KG_M.get(bitola, KG_M[nearest])
        peso_kg = qtd * comp_m * kgm

        # associa à viga mais próxima
        best_v = None
        best_d = 1e18
        for v, (vx, vy) in vigas.items():
            d = _dist((it.x, it.y), (vx, vy))
            if d < best_d:
                best_d = d
                best_v = v

        if best_v is None or best_d > raio:
            # sem associação confiável -> ignora (evita “misturar o projeto todo”)
            continue

        callouts.append(Callout(
            viga=best_v,
            pos=pos,
            bitola_mm=float(bitola),
            qtd=qtd,
            comp_m=float(comp_m),
            peso_kg=float(peso_kg),
            src_text=tx,
            x=it.x,
            y=it.y,
        ))

    return callouts


def aggregate(callouts: List[Callout]) -> List[Callout]:
    # agrupa por viga+pos+bitola+comp_m (arredonda comp pra 2 casas)
    agg: Dict[Tuple[str, str, float, float], Callout] = {}
    for c in callouts:
        key = (c.viga, c.pos, round(c.bitola_mm, 1), round(c.comp_m, 2))
        if key not in agg:
            agg[key] = Callout(
                viga=c.viga,
                pos=c.pos,
                bitola_mm=round(c.bitola_mm, 1),
                qtd=c.qtd,
                comp_m=round(c.comp_m, 2),
                peso_kg=c.peso_kg,
                src_text=c.src_text,
                x=c.x,
                y=c.y,
            )
        else:
            agg[key].qtd += c.qtd
            agg[key].peso_kg += c.peso_kg
    # ordena para ficar legível
    out = list(agg.values())
    out.sort(key=lambda z: (z.viga, int(re.sub(r"\D", "", z.pos) or "0"), z.bitola_mm, z.comp_m))
    return out


def write_csv(out_csv: str, rows: List[Callout]) -> None:
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["viga", "pos", "bitola_mm", "qtd", "comp_m", "peso_kg"])
        for r in rows:
            w.writerow([
                r.viga,
                r.pos,
                f"{r.bitola_mm:.1f}",
                int(r.qtd),
                f"{r.comp_m:.2f}",
                f"{r.peso_kg:.3f}",
            ])


def list_input_files(path: str) -> List[str]:
    path = os.path.abspath(path)
    if os.path.isdir(path):
        out = []
        for fn in os.listdir(path):
            if fn.lower().endswith((".dxf", ".dwg")):
                out.append(os.path.join(path, fn))
        out.sort()
        return out
    return [path]


def safe_read_or_convert(path: str, oda_exe: Optional[str], out_root: str, debug: bool) -> str:
    ext = os.path.splitext(path)[1].lower()

    # DWG: sempre precisa converter
    if ext == ".dwg":
        if not oda_exe:
            raise RuntimeError("Arquivo .DWG requer ODA. Passe --oda \"C:\\...\\ODAFileConverter.exe\"")
        return convert_with_oda(path, oda_exe=oda_exe, out_root=out_root, debug=debug)

    # DXF: tenta ler direto; se falhar, converte
    try:
        _ = ezdxf.readfile(path)
        return path
    except Exception:
        if not oda_exe:
            raise
        return convert_with_oda(path, oda_exe=oda_exe, out_root=out_root, debug=debug)


def process_one(input_file: str, oda_exe: Optional[str], debug: bool = False) -> Tuple[List[Callout], str]:
    in_abs = os.path.abspath(input_file)
    out_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "_convertidos")
    os.makedirs(out_root, exist_ok=True)

    used_path = safe_read_or_convert(in_abs, oda_exe=oda_exe, out_root=out_root, debug=debug)
    if debug and used_path != in_abs:
        print(f"[DEBUG] convertido: {used_path}")

    items = read_text_items(used_path)
    vigas = detect_vigas(items)

    print(f"[V4 FINAL] Textos lidos: {len(items)}")
    print(f"[V4 FINAL] Vigas detectadas: {len(vigas)}")
    for v in sorted(vigas.keys()):
        print(f" - {v}")

    callouts = parse_callouts(items, vigas, debug=debug)
    rows = aggregate(callouts)

    return rows, used_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="Arquivo DXF/DWG ou pasta contendo DXF/DWG")
    ap.add_argument("--debug", action="store_true", help="Mostra debug controlado")
    ap.add_argument("--oda", default=r"C:\EngenhariaPlanPro\ODA\ODAFileConverter.exe", help="Caminho do ODAFileConverter.exe")
    args = ap.parse_args()

    oda_exe = args.oda if args.oda and os.path.exists(args.oda) else None
    debug = bool(args.debug)

    inputs = list_input_files(args.path)

    all_rows: List[Callout] = []
    total_peso = 0.0
    total_barras = 0

    # Saída: se input for arquivo -> mesmo nome _V4_FINAL.csv
    # Se for pasta -> gera _V4_FINAL_ALL.csv na pasta
    if os.path.isdir(os.path.abspath(args.path)):
        out_csv = os.path.join(os.path.abspath(args.path), "_V4_FINAL_ALL.csv")
    else:
        base = os.path.splitext(os.path.basename(args.path))[0]
        out_csv = os.path.join(os.path.dirname(os.path.abspath(args.path)), f"{base}_V4_FINAL.csv")

    for f in inputs:
        try:
            rows, used_path = process_one(f, oda_exe=oda_exe, debug=debug)
            all_rows.extend(rows)
        except Exception as e:
            print(f"[ERRO] Falhou em: {f}")
            print(f"       {type(e).__name__}: {e}")

    # Re-agrega tudo para não duplicar (quando é pasta)
    all_rows = aggregate(all_rows)

    for r in all_rows:
        total_peso += r.peso_kg
        total_barras += r.qtd

    print("\n========== RESULTADO V4 FINAL ==========")
    print(f"Itens: {len(all_rows)} | Barras: {total_barras} | Peso total: {total_peso:.2f} kg\n")

    for r in all_rows[:1200]:
        # print “tipo tabela”
        # exemplo: V10 | N1 | Ø20.0 | qtd 2 | comp 2.95 m | 3.141 kg
        print(f"{r.viga:>3} | {r.pos:<4} | Ø{r.bitola_mm:>4.1f} | qtd {r.qtd:>4} | comp {r.comp_m:>5.2f} m | {r.peso_kg:>8.3f} kg")

    write_csv(out_csv, all_rows)
    print(f"\n[V4 FINAL] CSV gerado: {out_csv}")

    if debug:
        # debug final
        print(f"[DEBUG] total_rows={len(all_rows)} total_barras={total_barras} total_peso={total_peso:.3f}")


if __name__ == "__main__":
    main()
