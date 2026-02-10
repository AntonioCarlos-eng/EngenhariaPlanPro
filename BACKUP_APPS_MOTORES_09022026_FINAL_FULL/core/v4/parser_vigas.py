# core/v4/parser_vigas.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import re

from reader_dxf import DxfText
from utils_norm import only_number, weight_kg_per_m

@dataclass
class ItemViga:
    viga: str
    pos: str      # N1, N2...
    bitola: float # mm
    qtd: int
    comp_m: float
    peso_kg: float
    origem: str   # debug (trecho)

# Aceita N1, N12...
RE_N = re.compile(r"^N(\d+)$", re.IGNORECASE)

def _is_n(tok: str) -> bool:
    return bool(RE_N.match(tok.strip().upper()))

def _norm_tok(tok: str) -> str:
    tok = tok.strip()
    # remove caracteres soltos
    tok = tok.replace(",", ".")
    return tok

def extrair_itens_de_tokens(viga: str, tokens: List[str]) -> List[ItemViga]:
    """
    Procura padrões reais:
      QTD  Nxx  (DIA)  bitola  C=  comp
    - ignora C/ (ex: C/20)
    - aceita C=295, C= 295, L=...
    """
    itens: List[ItemViga] = []
    i = 0

    while i < len(tokens):
        # tenta achar sequência iniciando em um número (qtd)
        qtd = None
        if re.fullmatch(r"\d+", tokens[i]):
            qtd = int(tokens[i])

        if qtd is None:
            i += 1
            continue

        # próxima: Nxx
        if i + 1 >= len(tokens) or not _is_n(tokens[i+1]):
            i += 1
            continue
        pos = tokens[i+1].upper()

        # procurar bitola e comprimento nos próximos tokens (janela)
        window = tokens[i:i+12]  # janela curta para não “puxar” coisa de longe
        window_str = " ".join(window)

        # bitola: depois de DIA ou Ø ou simplesmente número (com cuidado)
        # preferir padrão "DIA 10" ou "DIA 12.5"
        bitola = None
        m = re.search(r"\bDIA\s*(\d+(?:\.\d+)?)\b", window_str, flags=re.IGNORECASE)
        if m:
            bitola = float(m.group(1))
        else:
            # fallback: pegar um número que pareça bitola (>=4 e <=32)
            nums = [float(x) for x in re.findall(r"\b(\d+(?:\.\d+)?)\b", window_str)]
            cand = [n for n in nums if 4.0 <= n <= 32.0]
            bitola = cand[0] if cand else None

        # comprimento: precisa ser C= (NÃO C/)
        comp_cm = None
        m2 = re.search(r"\bC\s*=\s*(\d+(?:\.\d+)?)\b", window_str, flags=re.IGNORECASE)
        if not m2:
            m2 = re.search(r"\bL\s*=\s*(\d+(?:\.\d+)?)\b", window_str, flags=re.IGNORECASE)
        if m2:
            comp_cm = float(m2.group(1))

        # se não achou, pode ser "C=295" colado sem espaço já cobre; ok
        # se não achou, pula
        if bitola is None or comp_cm is None:
            i += 1
            continue

        comp_m = comp_cm / 100.0
        peso = weight_kg_per_m(bitola) * comp_m * qtd

        itens.append(ItemViga(
            viga=viga,
            pos=pos,
            bitola=bitola,
            qtd=qtd,
            comp_m=round(comp_m, 2),
            peso_kg=round(peso, 2),
            origem=window_str
        ))

        i += 2  # anda após QTD+N
    return itens

def parse_viga_bucket(viga: str, textos: List[DxfText]) -> List[ItemViga]:
    """
    Junta todos os tokens da viga, na ordem visual,
    e aplica o extrator.
    """
    tokens: List[str] = []
    for t in textos:
        # quebra por espaço
        for tok in t.txt.split():
            tok = _norm_tok(tok)

            # ignora "C/20", "C/14", etc (isso é espaçamento, não comprimento)
            if re.match(r"^C/\d+", tok, flags=re.IGNORECASE):
                continue

            # ignora lixo muito curto
            if tok == "|":
                continue

            tokens.append(tok)

    return extrair_itens_de_tokens(viga, tokens)

def consolidar(itens: List[ItemViga]) -> List[ItemViga]:
    """
    Agrupa por (viga, pos, bitola, comp_m) somando qtd e peso.
    """
    key_map: Dict[Tuple[str,str,float,float], ItemViga] = {}
    for it in itens:
        k = (it.viga, it.pos, float(it.bitola), float(it.comp_m))
        if k not in key_map:
            key_map[k] = ItemViga(
                viga=it.viga, pos=it.pos, bitola=it.bitola,
                qtd=it.qtd, comp_m=it.comp_m, peso_kg=it.peso_kg,
                origem=it.origem
            )
        else:
            key_map[k].qtd += it.qtd
            key_map[k].peso_kg = round(key_map[k].peso_kg + it.peso_kg, 2)

    out = list(key_map.values())
    out.sort(key=lambda z: (z.viga, int(z.pos[1:]), z.bitola, z.comp_m))
    return out
