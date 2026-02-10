#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste do novo motor de leitura estrutural de tabelas"""

import os
import sys
sys.path.insert(0, r'c:\EngenhariaPlanPro')

from core.lajes_motor_novo import processar_lajes

# Testa com arquivos reais
arquivos_teste = [
    r'c:\EngenhariaPlanPro\temp_dxf\laje tipo pos-091.DXF',
    r'c:\EngenhariaPlanPro\temp_dxf\laje tipo pos-092.DXF',
    r'c:\EngenhariaPlanPro\temp_dxf\laje tipo neg-093.DXF',
]

# Filtra arquivos existentes
arquivos_existentes = [f for f in arquivos_teste if os.path.exists(f)]
print(f"Arquivos encontrados: {len(arquivos_existentes)}\n")

# Processa
dados, peso_total, total_pecas = processar_lajes(arquivos_existentes)

print("\n" + "="*80)
print("RESULTADO DA EXTRAÇÃO")
print("="*80)

# Mostra resumo
for laje_atual in set(d[0] for d in dados):
    dados_laje = [d for d in dados if d[0] == laje_atual]
    print(f"\n{laje_atual}: {len(dados_laje)} posições, {sum(int(d[3]) for d in dados_laje)} barras")
    
    # Mostra primeiras linhas
    for dado in dados_laje[:5]:
        elemento, pos_tipo, bitola, qtde, comp_m, largura, peso, dobra, medidas = dado
        print(f"  {pos_tipo:15s} Ø{bitola:4.1f}mm x {comp_m:5.2f}m x {int(qtde):4d} pç = {peso:8.2f}kg")

print(f"\n{'='*80}")
print(f"TOTAIS GERAIS: {len(dados)} posições | {total_pecas} barras | {peso_total:.2f} kg")
