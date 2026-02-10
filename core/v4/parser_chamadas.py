# core/v4/parser_chamadas.py
import re
from typing import Optional, Dict, Any, Tuple, List

# Bitolas plausíveis (mm). Se quiser adicionar, adicione aqui.
BITOLAS_OK = {4.2, 5.0, 6.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0}

# Ex: "2 N1 Ø10 C=295" | "11 N3 %%%c 5 C=141" | "qtd 2 N2 Ø10 L=300"
RE_N = re.compile(r"\bN\s*(\d{1,3})\b", re.IGNORECASE)
RE_LEN = re.compile(r"\b([CL])\s*=\s*(\d{2,5})\b", re.IGNORECASE)   # C=295, L=300
RE_DIA = re.compile(r"(?:Ø|DIA|DIAM|⌀)\s*([0-9]{1,2}(?:[.,][0-9])?)", re.IGNORECASE)
RE_QTD_ANTES_N = re.compile(r"^\s*(\d{1,4})\s+N\s*\d{1,3}\b", re.IGNORECASE)
RE_QTD = re.compile(r"\bQTD\s*[:=]?\s*(\d{1,4})\b", re.IGNORECASE)

# Para evitar confundir dimensão "19X89" etc
RE_DIM = re.compile(r"\b\d{1,3}\s*[Xx]\s*\d{1,3}\b")

def kg_por_metro(d_mm: float) -> float:
    # kg/m = 0.006165 * d^2
    return 0.006165 * (d_mm ** 2)

def _parse_float(s: str) -> Optional[float]:
    try:
        return float(s.replace(",", "."))
    except Exception:
        return None

def parse_chamada(texto: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Tenta extrair uma chamada de aço de um único texto.
    Retorna: (item_dict, motivo_falha)

    item_dict:
      { "pos":"N1", "qtd":2, "bitola_mm":10.0, "comp_cm":295, "comp_m":2.95, "len_tag":"C" }
    """
    if not texto:
        return None, "texto_vazio"

    s = texto.strip()

    # filtro: se for claramente dimensão, ignora
    if RE_DIM.search(s):
        return None, "dimensao_ignorada"

    mN = RE_N.search(s)
    if not mN:
        return None, "sem_N"

    pos = f"N{int(mN.group(1))}"

    mL = RE_LEN.search(s)
    if not mL:
        return None, "sem_C_ou_L"

    len_tag = mL.group(1).upper()
    comp_cm = int(mL.group(2))

    # Regras de sanidade do comprimento (em cm)
    # 50 cm mínimo e 3000 cm máximo (ajuste se precisar)
    if comp_cm < 50 or comp_cm > 3000:
        return None, f"comprimento_fora:{comp_cm}"

    # Bitola
    mD = RE_DIA.search(s)
    if not mD:
        # tem casos "%%c 5" sem Ø explícito; tenta pegar número após o símbolo %%c já convertido em Ø no norm
        # ou um padrão "N1 10 C=295"
        # pegamos o primeiro número plausível perto do N
        nums = re.findall(r"(?<![A-Z])([0-9]{1,2}(?:[.,][0-9])?)", s)
        cand = None
        for n in nums:
            v = _parse_float(n)
            if v is None:
                continue
            if v in BITOLAS_OK:
                cand = v
                break
        if cand is None:
            return None, "sem_bitola"
        bitola = cand
    else:
        bitola = _parse_float(mD.group(1))
        if bitola is None:
            return None, "bitola_invalida"
        # sanidade + whitelist
        if bitola not in BITOLAS_OK:
            return None, f"bitola_fora:{bitola}"

    # Quantidade: preferir "qtd", senão número antes do N
    qtd = None
    mQ = RE_QTD.search(s)
    if mQ:
        qtd = int(mQ.group(1))
    else:
        mQA = RE_QTD_ANTES_N.search(s)
        if mQA:
            qtd = int(mQA.group(1))

    if qtd is None:
        return None, "sem_qtd"

    if qtd <= 0 or qtd > 5000:
        return None, f"qtd_fora:{qtd}"

    comp_m = comp_cm / 100.0

    return {
        "pos": pos,
        "qtd": qtd,
        "bitola_mm": float(bitola),
        "comp_cm": comp_cm,
        "comp_m": comp_m,
        "len_tag": len_tag,
        "src": s,
    }, None


def escolher_raio_assoc(vigas: List[Dict[str, Any]], textos: List[Dict[str, Any]]) -> float:
    """
    Estima um raio máximo de associação (unidades do DXF) usando distância típica
    entre textos e a viga mais próxima.
    """
    if not vigas or not textos:
        return 0.0

    # pega algumas distâncias amostrais
    import math
    def dist(a, b):
        return math.hypot(a["x"]-b["x"], a["y"]-b["y"])

    # amostra no máximo 300 textos
    sample = textos[:300] if len(textos) > 300 else textos
    dists = []
    for t in sample:
        # só textos que parecem chamada (tem N e C/L)
        if "N" not in t["text"].upper():
            continue
        if ("C=" not in t["text"].upper()) and ("L=" not in t["text"].upper()):
            continue
        dmin = None
        for v in vigas:
            d = dist(t, v)
            if dmin is None or d < dmin:
                dmin = d
        if dmin is not None:
            dists.append(dmin)

    if not dists:
        # fallback padrão
        return 5000.0

    dists.sort()
    # usa percentil 85 e multiplica um pouco (mais tolerante)
    idx = int(0.85 * (len(dists)-1))
    base = dists[idx]
    return max(2000.0, base * 1.35)
