# core/romaneio.py
from __future__ import annotations
from datetime import datetime


def gerar_romaneio_texto(
    obra: str,
    etapa: str,
    plano: str,
    arquivos: list[str],
    barras: list[dict],
) -> str:
    """
    Gera o texto do romaneio simples (V8.3 de pilares).
    """

    linhas = []
    linhas.append(f"ROMANEIO — CONFERÊNCIA")
    linhas.append("=" * 60)
    linhas.append("")
    linhas.append(f"OBRA : {obra}")
    linhas.append(f"ETAPA: {etapa}")
    linhas.append(f"PLANO: {plano}")
    linhas.append(f"DATA : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    linhas.append("")
    linhas.append("ARQUIVOS:")
    for a in arquivos:
        linhas.append(f" - {a}")
    linhas.append("=" * 60)
    linhas.append("")

    bloco = None
    for b in barras:
        elem = b.get("elem", "")
        pos = b.get("pos", "")
        bit = b.get("bit", "")
        qt = b.get("qt", "")
        comp = b.get("comp", "")
        peso = b.get("peso", "")

        if elem != bloco:
            bloco = elem
            linhas.append("")
            linhas.append(elem)
            linhas.append("-" * 60)

        linhas.append(
            f"{pos:<3} | {bit:>4} | Qt:{qt:<4} | C:{comp:<5} | P:{peso:>7}"
        )

    linhas.append("")
    peso_total = sum(b["peso"] for b in barras)
    total_barras = sum(b["qt"] for b in barras)

    linhas.append("=" * 60)
    linhas.append(f"TOTAL: {peso_total:.3f} kg | {total_barras} barra(s) processada(s).")
    linhas.append("")

    return "\n".join(linhas)
