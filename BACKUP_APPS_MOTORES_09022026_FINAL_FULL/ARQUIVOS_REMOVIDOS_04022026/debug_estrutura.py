#!/usr/bin/env python3
"""
Debug da estrutura de dados retornada
"""

import sys
sys.path.insert(0, r"c:\EngenhariaPlanPro")

from core.pilares_motor_dual import processar_pilares

arquivos = [r"c:\EngenhariaPlanPro\pilares_l1-020.DXF"]

resultado = processar_pilares(arquivos)

print(f"Tipo resultado: {type(resultado)}")
print(f"Comprimento: {len(resultado)}")

if resultado:
    print(f"\nPrimeiro elemento:")
    print(f"  Tipo: {type(resultado[0])}")
    print(f"  Tamanho: {len(resultado[0]) if isinstance(resultado[0], (tuple, list)) else 'N/A'}")
    print(f"  Conteúdo: {resultado[0]}")
    
    print(f"\nÚltimos 3 elementos:")
    for i, r in enumerate(resultado[-3:]):
        print(f"  [{i}] {r}")
