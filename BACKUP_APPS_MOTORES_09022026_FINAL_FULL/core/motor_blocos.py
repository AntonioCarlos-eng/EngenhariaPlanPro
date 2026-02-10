# core/motor_blocos.py
import ezdxf
import re
from math import pi
from typing import List, Tuple, Dict


# -----------------------------
# Suporte
# -----------------------------
def _normalizar_elemento(txt: str) -> str:
    t = txt.upper()
    m = re.search(r"BLOCO\s+DE\s+(\d+)\s+ESTACA", t)
    if not m:
        return txt.strip()
    n = m.group(1)
    return f"BLOCO DE {n} ESTACAS"


def _peso(diam_mm: float, comp_m: float, qtd: int) -> float:
    diam_m = diam_mm / 1000.0
    area = pi * (diam_m ** 2) / 4
    kg_m = area * 7850.0
    return kg_m * comp_m * qtd


PADRAO_BARRA = re.compile(
    r"(?P<qtd>\d+)\s+N(?P<pos>\d+).*?Ø?\s*(?P<bitola>\d+[\.,]?\d*).*?C[=\:\s]+(?P<C>[\d\.,]+)",
    re.IGNORECASE
)


# -----------------------------
# Motor Principal
# -----------------------------
def processar_blocos(arquivos: List[str]) -> Tuple[List[Dict], float, int]:
    dados = []
    total_kg = 0
    total_barras = 0

    for caminho in arquivos:

        # -----------------------------
        # 1. Abrir arquivo
        # -----------------------------
        try:
            doc = ezdxf.readfile(caminho)
        except:
            continue

        msp = doc.modelspace()

        # -----------------------------
        # 2. Extrair TEXTO em ordem exata
        # -----------------------------
        textos = []
        for e in msp:
            if e.dxftype() == "TEXT":
                t = e.dxf.text.strip()
            elif e.dxftype() == "MTEXT":
                t = e.plain_text().strip()
            else:
                continue
            if t:
                textos.append(t)

        if not textos:
            continue

        # -----------------------------
        # 3. Identificar títulos de blocos
        # -----------------------------
        indices_blocos = []
        for idx, t in enumerate(textos):
            if "BLOCO DE" in t.upper() and "ESTACA" in t.upper():
                indices_blocos.append((idx, _normalizar_elemento(t)))

        if not indices_blocos:
            continue

        # Acrescenta fim artificial
        indices_blocos.append((len(textos), "FIM"))

        # -----------------------------
        # 4. Processar CADA bloco isolado
        # -----------------------------
        for i in range(len(indices_blocos) - 1):

            ini, nome_bloco = indices_blocos[i]
            fim, _ = indices_blocos[i + 1]

            # restringe somente ao trecho do bloco
            trecho = textos[ini:fim]

            for linha in trecho:

                up = linha.upper()

                if "VAR" in up:
                    continue

                m = PADRAO_BARRA.search(up)
                if not m:
                    continue

                try:
                    qtd = int(m.group("qtd"))
                    pos = f"N{int(m.group('pos'))}"
                    bitola = float(m.group("bitola").replace(",", "."))
                    C_cm = float(m.group("C").replace(",", "."))
                except:
                    continue

                comp_m = C_cm / 100.0
                peso = _peso(bitola, comp_m, qtd)

                dados.append({
                    "elemento": nome_bloco,
                    "pos": pos,
                    "bitola": bitola,
                    "qtd": qtd,
                    "comp": round(comp_m, 3),
                    "peso": round(peso, 4)
                })

                total_barras += qtd
                total_kg += peso

    return dados, total_kg, total_barras
