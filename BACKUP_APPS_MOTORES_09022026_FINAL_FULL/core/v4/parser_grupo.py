import re

RE_N = re.compile(r"\bN\s*([0-9]{1,3})\b", re.IGNORECASE)

# quantidade pode vir como "2", ou "2x", ou "Q=2", ou "QTD 2"
RE_QTD_ANY = re.compile(r"\b(?:QTD|Q|QT)\s*=?\s*([0-9]{1,5})\b", re.IGNORECASE)
RE_INT = re.compile(r"^\s*([0-9]{1,5})\s*$")

# bitola aparece como:
# "Ø10", "Ø 10", "PHI 10", "φ10", "Φ10", "D10", "%C 10" (seu log antigo),
# "Ø 6.3", "6.3" (quando vem só o número perto do símbolo)
RE_BITOLA_1 = re.compile(r"(?:Ø|∅|Φ|φ|PHI|DIA|DIAM|D)\s*([0-9]{1,2}(?:\.[0-9])?)", re.IGNORECASE)
RE_BITOLA_PC = re.compile(r"%\s*C\s*([0-9]{1,2}(?:\.[0-9])?)", re.IGNORECASE)

# comprimento aparece como:
# "C=295", "C = 295", "C295", "L=295", "L 295"
RE_COMP = re.compile(r"\b(?:C|L)\s*=?\s*([0-9]{2,5}(?:\.[0-9])?)\b", re.IGNORECASE)

def _norm(s: str) -> str:
    s = (s or "").strip()
    s = s.replace(",", ".")
    s = s.replace("∅", "Ø").replace("Φ", "Ø").replace("φ", "Ø")
    return s

def _flatten_tokens(cluster):
    toks = []
    for t in cluster:
        s = _norm(t.get("text", "") or t.get("texto", "") or "")
        if not s:
            continue
        # quebra em pedacinhos sem destruir Ø e =
        parts = re.split(r"[\|\t;]", s)
        for p in parts:
            p = p.strip()
            if p:
                toks.append(p)
    return toks

def _find_qtd(tokens, joined):
    # 1) QTD/Q= etc
    m = RE_QTD_ANY.search(joined)
    if m:
        return int(m.group(1)), ""
    # 2) um inteiro isolado no cluster (pega o menor “realista” perto: 1..9999)
    ints = []
    for tk in tokens:
        mi = RE_INT.match(tk)
        if mi:
            v = int(mi.group(1))
            if 1 <= v <= 9999:
                ints.append(v)
    if ints:
        return ints[0], ""
    # 3) fallback: 1
    return 1, "QTY_ASSUMED_1"

def _find_bitola(tokens, joined):
    m = RE_BITOLA_1.search(joined)
    if m:
        return float(m.group(1))
    m = RE_BITOLA_PC.search(joined)
    if m:
        return float(m.group(1))
    # fallback: procura número “padrão” 4.2/5/6.3/8/10/12.5/16/20 próximo de Ø perdido
    # se não achar, retorna None
    return None

def _find_comp(tokens, joined):
    m = RE_COMP.search(joined)
    if m:
        return float(m.group(1))
    return None

def parse_grupo(cluster):
    tokens = _flatten_tokens(cluster)
    if not tokens:
        return None
    joined = " ".join(tokens).upper()

    # N
    mN = RE_N.search(joined)
    if not mN:
        return None
    pos = f"N{int(mN.group(1))}"

    bitola = _find_bitola(tokens, joined)
    if bitola is None:
        return None

    comp_cm = _find_comp(tokens, joined)
    if comp_cm is None:
        return None

    qtd, note = _find_qtd(tokens, joined)

    comp_m = float(comp_cm) / 100.0

    return {
        "pos": pos,
        "bitola": float(bitola),
        "qtd": int(qtd),
        "comp_cm": float(comp_cm),
        "comp_m": float(comp_m),      # <- CHAVE NOVA (m)
        "comp": float(comp_m),        # <- ALIAS (m) p/ motores antigos
        "note": note,
        "tokens": tokens,
    }

