#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Análise visual completa do DXF"""
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
            textos_completos.append((txt, x, y, 'TEXT'))
        elif entity.dxftype() == 'MTEXT':
            txt = entity.plain_text()
            x = entity.dxf.insert[0]
            y = entity.dxf.insert[1]
            textos_completos.append((txt, x, y, 'MTEXT'))
    except:
        pass

# Ordena por Y (de cima para baixo)
textos_ordenados = sorted(textos_completos, key=lambda t: t[2], reverse=True)

print("="*100)
print("CONTEUDO COMPLETO DO DXF - ORDENADO DE CIMA PARA BAIXO")
print("="*100)

for i, (txt, x, y, tipo) in enumerate(textos_ordenados[:150]):
    print(f"{i+1:3d}. Y={y:7.2f} X={x:7.2f} | {tipo:5s} | '{txt}'")

print("\n" + "="*100)
print(f"Total de texto no arquivo: {len(textos_completos)}")
print("="*100)
