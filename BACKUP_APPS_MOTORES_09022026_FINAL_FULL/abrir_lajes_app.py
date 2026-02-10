#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para abrir e testar lajes_app.py"""

import os
import sys
sys.path.insert(0, r'c:\EngenhariaPlanPro')

print("✓ Iniciando teste de lajes_app.py...")
print("✓ Motor importado: core.lajes_motor (NEW - estrutural)")

# Testa importação
try:
    from core.lajes_motor import processar_lajes
    print("✓ processar_lajes() importado com sucesso")
except Exception as e:
    print(f"✗ Erro ao importar: {e}")
    sys.exit(1)

# Testa com um arquivo
arquivos_teste = [r'c:\EngenhariaPlanPro\temp_dxf\laje tipo pos-092.DXF']
print(f"\nTestando extração com: {os.path.basename(arquivos_teste[0])}")

try:
    dados, peso, pecas = processar_lajes(arquivos_teste)
    print(f"✓ Extração bem-sucedida: {len(dados)} posições, {pecas} barras, {peso:.2f}kg")
    
    # Mostra algumas linhas
    print("\nPrimeiras 5 posições:")
    for dado in dados[:5]:
        elemento, pos_tipo, bitola, qtde, comp_m, _, peso_item, dobra, _ = dado
        print(f"  {pos_tipo:15s} Ø{bitola:4.1f}mm x {comp_m:5.2f}m x {int(qtde):3d} pç")
    
except Exception as e:
    print(f"✗ Erro na extração: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓✓✓ Motor funcionando perfeitamente! ✓✓✓")
print("\nAgora vou abrir a interface gráfica...")
print("(Feche a janela quando terminar o teste)\n")

# Abre a app
try:
    from lajes_app import LajesApp
    app = LajesApp()
    app.mainloop()
except Exception as e:
    print(f"\n✗ Erro ao abrir app: {e}")
    import traceback
    traceback.print_exc()
