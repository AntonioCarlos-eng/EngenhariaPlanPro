#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
teste_extracao_direto.py - Teste direto da extração
"""

import sys
sys.path.insert(0, '/EngenhariaPlanPro')

from core.desenho_extractor import localizar_desenho_viga_no_dxf
from PIL import Image

print("=" * 60)
print("TESTE DE EXTRAÇÃO DIRETA")
print("=" * 60)

dxf_path = r"dxf\vig terreo f 1-R2 - Copia.DXF"
viga = "V8"
pos = "N1"

print(f"\nTestando: {viga} / {pos}")
print(f"DXF: {dxf_path}")

img = localizar_desenho_viga_no_dxf(dxf_path, viga, pos, 220, 170)

if img:
    print(f"\n✅ SUCESSO - Imagem gerada: {img.size}")
    img.save("teste_direto_v8_n1.png")
    print(f"   Salvo em: teste_direto_v8_n1.png")
else:
    print(f"\n❌ FALHA - Retornou None")

print("=" * 60)
