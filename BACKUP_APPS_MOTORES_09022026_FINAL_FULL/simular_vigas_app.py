#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 Simulação do Fluxo do vigas_app
"""

import sys
import os

print("=" * 70)
print("🧪 SIMULAÇÃO VIGAS_APP")
print("=" * 70)

# Simular o fluxo completo
print("\n1️⃣ Importando módulos...")

try:
    from core.etiquetas_generator import GeradorEtiquetasDinamico
    print("   ✅ GeradorEtiquetasDinamico OK")
except Exception as e:
    print(f"   ❌ GeradorEtiquetasDinamico FALHOU: {e}")
    sys.exit(1)

print("\n2️⃣ Criando gerador com DXF...")

dxf_file = "dxf/vig terreo f 1-R2 - Copia.DXF"
if not os.path.exists(dxf_file):
    print(f"   ❌ DXF não existe: {dxf_file}")
    sys.exit(1)

try:
    gerador = GeradorEtiquetasDinamico(
        arquivos_dxf=[dxf_file],
        obra="OBRA - 001",
        pavimento="ARMADO"
    )
    print(f"   ✅ Gerador criado")
    print(f"   • pasta_etiquetas: {gerador.pasta_etiquetas}")
    print(f"   • arquivo_dxf_base: {gerador.arquivo_dxf_base}")
    print(f"   • arquivos_dxf: {gerador.arquivos_dxf}")
    print(f"   • Total de barras: {len(gerador.dados)}")
except Exception as e:
    print(f"   ❌ Erro ao criar gerador: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n3️⃣ Testando primeira etiqueta...")

if gerador.dados:
    primeira = gerador.dados[0]
    viga, pos, bitola, qtde, comp, peso = primeira
    print(f"   • Viga: {viga}")
    print(f"   • Pos: {pos}")
    print(f"   • Bitola: {bitola}mm")
    print(f"   • Qtde: {qtde}")
    print(f"   • Comp: {comp}m")
    
    print("\n4️⃣ Testando localização de desenho...")
    
    from core.etiquetas_helper import localizar_desenho_barra
    
    # Usar dados do gerador
    caminho_dxf_completo = gerador.arquivos_dxf[0] if gerador.arquivos_dxf else None
    pasta = gerador.pasta_etiquetas
    arq_base = gerador.arquivo_dxf_base
    
    print(f"   • pasta: {pasta}")
    print(f"   • arq_base: {arq_base}")
    print(f"   • DXF completo: {caminho_dxf_completo}")
    
    caminho_png = localizar_desenho_barra(
        pasta,
        caminho_dxf_completo if caminho_dxf_completo else arq_base,
        viga, pos, bitola, qtde, comp * 100.0
    )
    
    print(f"   • Resultado: {caminho_png}")
    
    if caminho_png:
        if caminho_png.startswith("DXF:"):
            print(f"   ✅ Marcador DXF retornado - extração dinâmica será usada")
            print(f"   • Marcador completo: {caminho_png}|{viga}|{pos}")
        else:
            print(f"   ✅ PNG encontrado: {caminho_png}")
    else:
        print(f"   ❌ Nenhum desenho encontrado")

print("\n" + "=" * 70)
print("✅ SIMULAÇÃO CONCLUÍDA")
print("=" * 70)
print("\n💡 CONCLUSÃO:")
print("   Se chegou até aqui sem erros, o vigas_app deve funcionar!")
print("   O desenho será extraído dinamicamente do DXF.")
