#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 Teste de Extração de Desenhos do DXF

Valida sistema de extração automática de desenhos técnicos
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 70)
print("🧪 TESTE - Extração Automática de Desenhos do DXF")
print("=" * 70)

# 1️⃣ Verificar módulo desenho_extractor
try:
    from core.desenho_extractor import (
        renderizar_desenho_dxf,
        localizar_desenho_viga_no_dxf,
        extrair_bbox_entidades
    )
    print("✅ Módulo desenho_extractor importado")
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
    sys.exit(1)

# 2️⃣ Verificar etiquetas_helper atualizado
try:
    from core.etiquetas_helper import DESENHO_EXTRACTOR_DISPONIVEL
    if DESENHO_EXTRACTOR_DISPONIVEL:
        print("✅ Extrator integrado ao etiquetas_helper")
    else:
        print("⚠️  Extrator NÃO disponível no helper")
except Exception as e:
    print(f"⚠️  Erro: {e}")

# 3️⃣ Testar com DXF real
DXF_TEST = "P1_COMPLETO.dxf"
if os.path.exists(DXF_TEST):
    print(f"\n✅ DXF encontrado: {DXF_TEST}")
    
    try:
        print("🔄 Renderizando desenho completo...")
        img = renderizar_desenho_dxf(DXF_TEST, 300, 200)
        if img:
            img.save("teste_desenho_full.png")
            print(f"✅ Desenho completo salvo: teste_desenho_full.png ({img.size})")
        else:
            print("⚠️  Não foi possível renderizar")
    except Exception as e:
        print(f"❌ Erro ao renderizar: {e}")
        import traceback
        traceback.print_exc()
    
    # Testar extração de viga específica
    try:
        print("\n🔄 Tentando localizar V_GERAL...")
        img_viga = localizar_desenho_viga_no_dxf(DXF_TEST, "V_GERAL", "N8", 200, 150)
        if img_viga:
            img_viga.save("teste_desenho_viga.png")
            print(f"✅ Desenho da viga salvo: teste_desenho_viga.png ({img_viga.size})")
        else:
            print("⚠️  Desenho da viga não localizado")
    except Exception as e:
        print(f"❌ Erro ao localizar viga: {e}")
else:
    print(f"⚠️  DXF não encontrado: {DXF_TEST}")

print("\n" + "=" * 70)
print("✅ TESTE CONCLUÍDO")
print("=" * 70)
print("\n📋 Próximos passos:")
print("1. Execute: .venv\\Scripts\\python.exe main.py")
print("2. Carregue o DXF e gere as etiquetas")
print("3. Os desenhos serão extraídos automaticamente do DXF")
print("4. Se não encontrar PNG pré-renderizado, renderiza do DXF na hora")
