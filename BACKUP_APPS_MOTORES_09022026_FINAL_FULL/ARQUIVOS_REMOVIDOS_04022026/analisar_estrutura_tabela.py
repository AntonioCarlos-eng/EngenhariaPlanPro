#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para analisar a estrutura de tabela nos DXF de lajes
"""

import ezdxf
from ezdxf.recover import readfile as recover_readfile
import os

arquivo = r"c:\EngenhariaPlanPro\temp_dxf\laje tipo pos-092.DXF"

print(f"Analisando: {os.path.basename(arquivo)}")
print("=" * 80)

doc, auditor = recover_readfile(arquivo)

# Procura por TABLE entities
print("\n1. PROCURANDO POR TABELAS (TABLE ENTITIES):")
print("-" * 80)
tabelas = []
for entity in doc.entities:
    if entity.dxftype() == 'TABLE':
        tabelas.append(entity)
        print(f"✓ Encontrada TABLE entity")

if not tabelas:
    print("❌ Nenhuma TABLE entity encontrada")

# Procura por MTEXT que indique tipo de armadura
print("\n2. PROCURANDO POR TÍTULOS DE ARMADURA (MTEXT):")
print("-" * 80)
for entity in doc.entities:
    if entity.dxftype() == 'MTEXT':
        try:
            txt = entity.plain_text().upper()
            if any(palavra in txt for palavra in ['NEGATIVA', 'POSITIVA', 'HORIZONTAL', 'VERTICAL', 'ARMADURA', 'REFORÇO', 'ARMAD']):
                print(f"✓ {txt[:100]}")
        except:
            pass

# Extrai textos e ordena por Y para reconstruir tabela
print("\n3. ANALISANDO ESTRUTURA DE TEXTO:")
print("-" * 80)
textos = []
for entity in doc.entities:
    if entity.dxftype() == 'TEXT':
        try:
            txt = entity.dxf.text
            x = entity.dxf.insert[0]
            y = entity.dxf.insert[1]
            if txt.strip():
                textos.append((txt.strip(), x, y))
        except:
            pass

print(f"Total de textos: {len(textos)}")

# Agrupa por Y
textos_por_y = {}
for txt, x, y in textos:
    y_round = round(y, 1)
    if y_round not in textos_por_y:
        textos_por_y[y_round] = []
    textos_por_y[y_round].append((txt, x))

# Detecta cabeçalhos (linhas com múltiplos textos alinhados)
print("\nLINHAS COM ESTRUTURA DE TABELA (multiplos textos):")
print("-" * 80)
linhas_tabela = []
for y in sorted(textos_por_y.keys(), reverse=True):
    linha = textos_por_y[y]
    if len(linha) >= 3:  # Pelo menos 3 colunas
        linha_ordenada = sorted(linha, key=lambda t: t[1])
        textos_linha = [txt for txt, x in linha_ordenada]
        linhas_tabela.append((y, textos_linha))
        
        # Mostra linha
        linha_str = " | ".join(textos_linha[:7])  # Primeiras 7 colunas
        print(f"Y={y:7.1f}: {linha_str[:120]}")

print(f"\nTotal de linhas de tabela: {len(linhas_tabela)}")

# Tenta detectar cabeçalho
print("\n4. DETECTANDO CABEÇALHO:")
print("-" * 80)
if linhas_tabela:
    y_first, textos_first = linhas_tabela[0]
    print(f"Primeira linha (cabeçalho provável):")
    print(f"  {textos_first}")
    
    # Verifica se parece um cabeçalho
    palavras_cabecalho = ['A/0', 'POS', 'BIT', 'QTD', 'QUANT', 'COMPR', 'COMP', 'PESO', 'TOTAL', 'C=', 'N']
    eh_cabecalho = any(any(p in str(t).upper() for p in palavras_cabecalho) for t in textos_first)
    print(f"  Parece ser cabeçalho: {eh_cabecalho}")

print("\n" + "=" * 80)
print("ANÁLISE CONCLUÍDA")
