#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔍 Análise do DXF Real de Vigas
"""

import ezdxf
import sys

DXF_FILE = "dxf/#vigas t1-069.DXF"

print("=" * 70)
print(f"🔍 ANALISANDO: {DXF_FILE}")
print("=" * 70)

try:
    dxf = ezdxf.readfile(DXF_FILE)
    msp = dxf.modelspace()
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

# 1. Contar entidades
tipos = {}
for entity in msp:
    tipo = entity.dxftype()
    tipos[tipo] = tipos.get(tipo, 0) + 1

print("\n📊 TIPOS DE ENTIDADES:")
for tipo, count in sorted(tipos.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"   {tipo}: {count}")

# 2. Textos (amostra)
print("\n📝 AMOSTRA DE TEXTOS (primeiros 20):")
print("-" * 70)

textos = []
for entity in msp.query("TEXT"):
    if hasattr(entity, 'dxf') and hasattr(entity.dxf, 'text'):
        texto = entity.dxf.text
        x, y = entity.dxf.insert.x, entity.dxf.insert.y
        textos.append(("TEXT", texto, x, y))

for entity in msp.query("MTEXT"):
    if hasattr(entity, 'text'):
        texto = entity.text
        x, y = entity.dxf.insert.x, entity.dxf.insert.y
        textos.append(("MTEXT", texto, x, y))

print(f"\nTotal de textos: {len(textos)}\n")

for i, (tipo, texto, x, y) in enumerate(textos[:20], 1):
    print(f"{i:2d}. {tipo:6s} | '{texto[:50]}' | ({x:.0f}, {y:.0f})")

# 3. Buscar textos com identificação de viga
print("\n🔍 TEXTOS COM IDENTIFICAÇÃO (V, N):")
print("-" * 70)

relevantes = [(t, texto, x, y) for t, texto, x, y in textos 
              if 'V' in texto.upper()[:10] or 'N' in texto.upper()[:10]]

for i, (tipo, texto, x, y) in enumerate(relevantes[:30], 1):
    print(f"{i:2d}. '{texto[:60]}'")

# 4. Layers
print("\n🗂️  LAYERS:")
print("-" * 70)
layers = [layer.dxf.name for layer in dxf.layers]
for layer in sorted(layers)[:20]:
    print(f"   - {layer}")

print("\n" + "=" * 70)
print("✅ ANÁLISE CONCLUÍDA")
print("=" * 70)
