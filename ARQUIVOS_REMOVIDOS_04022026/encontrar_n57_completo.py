#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Encontrar todos os N1 a N57 com seus dados corretos"""
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

# Agrupa por Y
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

print("="*100)
print("PROCURANDO TODAS AS 57 POSICOES - ANALISE MANUAL")
print("="*100)

# Extrai dados linha por linha
dados_posicoes = {}

for y_linha, tokens in linhas:
    tokens_texto = [t[0].strip() for t in tokens if t[0].strip()]
    
    if len(tokens_texto) < 3:
        continue
    
    # Procura por "POS" seguido de número
    linha_str = ' '.join(tokens_texto)
    
    # Tenta encontrar padrão: ... POS=numero BIT=numero QTDE=numero ...
    matches_pos = re.finditer(r'(?:POS|N|pos)[\s=]?(\d+)', linha_str, re.IGNORECASE)
    
    for match_pos in matches_pos:
        pos_num = int(match_pos.group(1))
        
        if 1 <= pos_num <= 60:  # Posição válida
            # Procura por bitola na mesma linha
            matches_bit = re.finditer(r'(?:BIT|%%c|Ø)?[\s=]?(\d+[.,]?\d*)', linha_str)
            
            for match_bit in matches_bit:
                bit_str = match_bit.group(1).replace(',', '.')
                try:
                    bitola = float(bit_str)
                    if 3 <= bitola <= 50:  # Bitola válida
                        # Procura por quantidade
                        matches_qtd = re.finditer(r'(\d+)(?:\s+pç|\s+pc|$)', linha_str)
                        
                        encontrou = False
                        for match_qtd in matches_qtd:
                            qtd = int(match_qtd.group(1))
                            if 1 <= qtd <= 10000:
                                chave = (pos_num, bitola)
                                if chave not in dados_posicoes:
                                    dados_posicoes[chave] = (qtd, y_linha, ' | '.join(tokens_texto[:8]))
                                encontrou = True
                                break
                        
                        if encontrou:
                            break
                except:
                    pass

print(f"\nPosicoes encontradas: {len(set(p[0] for p in dados_posicoes.keys()))}")
print(f"Total de registros: {len(dados_posicoes)}")

print("\n" + "="*100)
print("POSICOES E DADOS:")
print("="*100)

for (pos, bit), (qtd, y, linha_preview) in sorted(dados_posicoes.items()):
    print(f"N{pos:2d} Ø{bit:5.1f}mm QtdePrev: {qtd:4d}  Y={y:6.2f}  |  {linha_preview}")
