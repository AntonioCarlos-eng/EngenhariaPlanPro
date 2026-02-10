#!/usr/bin/env python3
"""
Teste de integração - Etiquetas com código de barras
"""
from core.etiquetas_helper import (
    gerar_codigo_identificador,
    gerar_codigo_barras_imagem,
    formatar_os_numero
)

# Simular dados de vigas
dados_vigas = [
    ("V301", "N1", 10.0, 3, 2.55),
    ("V301", "N2", 10.0, 2, 4.35),
    ("V307=V311=V333=V336", "N1", 6.3, 8, 3.30),
    ("V309", "N1", 10.0, 3, 5.74),
]

print("=" * 70)
print("TESTE DE GERAÇÃO DE CÓDIGOS IDENTIFICADORES")
print("=" * 70)

obra = "SAGA 001"

for idx, (viga, pos, bitola, qtde, comp) in enumerate(dados_vigas):
    os_num = formatar_os_numero(idx, len(dados_vigas))
    
    codigo = gerar_codigo_identificador(
        obra=obra,
        os_num=os_num,
        elemento=viga,
        pos=pos,
        bitola=bitola,
        comp=comp
    )
    
    print(f"\n{idx+1}. {viga} / {pos}")
    print(f"   OS: {os_num}")
    print(f"   Código: {codigo}")
    
    # Tentar gerar imagem
    try:
        img = gerar_codigo_barras_imagem(codigo, largura_px=250, altura_px=60)
        print(f"   ✅ Código de barras gerado: {img.size[0]}x{img.size[1]} px")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print("\n" + "=" * 70)
print("✅ TESTE CONCLUÍDO!")
print("=" * 70)
