#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔍 Análise Completa do DXF - Entidades e Estrutura
"""

import ezdxf
import sys

DXF_FILE = "P1_COMPLETO.dxf"

print("=" * 70)
print(f"🔍 ANÁLISE COMPLETA: {DXF_FILE}")
print("=" * 70)

try:
    dxf = ezdxf.readfile(DXF_FILE)
    msp = dxf.modelspace()
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

# 1. LAYERS
print("\n🗂️  LAYERS NO DXF:")
print("-" * 70)
for layer in dxf.layers:
    print(f"   - {layer.dxf.name}")

# 2. BLOCOS
print("\n📦 BLOCOS NO DXF:")
print("-" * 70)
blocos_usados = set()
for entity in msp.query("INSERT"):
    if hasattr(entity.dxf, 'name'):
        blocos_usados.add(entity.dxf.name)

if blocos_usados:
    for bloco in sorted(blocos_usados):
        print(f"   - {bloco}")
else:
    print("   (Nenhum bloco encontrado)")

# 3. TIPOS DE ENTIDADES
print("\n📊 TIPOS DE ENTIDADES:")
print("-" * 70)
tipos = {}
for entity in msp:
    tipo = entity.dxftype()
    tipos[tipo] = tipos.get(tipo, 0) + 1

for tipo, count in sorted(tipos.items(), key=lambda x: x[1], reverse=True):
    print(f"   - {tipo}: {count}")

# 4. TEXTOS COMPLETOS
print("\n📝 TODOS OS TEXTOS (TEXT + MTEXT):")
print("-" * 70)
textos_completos = []

for entity in msp.query("TEXT"):
    if hasattr(entity, 'dxf') and hasattr(entity.dxf, 'text'):
        texto = entity.dxf.text
        x, y = entity.dxf.insert.x, entity.dxf.insert.y
        layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else ''
        textos_completos.append(("TEXT", texto, x, y, layer))

for entity in msp.query("MTEXT"):
    if hasattr(entity, 'text'):
        texto = entity.text
        x, y = entity.dxf.insert.x, entity.dxf.insert.y
        layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else ''
        textos_completos.append(("MTEXT", texto, x, y, layer))

print(f"\nTotal: {len(textos_completos)} textos\n")
for tipo, texto, x, y, layer in textos_completos:
    print(f"{tipo:6s} | '{texto}' | ({x:.1f}, {y:.1f}) | Layer: {layer}")

# 5. AMOSTRA DE LINE/POLYLINE
print("\n📏 AMOSTRA DE GEOMETRIA (primeiras 10 linhas):")
print("-" * 70)
count = 0
for entity in msp.query("LINE LWPOLYLINE POLYLINE"):
    if count >= 10:
        break
    layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else ''
    print(f"   - {entity.dxftype()} no layer '{layer}'")
    count += 1

print("\n" + "=" * 70)
print("✅ ANÁLISE CONCLUÍDA")
print("=" * 70)
