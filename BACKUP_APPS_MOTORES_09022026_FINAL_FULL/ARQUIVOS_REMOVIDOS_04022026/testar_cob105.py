#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste com laje neg cob-105"""

import os
import sys
sys.path.insert(0, r'c:\EngenhariaPlanPro')

from core.lajes_motor import processar_lajes

arquivo = r'c:\EngenhariaPlanPro\temp_dxf\laje-neg-cob-105.DXF'

print("="*80)
print("TESTE: laje neg cob-105.DXF (LEITURA APENAS DE TABELA)")
print("="*80 + "\n")

dados, peso_total, total_pecas = processar_lajes([arquivo])

print("\n" + "="*80)
print("RESULTADO DA EXTRAÇÃO")
print("="*80)

if dados:
    print(f"\n✓ Total extraído: {len(dados)} posições únicas")
    print(f"✓ Total: {total_pecas} barras")
    print(f"✓ Peso total: {peso_total:.2f} kg")
    
    print("\n" + "-"*80)
    print("POSIÇÕES ENCONTRADAS:")
    print("-"*80)
    
    for i, dado in enumerate(dados, 1):
        elemento, pos_tipo, bitola, qtde, comp_m, largura, peso, dobra, medidas = dado
        print(f"{i:3d}. {pos_tipo:15s} Ø{bitola:4.1f}mm x {comp_m:6.2f}m x {int(qtde):5d} pç = {peso:9.2f}kg  [{dobra}]")
else:
    print("\n✗ NENHUM DADO EXTRAÍDO")

print("\n" + "="*80)
