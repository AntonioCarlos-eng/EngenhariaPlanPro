#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔍 Análise de Textos no DXF
Mostra todos os textos TEXT/MTEXT para entender a nomenclatura das vigas/posições
"""

import ezdxf
import sys

DXF_FILE = "P1_COMPLETO.dxf"

print("=" * 70)
print(f"🔍 Analisando textos em: {DXF_FILE}")
print("=" * 70)

try:
    dxf = ezdxf.readfile(DXF_FILE)
    msp = dxf.modelspace()
except Exception as e:
    print(f"❌ Erro ao ler DXF: {e}")
    sys.exit(1)

textos = []

# Buscar TEXT entities
for entity in msp.query("TEXT"):
    if hasattr(entity, 'dxf'):
        texto = entity.dxf.text.strip()
        layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else ''
        x, y = entity.dxf.insert.x, entity.dxf.insert.y
        textos.append((texto, layer, x, y))

# Buscar MTEXT entities
for entity in msp.query("MTEXT"):
    if hasattr(entity, 'text'):
        texto = entity.text.strip()
        layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else ''
        x, y = entity.dxf.insert.x, entity.dxf.insert.y
        textos.append((texto, layer, x, y))

print(f"\n✅ Total de textos encontrados: {len(textos)}\n")

# Filtrar textos relevantes (com V ou N)
relevantes = [(t, l, x, y) for t, l, x, y in textos if 'V' in t.upper() or 'N' in t.upper()]

print("=" * 70)
print("📋 Textos relevantes (com V ou N):")
print("=" * 70)

for i, (texto, layer, x, y) in enumerate(relevantes[:50], 1):  # Primeiros 50
    print(f"{i:3d}. '{texto}' | Layer: {layer} | ({x:.1f}, {y:.1f})")

print("\n" + "=" * 70)
print(f"📊 Total relevantes: {len(relevantes)}")
print("=" * 70)

# Estatísticas de layers
layers_unicos = set(l for _, l, _, _ in relevantes)
print(f"\n🗂️  Layers únicos com textos relevantes:")
for layer in sorted(layers_unicos):
    count = len([1 for _, l, _, _ in relevantes if l == layer])
    print(f"   - {layer}: {count} textos")
