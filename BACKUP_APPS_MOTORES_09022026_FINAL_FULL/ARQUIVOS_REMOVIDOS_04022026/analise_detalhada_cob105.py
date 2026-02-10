#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Análise detalhada da estrutura do DXF laje neg cob-105"""

import ezdxf
from ezdxf.recover import readfile as recover_readfile
import re

arquivo = r'c:\EngenhariaPlanPro\temp_dxf\laje-neg-cob-105.DXF'

print("="*100)
print("ANÁLISE DETALHADA DO DXF - laje neg cob-105")
print("="*100)

doc, auditor = recover_readfile(arquivo)

# Coleta TODOS os textos com coordenadas
textos_completos = []

for entity in doc.entities:
    if not entity.is_alive:
        continue
    
    try:
        if entity.dxftype() == 'TEXT':
            txt = entity.dxf.text
            x = entity.dxf.insert[0]
            y = entity.dxf.insert[1]
            textos_completos.append((txt, x, y, 'TEXT'))
        elif entity.dxftype() == 'MTEXT':
            txt = entity.plain_text()
            x = entity.dxf.insert[0]
            y = entity.dxf.insert[1]
            textos_completos.append((txt, x, y, 'MTEXT'))
    except:
        pass

print(f"\nTotal de textos: {len(textos_completos)}")

# Agrupa por Y (linhas da tabela)
textos_ordenados = sorted(textos_completos, key=lambda t: t[2], reverse=True)

# Identifica região da tabela (procura por cabeçalhos)
print("\n" + "="*100)
print("PROCURANDO CABEÇALHO DA TABELA")
print("="*100)

for i, (txt, x, y, tipo) in enumerate(textos_ordenados[:100]):
    txt_upper = txt.upper()
    if any(palavra in txt_upper for palavra in ['AÇO', 'POS', 'BIT', 'QUANT', 'COMP', 'PESO']):
        print(f"Y={y:6.2f} | X={x:6.2f} | {tipo:5s} | '{txt}'")

# Agrupa textos por linha (Y com tolerância)
print("\n" + "="*100)
print("PRIMEIRAS 30 LINHAS DA TABELA (agrupadas por Y)")
print("="*100)

linhas = []
linha_atual = []
y_ref = None
tolerancia = 0.3

for txt, x, y, tipo in textos_ordenados:
    if y_ref is None:
        y_ref = y
        linha_atual = [(txt, x, y)]
    elif abs(y - y_ref) <= tolerancia:
        linha_atual.append((txt, x, y))
    else:
        if linha_atual:
            linha_ordenada = sorted(linha_atual, key=lambda t: t[1])
            linhas.append((y_ref, linha_ordenada))
        y_ref = y
        linha_atual = [(txt, x, y)]

if linha_atual:
    linha_ordenada = sorted(linha_atual, key=lambda t: t[1])
    linhas.append((y_ref, linha_ordenada))

# Mostra primeiras 30 linhas
for i, (y_linha, tokens) in enumerate(linhas[:30]):
    tokens_texto = [t[0] for t in tokens]
    print(f"\nLinha {i+1:2d} (Y={y_linha:6.2f}): {len(tokens)} tokens")
    print(f"  Tokens: {' | '.join(tokens_texto[:15])}")  # Primeiros 15

# Procura por padrões de posição N1, N2, etc
print("\n" + "="*100)
print("POSIÇÕES ENCONTRADAS (N1, N2, N3...)")
print("="*100)

posicoes_encontradas = {}
for y_linha, tokens in linhas:
    tokens_texto = [t[0] for t in tokens]
    linha_texto = ' '.join(tokens_texto)
    
    # Procura por N seguido de número
    matches = re.finditer(r'\bN(\d+)\b', linha_texto, re.IGNORECASE)
    for match in matches:
        pos_num = int(match.group(1))
        if pos_num not in posicoes_encontradas:
            posicoes_encontradas[pos_num] = []
        posicoes_encontradas[pos_num].append((y_linha, tokens_texto))

print(f"\nTotal de posições únicas encontradas: {len(posicoes_encontradas)}")
print("\nPrimeiras 10 posições com suas linhas:")

for pos_num in sorted(posicoes_encontradas.keys())[:10]:
    ocorrencias = posicoes_encontradas[pos_num]
    print(f"\n  N{pos_num}: {len(ocorrencias)} ocorrência(s)")
    for y, tokens in ocorrencias[:2]:  # Mostra até 2 ocorrências
        print(f"    Y={y:6.2f}: {' | '.join(tokens[:10])}")

# Procura por padrão específico: N + número + bitola + quantidade + comprimento
print("\n" + "="*100)
print("ANÁLISE DE ESTRUTURA DE COLUNAS")
print("="*100)

print("\nProcurando padrão: [AÇO] [POS] [BITOLA] [QUANTIDADE] [COMPRIMENTO]")
print("\nPrimeiras 20 linhas que parecem ser dados de tabela:")

contador = 0
for y_linha, tokens in linhas:
    if contador >= 20:
        break
    
    tokens_texto = [t[0].strip() for t in tokens if t[0].strip()]
    
    # Procura por linha que tenha números
    tem_numero = any(re.search(r'\d', t) for t in tokens_texto)
    if not tem_numero or len(tokens_texto) < 3:
        continue
    
    # Verifica se não é cabeçalho
    if any(palavra in ' '.join(tokens_texto).upper() for palavra in ['AÇO', 'POS', 'BIT', 'QUANT']):
        continue
    
    print(f"\nY={y_linha:6.2f}: {len(tokens_texto)} tokens")
    for j, token in enumerate(tokens_texto[:8]):
        print(f"  [{j}] '{token}'")
    
    contador += 1

print("\n" + "="*100)
