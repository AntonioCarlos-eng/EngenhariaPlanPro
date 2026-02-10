#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Análise detalhada da estrutura - comparando com DXF real"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import ezdxf
from ezdxf.recover import readfile as recover_readfile
import re

arquivo = r'c:\EngenhariaPlanPro\temp_dxf\laje-neg-cob-105.DXF'

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

print("="*100)
print("ANÁLISE ESTRUTURAL DA TABELA - laje neg cob-105")
print("="*100)

# Agrupa por Y
textos_ordenados = sorted(textos_completos, key=lambda t: t[2], reverse=True)

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

print(f"\nTotal de linhas agrupadas: {len(linhas)}")

# Encontra onde começa a tabela
cabeçalho_idx = -1
for i, (y_linha, tokens) in enumerate(linhas):
    tokens_texto = [t[0] for t in tokens]
    linha_texto = ' '.join(tokens_texto)
    if 'POS' in linha_texto.upper() and 'BIT' in linha_texto.upper():
        cabeçalho_idx = i
        print(f"\nCabeçalho encontrado na linha {i} (Y={y_linha:.2f})")
        print(f"Conteúdo: {' | '.join(tokens_texto)}")
        break

if cabeçalho_idx >= 0:
    print("\n" + "="*100)
    print("TODAS AS LINHAS DE DADOS DA TABELA (após cabeçalho)")
    print("="*100)
    
    dados_extraidos = []
    
    for i in range(cabeçalho_idx + 1, len(linhas)):
        y_linha, tokens = linhas[i]
        tokens_texto = [t[0].strip() for t in tokens if t[0].strip()]
        
        # Pula linhas de sub-cabeçalho
        if any(palavra in ' '.join(tokens_texto).upper() for palavra in ['(mm)', 'UNIT', 'TOTAL', 'PESO']):
            continue
        
        # Pula linhas com muito poucas colunas ou que não parecem dados
        if len(tokens_texto) < 4:
            continue
        
        # Verifica se primeira coluna é número (AÇO)
        if not re.match(r'^\d+$', tokens_texto[0]):
            # Se não é número, pode ser fim da tabela ou outra coisa
            if len(dados_extraidos) > 0:
                break
            continue
        
        print(f"\nLinha {i:2d} (Y={y_linha:6.2f}): {len(tokens_texto)} tokens")
        
        # Mostra os tokens em ordem
        for j, token in enumerate(tokens_texto[:8]):
            print(f"  [{j}] '{token}'")
        
        # Tenta extrair
        try:
            if len(tokens_texto) >= 5:
                aco = tokens_texto[0]
                pos = tokens_texto[1]
                bit = tokens_texto[2]
                qtd = tokens_texto[3]
                comp = tokens_texto[4]
                
                print(f"  EXTRAIDO: ACO={aco}, POS={pos}, BIT={bit}, QTDE={qtd}, COMP={comp}")
                dados_extraidos.append((int(pos), float(bit.replace(',', '.')), int(comp), int(qtd)))
        except Exception as e:
            print(f"  X Erro ao extrair: {e}")

    print(f"\n{'='*100}")
    print(f"TOTAL DE LINHAS DE DADOS EXTRAÍDAS: {len(dados_extraidos)}")
    print(f"{'='*100}")
    
    # Mostra resumo
    posicoes_unicas = sorted(set(d[0] for d in dados_extraidos))
    print(f"\nPosições únicas encontradas: {posicoes_unicas}")
    print(f"Total de posições únicas: {len(posicoes_unicas)}")
    
    # Agrupa por posição
    agrupado = {}
    for pos, bit, comp, qtd in dados_extraidos:
        chave = (pos, bit)
        if chave in agrupado:
            qtd_atual, comp_atual = agrupado[chave]
            agrupado[chave] = (qtd_atual + qtd, comp_atual)
        else:
            agrupado[chave] = (qtd, comp)
    
    print(f"\nApós agregação por (POS, BIT): {len(agrupado)} registros únicos")
