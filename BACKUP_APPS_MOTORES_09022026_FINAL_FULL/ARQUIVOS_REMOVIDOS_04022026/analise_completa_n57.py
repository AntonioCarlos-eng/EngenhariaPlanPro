#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Análise completa - todas as posições N1 até N57"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import ezdxf
from ezdxf.recover import readfile as recover_readfile
import re

arquivo = r'c:\EngenhariaPlanPro\temp_dxf\laje-neg-cob-105.DXF'

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

print("="*100)
print("PROCURANDO TODAS AS POSICOES N1 A N57")
print("="*100)

# Procura por todas as ocorrências de N seguido de número
posicoes_encontradas = {}

for txt, x, y in textos_completos:
    matches = re.finditer(r'\bN(\d+)\b', txt, re.IGNORECASE)
    for match in matches:
        pos_num = int(match.group(1))
        if pos_num not in posicoes_encontradas:
            posicoes_encontradas[pos_num] = []
        posicoes_encontradas[pos_num].append((txt, x, y))

print(f"\nTotal de posicoes encontradas: {len(posicoes_encontradas)}")
print(f"Posicoes: {sorted(posicoes_encontradas.keys())}")

# Agrupa por Y para ver linhas da tabela
textos_ordenados = sorted(textos_completos, key=lambda t: t[2], reverse=True)

linhas = []
linha_atual = []
y_ref = None
tolerancia = 0.3

for txt, x, y in textos_ordenados:
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

print(f"\nTotal de linhas: {len(linhas)}")

# Procura por padrões de tabela com posições
print("\n" + "="*100)
print("TODAS AS LINHAS COM ESTRUTURA DE TABELA")
print("="*100)

for i, (y_linha, tokens) in enumerate(linhas):
    tokens_texto = [t[0].strip() for t in tokens if t[0].strip()]
    
    # Procura por linhas que têm a estrutura: numero | numero | numero | numero | numero
    if len(tokens_texto) >= 5:
        # Tenta ver se segue padrão numérico
        primeiros = tokens_texto[:5]
        
        # Conta quantos são números
        num_count = sum(1 for t in primeiros if re.match(r'^[\d.]+$', t.replace(',', '.')))
        
        if num_count >= 4:  # Pelo menos 4 números seguidos = provável linha de tabela
            print(f"\nY={y_linha:6.2f}: {len(tokens_texto)} tokens | {' | '.join(primeiros)}")
            
            # Tenta extrair dados
            try:
                if len(tokens_texto) >= 5:
                    aco = tokens_texto[0]
                    pos = tokens_texto[1]
                    bit = tokens_texto[2]
                    qtd = tokens_texto[3]
                    comp = tokens_texto[4]
                    
                    if re.match(r'^\d+$', aco) and re.match(r'^\d+$', pos) and re.match(r'^[\d.]+$', bit.replace(',', '.')):
                        print(f"  OK: ACO={aco}, POS={pos}, BIT={bit}, QTDE={qtd}, COMP={comp}")
            except:
                pass

print("\n" + "="*100)
print(f"RESUMO: {len(posicoes_encontradas)} posicoes unicas encontradas")
print("="*100)
