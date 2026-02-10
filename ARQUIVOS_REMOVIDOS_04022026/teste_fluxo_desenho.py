#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 Teste Completo do Fluxo de Desenho
"""

import os
import sys

print("=" * 70)
print("🧪 TESTE FLUXO DE DESENHO")
print("=" * 70)

# 1. Importar funções
from core.etiquetas_helper import localizar_desenho_barra, carregar_desenho_redimensionado

# 2. Simular dados de uma etiqueta real
pasta_etiquetas = "etiquetas"
dxf_file = "dxf/vig terreo f 1-R2 - Copia.DXF"
viga = "V8"
pos = "N1"
bitola = 10.0
qtde = 2
comp_cm = 295.0

print(f"\n📋 Dados da etiqueta:")
print(f"   DXF: {dxf_file}")
print(f"   Viga: {viga}, Pos: {pos}")
print(f"   Bitola: {bitola}mm, Qtde: {qtde}, Comp: {comp_cm}cm")

# 3. Verificar se DXF existe
if os.path.exists(dxf_file):
    print(f"   ✅ DXF existe")
else:
    print(f"   ❌ DXF NÃO existe!")
    print(f"   Caminho: {os.path.abspath(dxf_file)}")

# 4. Tentar localizar desenho
print(f"\n🔍 Localizando desenho...")
caminho_png = localizar_desenho_barra(
    pasta_etiquetas, 
    dxf_file, 
    viga, pos, bitola, qtde, comp_cm
)

print(f"   Resultado: {caminho_png}")

if caminho_png:
    # 5. Se encontrou, tentar carregar
    print(f"\n📥 Carregando desenho...")
    
    # Se é marcador DXF, adicionar viga|pos
    if caminho_png.startswith("DXF:"):
        caminho_png_completo = f"{caminho_png}|{viga}|{pos}"
        print(f"   Marcador DXF: {caminho_png_completo}")
    else:
        caminho_png_completo = caminho_png
        print(f"   PNG direto: {caminho_png_completo}")
    
    # Tentar carregar (220x170 pixels)
    try:
        photo = carregar_desenho_redimensionado(caminho_png_completo, 220, 170)
        if photo:
            print(f"   ✅ Desenho carregado: {type(photo)}")
        else:
            print(f"   ❌ Desenho retornou None")
    except Exception as e:
        print(f"   ❌ Erro ao carregar: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"\n❌ Desenho NÃO localizado")

print("\n" + "=" * 70)
print("✅ TESTE CONCLUÍDO")
print("=" * 70)
