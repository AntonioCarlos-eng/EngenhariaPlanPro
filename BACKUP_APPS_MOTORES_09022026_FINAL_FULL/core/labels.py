"""
labels.py
---------
Módulo reservado para futuras rotinas de geração de etiquetas / romaneio,
QR Code, etc. No momento ele só contém funções utilitárias simples, mas já
pode ser importado sem quebrar nada.
"""

from typing import Dict


def formatar_label_linha(reg: Dict) -> str:
    """
    Gera um texto padrão de etiqueta a partir de um registro de barra.
    """
    elem = reg.get("elem", "")
    pos = reg.get("pos", "")
    bit = reg.get("bitola", "")
    qtde = reg.get("qtde", "")
    comp = reg.get("comp", "")
    peso = reg.get("peso", "")

    return (f"ELEM: {elem}  POS: {pos}  Ø{bit}  "
            f"QTD: {qtde}  COMP: {comp} m  PESO: {peso} kg")
