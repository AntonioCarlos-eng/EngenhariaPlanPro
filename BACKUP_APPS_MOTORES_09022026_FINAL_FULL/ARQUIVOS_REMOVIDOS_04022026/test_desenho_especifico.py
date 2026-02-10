#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 Teste de Extração por Viga/Posição Específica

Testa se o sistema extrai apenas o desenho da barra, não o projeto todo
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 70)
print("🧪 TESTE - Extração de Desenho Específico por Viga/Posição")
print("=" * 70)

try:
    from core.desenho_extractor import localizar_desenho_viga_no_dxf
    print("✅ Módulo importado")
except ImportError as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

DXF_TEST = "P1_COMPLETO.dxf"
if not os.path.exists(DXF_TEST):
    print(f"⚠️  DXF não encontrado: {DXF_TEST}")
    sys.exit(1)

print(f"✅ DXF: {DXF_TEST}\n")

# Testar com diferentes vigas/posições
testes = [
    ("V8", "N1"),
    ("V_GERAL", "N8"),
    ("V9", "N1"),
    ("V10", "N1"),
]

for viga, pos in testes:
    print(f"🔄 Testando {viga} {pos}...")
    try:
        img = localizar_desenho_viga_no_dxf(DXF_TEST, viga, pos, 250, 180)
        if img:
            nome_arquivo = f"teste_desenho_{viga}_{pos}.png"
            img.save(nome_arquivo)
            print(f"   ✅ Salvo: {nome_arquivo} ({img.size})")
        else:
            print(f"   ⚠️  Desenho não localizado")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    print()

print("=" * 70)
print("✅ TESTE CONCLUÍDO")
print("=" * 70)
print("\n📋 Verificar:")
print("- Imagens PNG devem mostrar APENAS o desenho da barra")
print("- NÃO deve mostrar o projeto todo")
print("- Deve ter cotas, dimensões e detalhes da posição")
