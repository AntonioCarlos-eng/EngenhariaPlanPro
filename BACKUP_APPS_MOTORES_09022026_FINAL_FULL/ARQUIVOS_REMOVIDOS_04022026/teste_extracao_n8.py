#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 Teste Específico - Extrair N8 do P1_COMPLETO.dxf
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.desenho_extractor import localizar_desenho_viga_no_dxf

DXF_FILE = "P1_COMPLETO.dxf"

print("=" * 70)
print("🧪 TESTE - Extrair desenho específico")
print("=" * 70)

# O DXF tem o texto "28 N8 Ø5.0  C=75"
# Isso indica:
# - Posição: N8
# - Bitola: 5.0mm  
# - Comprimento: 75cm
# - Quantidade: 28

# Vamos tentar extrair com diferentes identificações
testes = [
    # (viga, pos, descrição)
    ("V_GERAL", "N8", "Tentativa 1: V_GERAL N8"),
    ("GERAL", "N8", "Tentativa 2: GERAL N8"),
    ("P1", "N8", "Tentativa 3: P1 N8 (usando o texto 'P1' do DXF)"),
    ("", "N8", "Tentativa 4: Apenas N8"),
    ("V8", "N1", "Tentativa 5: V8 N1 (deveria falhar)"),
]

for viga, pos, descricao in testes:
    print(f"\n{descricao}")
    print(f"   Buscando: viga='{viga}' pos='{pos}'")
    
    try:
        img = localizar_desenho_viga_no_dxf(DXF_FILE, viga, pos, 250, 180)
        
        if img:
            nome = f"teste_extracao_{viga}_{pos}.png".replace(" ", "_")
            img.save(nome)
            print(f"   ✅ SUCESSO! Salvo: {nome}")
        else:
            print(f"   ⚠️  Não encontrado")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print("\n" + "=" * 70)
print("✅ TESTE CONCLUÍDO")
print("=" * 70)
