# core/autotabela.py — V8.3 Oficial (PILARES)
# -----------------------------------------------------------
# Esta versão é a estável e usada na V8.3 sem suporte a vigas.
# Gera tabela simples e romaneio de produção.
# -----------------------------------------------------------

from __future__ import annotations
from typing import List, Tuple


def rodar_autotabela(dados):
    """
    Recebe a lista de tuplas:
    (elem, pos, bit, qt, comp, peso)

    Retorna texto formatado para colar em planilha, Excel ou TXT.
    """
    linhas = []
    linhas.append("ELEMENTO;POS;BITOLA;QTD;COMPRIMENTO(m);PESO(kg)")

    for elem, pos, bit, qt, comp, peso in dados:
        linhas.append(f"{elem};{pos};{bit};{qt};{comp};{peso}")

    return "\n".join(linhas)


def gerar_romaneio_producao(
    obra: str,
    etapa: str,
    plano: str,
    arquivos: List[str],
    dados: List[Tuple[str, str, float, int, float, float]],
    total_kg: float,
    total_barras: int
) -> str:
    """
    Gera ROMANEIO DE PRODUÇÃO completo em texto puro.
    Usado na V8.3 original.
    """

    linhas = []
    linhas.append(f"ROMANEIO — PRODUÇÃO")
    linhas.append("=" * 60)
    linhas.append("")
    linhas.append(f"OBRA : {obra}")
    linhas.append(f"ETAPA: {etapa}")
    linhas.append(f"PLANO: {plano}")
    linhas.append("")
    linhas.append("ARQUIVOS PROCESSADOS:")

    for a in arquivos:
        linhas.append(f" - {a}")

    linhas.append("")
    linhas.append("=" * 60)
    linhas.append("")

    bloco_atual = None

    for elem, pos, bit, qt, comp, peso in dados:
        if elem != bloco_atual:
            bloco_atual = elem
            linhas.append("")
            linhas.append(elem)
            linhas.append("-" * 60)

        linhas.append(
            f"{pos:<4} | ø{bit:<4} | Qt:{qt:<4} | C:{comp:<5} | Peso:{peso:>7.3f}"
        )

    linhas.append("")
    linhas.append("=" * 60)
    linhas.append(f"TOTAL PESO  : {total_kg:.3f} kg")
    linhas.append(f"TOTAL BARRAS: {total_barras}")
    linhas.append("=" * 60)

    return "\n".join(linhas)
