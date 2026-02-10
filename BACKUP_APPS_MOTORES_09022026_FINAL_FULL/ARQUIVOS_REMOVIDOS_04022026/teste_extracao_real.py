#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 Teste com DXF Real - Vigas T1
Testar extração de desenhos específicos do DXF com múltiplas vigas
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.desenho_extractor import localizar_desenho_viga_no_dxf

DXF_FILE = "dxf/#vigas t1-069.DXF"

print("=" * 70)
print("🧪 TESTE COM DXF REAL - Extração Regional")
print("=" * 70)
print(f"DXF: {DXF_FILE}\n")

# Baseado na análise, sabemos que tem V301, V302, V346 e posições N1-N15
testes = [
    ("V301", "N1", "V301 N1"),
    ("V301", "N2", "V301 N2"),
    ("V302", "N1", "V302 N1"),
    ("V346", "N1", "V346 N1"),
    ("V301", "N14", "V301 N14"),
]

for viga, pos, desc in testes:
    print(f"\n{'=' * 70}")
    print(f"🔍 {desc}")
    print(f"{'=' * 70}")
    
    try:
        img = localizar_desenho_viga_no_dxf(DXF_FILE, viga, pos, 220, 170)
        
        if img:
            nome = f"teste_real_{viga}_{pos}.png"
            img.save(nome)
            print(f"\n✅ SUCESSO! Salvo: {nome} ({img.size[0]}x{img.size[1]}px)")
        else:
            print(f"\n❌ Não encontrado")
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 70)
print("✅ TESTE CONCLUÍDO")
print("=" * 70)
print("\n📋 Verifique as imagens geradas:")
print("   - Devem mostrar APENAS o desenho da barra específica")
print("   - NÃO devem mostrar o projeto todo")
print("   - Devem ter cotas, detalhes e dimensões")
