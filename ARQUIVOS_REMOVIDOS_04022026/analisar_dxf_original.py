#!/usr/bin/env python3
"""Analisar arquivo DXF original do usuário para verificar nomenclatura de expansão"""

import sys
sys.path.insert(0, '.')

try:
    import ezdxf
except ImportError:
    print("ezdxf não disponível")
    sys.exit(1)

arquivo_usuario = r"C:\Users\orqui\OneDrive\Área de Trabalho\projetos\pilares\pilares l1-020.DXF"

print(f"Analisando: {arquivo_usuario}\n")

try:
    dwg = ezdxf.readfile(arquivo_usuario)
except Exception as e:
    print(f"Erro ao abrir: {e}")
    sys.exit(1)

# Extrair todos os textos
msp = dwg.modelspace()
textos = [(ent.dxf.text, ent.dxf.insert.x, ent.dxf.insert.y) for ent in msp.query('TEXT')]

print(f"Total de textos: {len(textos)}\n")

# Procurar por títulos de pilares (com padrão P + dígitos)
import re

pilares_encontrados = []
for txt, x, y in textos:
    # Procurar por padrões como P13, P14, P14-P32, P14=P32, P14=P32(X2), etc
    if re.search(r'P\d+', txt):
        pilares_encontrados.append((txt, x, y))
        print(f"Texto: '{txt:30}' em x={x:7.1f}, y={y:7.1f}")

print(f"\n=== TÍTULOS DE PILARES ===")
# Ordenar por Y (descendente) para ver ordem
pilares_por_y = sorted(pilares_encontrados, key=lambda t: -t[2])

for i, (txt, x, y) in enumerate(pilares_por_y):
    print(f"{i+1:2}. '{txt:30}' y={y:7.1f}")
    
    # Verificar se tem padrão de expansão
    if '=' in txt:
        print(f"    -> EXPANSAO COM IGUAL (=)")
    elif '-' in txt and re.search(r'P\d+-P\d+', txt):
        print(f"    -> EXPANSAO COM HIFEN (-)")
    elif '(' in txt and 'X' in txt:
        print(f"    -> MULTIPLICADOR (X)")
