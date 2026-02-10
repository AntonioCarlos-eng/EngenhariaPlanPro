#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
teste_integracao_completa.py
Testa o fluxo completo de extração como acontece na aplicação
"""

import os
import sys

os.chdir(r'c:\EngenhariaPlanPro')

# Simular imports
from core.etiquetas_helper import localizar_desenho_barra, carregar_desenho_redimensionado

print("=" * 80)
print("TESTE INTEGRAÇÃO COMPLETA")
print("=" * 80)

# Dados de teste
pasta_etiquetas = "export"
arquivo_dxf = r"dxf\vig terreo f 1-R2 - Copia.DXF"
viga = "V8"
pos = "N1"
bitola = 10.0
qtde = 2
comp_cm = 295.0

print(f"\n📋 Parâmetros:")
print(f"   Pasta: {pasta_etiquetas}")
print(f"   DXF: {arquivo_dxf}")
print(f"   Viga: {viga}")
print(f"   Pos: {pos}")
print(f"   Bitola: {bitola}")
print(f"   Qtde: {qtde}")
print(f"   Comp: {comp_cm}cm")

# ETAPA 1: Localizar desenho
print(f"\n1️⃣ Chamando localizar_desenho_barra...")
caminho_png = localizar_desenho_barra(
    pasta_etiquetas, 
    arquivo_dxf, 
    viga, pos, bitola, qtde, comp_cm
)

print(f"   Resultado: {caminho_png}")

if not caminho_png:
    print(f"❌ FALHA: localizar_desenho_barra retornou None")
    sys.exit(1)

# ETAPA 2: Adicionar formato DXF se necessário
if caminho_png.startswith("DXF:"):
    caminho_png_full = f"{caminho_png}|{viga}|{pos}"
    print(f"\n2️⃣ Formato DXF dinâmico:")
    print(f"   {caminho_png_full[:80]}...")
else:
    caminho_png_full = caminho_png
    print(f"\n2️⃣ PNG estático:")
    print(f"   {caminho_png}")

# ETAPA 3: Carregar desenho redimensionado
print(f"\n3️⃣ Chamando carregar_desenho_redimensionado...")
dw, dh = 220, 170
photo = carregar_desenho_redimensionado(caminho_png_full, dw, dh)

print(f"   Resultado: {photo}")

if photo:
    print(f"✅ SUCESSO: Desenho carregado com {dw}x{dh}px")
else:
    print(f"❌ FALHA: carregar_desenho_redimensionado retornou None")

print("\n" + "=" * 80)
