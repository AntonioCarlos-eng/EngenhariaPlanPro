#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para validar extração de lajes por coordenadas
"""

import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.lajes_motor import processar_lajes

def testar_arquivo(caminho):
    """Testa a extração de um arquivo DXF."""
    print("=" * 80)
    print(f"TESTANDO: {os.path.basename(caminho)}")
    print("=" * 80)
    
    if not os.path.exists(caminho):
        print(f"❌ Arquivo não encontrado: {caminho}")
        return
    
    try:
        dados, peso_total, total_pecas = processar_lajes([caminho])
        
        print(f"\n📊 RESULTADO:")
        print(f"   Posições encontradas: {len(dados)}")
        print(f"   Total de barras: {total_pecas}")
        print(f"   Peso total: {peso_total:.2f} kg")
        print()
        
        if dados:
            print("📋 PRIMEIRAS 10 POSIÇÕES:")
            print("-" * 80)
            for i, dado in enumerate(dados[:10], 1):
                elemento, pos, bitola, qtd, comp_m, larg, peso, formato, medidas = dado
                print(f"{i:2}. {elemento:<12} {pos:<12} Ø{bitola:<5.1f} "
                      f"{int(qtd):>3}x {comp_m:>5.2f}m = {peso:>6.2f}kg  {formato}")
            
            if len(dados) > 10:
                print(f"   ... e mais {len(dados) - 10} posições")
        else:
            print("⚠️  Nenhuma posição extraída!")
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Testa arquivos da pasta temp_dxf
    temp_dxf = r"c:\EngenhariaPlanPro\temp_dxf"
    
    arquivos_teste = [
        "laje tipo pos-092.DXF",
        "laje tipo neg-093.DXF",
        "laje tipo pos-091.DXF"
    ]
    
    for arquivo in arquivos_teste:
        caminho = os.path.join(temp_dxf, arquivo)
        if os.path.exists(caminho):
            testar_arquivo(caminho)
            print()
        else:
            print(f"⏭️  Pulando {arquivo} (não encontrado)")
    
    print("\n" + "=" * 80)
    print("TESTE CONCLUÍDO")
    print("=" * 80)
