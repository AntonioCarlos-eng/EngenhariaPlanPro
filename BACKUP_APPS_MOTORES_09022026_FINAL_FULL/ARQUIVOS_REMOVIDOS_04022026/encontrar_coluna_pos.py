#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Encontrar todas as posições e sua coluna X"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import ezdxf
from ezdxf.recover import readfile as recover_readfile

arquivo = r'c:\EngenhariaPlanPro\laje-neg-cob-105-original.DXF'
doc, auditor = recover_readfile(arquivo)

textos_completos = []
for entity in doc.entities:
    if not entity.is_alive:
        continue
    
    try:
        if entity.dxftype() == 'TEXT':
            txt = entity.dxf.text
            x = entity.dxf.insert[0]
            y = entity.dxf.insert[1]
            textos_completos.append((txt, x, y))
        elif entity.dxftype() == 'MTEXT':
            txt = entity.plain_text()
            x = entity.dxf.insert[0]
            y = entity.dxf.insert[1]
            textos_completos.append((txt, x, y))
    except:
        pass

# Ordena por Y
textos_ordenados = sorted(textos_completos, key=lambda t: t[2], reverse=True)

print("="*100)
print("PROCURANDO COLUNA DE POSICOES")
print("="*100)

# Encontra textos que parecem ser posições (números pequenos como 1, 2, 3... 10, 11, 12...)
posicoes = {}

for txt, x, y in textos_completos:
    txt_strip = txt.strip()
    
    # Se é só número e está entre 1 e 57
    if txt_strip.isdigit():
        num = int(txt_strip)
        if 1 <= num <= 57:
            if x not in posicoes:
                posicoes[x] = []
            posicoes[x].append((num, y))

# Encontra a coluna com mais posições (deve ser a coluna de POS)
col_counts = {x: len(vals) for x, vals in posicoes.items()}
melhor_col = max(col_counts, key=col_counts.get)

print(f"\nColuna X={melhor_col:.2f} tem {col_counts[melhor_col]} posicoes")
print("\nTodas as posicoes em ordem de aparição (Y):")

posicoes_desta_coluna = sorted(posicoes[melhor_col], key=lambda p: p[1], reverse=True)
for pos, y in posicoes_desta_coluna:
    print(f"  POS={pos:2d} em Y={y:7.2f}")

print(f"\nPositicoes encontradas: {sorted([p[0] for p in posicoes_desta_coluna])}")
