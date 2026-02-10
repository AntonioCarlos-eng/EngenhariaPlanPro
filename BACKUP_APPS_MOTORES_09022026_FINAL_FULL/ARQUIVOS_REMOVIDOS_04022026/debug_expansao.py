#!/usr/bin/env python3
"""
Debug: Testar expansão de P14=P32(X2)
"""

import sys
sys.path.insert(0, r"c:\EngenhariaPlanPro")

from core.pilares_motor_dual import _expandir_titulos_pilares

# Testar os padrões encontrados no DXF
padroes = [
    "P14=P32",
    "P14=P32(X2)",
    "P14=P32   (X2)",  # Com espaço
]

print("=" * 80)
print("DEBUG: Testar expansão de padrões")
print("=" * 80)

for padrao in padroes:
    resultado = _expandir_titulos_pilares(padrao)
    print(f"\nEntrada: '{padrao}'")
    print(f"Resultado: {resultado}")
    print(f"Expandiu: {'SIM' if len(resultado) > 1 else 'NÃO'}")
    if len(resultado) > 1:
        print(f"Quantidade de pilares: {len(resultado)}")

print("\n" + "=" * 80)
