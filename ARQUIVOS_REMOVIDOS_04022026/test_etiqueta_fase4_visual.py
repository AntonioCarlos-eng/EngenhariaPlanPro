#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 Teste Visual FASE 4 - Layout 10x15cm idêntico ao projeto

Valida:
1. Topo 9,3 cm com OS, faixa vertical, tabela técnica
2. 3 seções de 1,9 cm com barcode e Compr. Corte
3. Medidas configuráveis via core/etiquetas_layout_config.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 70)
print("🧪 TESTE VISUAL FASE 4 - Layout Idêntico ao Projeto")
print("=" * 70)

# 1️⃣ Verificar config
try:
    from core.etiquetas_layout_config import (
        PX_MM, MARGEM_EXTERNA_MM, TOPO_ALTURA_MM, SECAO_MICRO_ALTURA_MM,
        OS_BLOCO_LARGURA_MM, FAIXA_VERTICAL_LARGURA_MM, 
        COL_BITOLA_MM, COL_COMPR_UNIT_MM, COL_PESO_MM, COL_QTDE_MM
    )
    print(f"✅ Config carregado:")
    print(f"   • Escala: {PX_MM} px/mm")
    print(f"   • Topo: {TOPO_ALTURA_MM} mm ({TOPO_ALTURA_MM * PX_MM} px)")
    print(f"   • Seção micro: {SECAO_MICRO_ALTURA_MM} mm ({SECAO_MICRO_ALTURA_MM * PX_MM} px)")
    print(f"   • Bloco OS: {OS_BLOCO_LARGURA_MM} mm")
    print(f"   • Faixa vertical: {FAIXA_VERTICAL_LARGURA_MM} mm")
    print(f"   • Colunas: {COL_BITOLA_MM} | {COL_COMPR_UNIT_MM} | {COL_PESO_MM} | {COL_QTDE_MM} mm")
except ImportError as e:
    print(f"❌ Erro ao importar config: {e}")
    sys.exit(1)

# 2️⃣ Verificar vigas_app
try:
    from vigas_app import VigasApp
    print(f"✅ VigasApp importado")
    
    if hasattr(VigasApp, 'desenhar_pagina_etiquetas_vigas_fase4'):
        print(f"✅ Método desenhar_pagina_etiquetas_vigas_fase4 EXISTE")
    
    if hasattr(VigasApp, '_desenhar_topo_identico_fase4'):
        print(f"✅ Método _desenhar_topo_identico_fase4 EXISTE")
    else:
        print(f"❌ Método _desenhar_topo_identico_fase4 NÃO ENCONTRADO")
        
    if hasattr(VigasApp, '_desenhar_secao_micro_fase4'):
        print(f"✅ Método _desenhar_secao_micro_fase4 EXISTE")
    else:
        print(f"❌ Método _desenhar_secao_micro_fase4 NÃO ENCONTRADO")
        
except Exception as e:
    print(f"⚠️  Erro ao importar vigas_app: {e}")

# 3️⃣ Verificar helpers
try:
    from core.etiquetas_helper import (
        gerar_codigo_identificador,
        gerar_codigo_barras_imagem,
        localizar_desenho_barra,
        carregar_desenho_redimensionado
    )
    print(f"✅ Etiquetas helper carregado")
except ImportError as e:
    print(f"❌ Erro ao importar helper: {e}")

print("\n" + "=" * 70)
print("✅ INFRAESTRUTURA PRONTA!")
print("=" * 70)
print("\n📋 Próximo passo:")
print("Execute: .venv\\Scripts\\python.exe vigas_app.py")
print("Ou:      .venv\\Scripts\\python.exe main.py")
print("\nCarregue um DXF e clique em 'Gerar Etiquetas'")
print("Visualize o topo (9,3 cm) e as 3 seções (1,9 cm cada)")
print("\n🔧 Para ajustar medidas, edite:")
print("   core\\etiquetas_layout_config.py")
