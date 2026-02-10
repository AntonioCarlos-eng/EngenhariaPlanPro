#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 Teste de Importações
"""

print("=" * 70)
print("🧪 TESTE DE IMPORTAÇÕES")
print("=" * 70)

print("\n1. Testando barcode...")
try:
    import barcode
    from barcode.writer import ImageWriter
    print("   ✅ barcode OK")
except ImportError as e:
    print(f"   ❌ barcode FALHOU: {e}")

print("\n2. Testando PIL...")
try:
    from PIL import Image, ImageTk
    print("   ✅ PIL OK")
except ImportError as e:
    print(f"   ❌ PIL FALHOU: {e}")

print("\n3. Testando ezdxf...")
try:
    import ezdxf
    print("   ✅ ezdxf OK")
except ImportError as e:
    print(f"   ❌ ezdxf FALHOU: {e}")

print("\n4. Testando desenho_extractor...")
try:
    from core.desenho_extractor import localizar_desenho_viga_no_dxf
    print("   ✅ desenho_extractor OK")
except ImportError as e:
    print(f"   ❌ desenho_extractor FALHOU: {e}")

print("\n5. Testando etiquetas_helper...")
try:
    from core.etiquetas_helper import (
        gerar_codigo_identificador,
        gerar_codigo_barras_imagem,
        localizar_desenho_barra,
        carregar_desenho_redimensionado
    )
    print("   ✅ etiquetas_helper OK")
except ImportError as e:
    print(f"   ❌ etiquetas_helper FALHOU: {e}")

print("\n" + "=" * 70)
print("✅ TESTE CONCLUÍDO")
print("=" * 70)
