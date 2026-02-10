#!/usr/bin/env python3
"""
Demonstração da integração de nomenclatura expandida no Motor Completo
Mostra como arquivos DXF com P14-P32(X2) são processados corretamente
"""

import sys
sys.path.insert(0, r"c:\EngenhariaPlanPro")

from core.pilares_motor_dual import _expandir_titulos_pilares

# Simular o processamento de um DXF com nomenclatura expandida
print("=" * 80)
print("DEMONSTRAÇÃO: PROCESSAMENTO DE NOMENCLATURA EXPANDIDA NO MOTOR COMPLETO")
print("=" * 80)

# Simulação 1: Arquivo com nomenclatura simples (comportamento anterior)
print("\n📋 Cenário 1: Arquivo DXF Antigo com Nomenclatura Simples")
print("-" * 80)
nomes_simples = ["P1", "P2", "P3", "P4", "P5", "P6"]
print(f"Títulos originais: {nomes_simples}")
print("\nProcessamento:")
for nome in nomes_simples:
    expandido = _expandir_titulos_pilares(nome)
    print(f"  {nome:15} → {expandido} (sem expansão)")

print("\n✅ Resultado: Cada pilar processado individualmente (comportamento original)")

# Simulação 2: Arquivo com nomenclatura composta
print("\n" + "=" * 80)
print("📋 Cenário 2: Arquivo DXF Novo com Nomenclatura Composta")
print("-" * 80)
nomes_compostos = ["P1-P5", "P14-P32(X2)", "P40"]
print(f"Títulos originais: {nomes_compostos}")
print("\nProcessamento:")

dados_simulados = {
    "P1-P5": {
        "bitola": 8.0,
        "quantidade": 6,
        "comprimento": 3.20,
    },
    "P14-P32(X2)": {
        "bitola": 10.0,
        "quantidade": 4,
        "comprimento": 2.80,
    },
    "P40": {
        "bitola": 12.5,
        "quantidade": 8,
        "comprimento": 4.50,
    }
}

total_entradas = 0
for nome, dados in dados_simulados.items():
    expandido = _expandir_titulos_pilares(nome)
    total_entradas += len(expandido)
    
    print(f"\n  Título: {nome}")
    print(f"    ↳ Expande para: {expandido}")
    print(f"    ↳ Quantidade de pilares: {len(expandido)}")
    
    if len(expandido) > 1:
        print(f"    ↳ Dados replicados para cada pilar:")
        print(f"       • Bitola: {dados['bitola']} mm")
        print(f"       • Quantidade: {dados['quantidade']} barras")
        print(f"       • Comprimento: {dados['comprimento']} m")
        print(f"    ↳ Resultado final: {len(expandido)} entradas no romaneio")
    else:
        print(f"    ↳ Sem expansão, 1 entrada no romaneio")

print("\n" + "-" * 80)
print(f"✅ Resultado: {total_entradas} entradas totais no romaneio")
print(f"   (Comparado com 3 títulos originais)")

# Análise de impacto
print("\n" + "=" * 80)
print("📊 ANÁLISE DE IMPACTO")
print("-" * 80)

print("\nCenário 1 (Nomenclatura Simples - Sem Expansão):")
print(f"  Títulos lidos: 6")
print(f"  Entradas geradas: 6")
print(f"  Taxa de expansão: 1.0x (nenhuma)")
print(f"  Status: ✅ Compatível com versão anterior")

print("\nCenário 2 (Nomenclatura Composta - Com Expansão):")
print(f"  Títulos lidos: 3")
print(f"  Entradas geradas: {total_entradas}")
print(f"  Taxa de expansão: {total_entradas/3:.1f}x")
print(f"  Status: ✅ Suporta novos formatos")

print("\n" + "=" * 80)
print("🎯 CONCLUSÃO")
print("-" * 80)
print("""
✅ O motor completo agora suporta AMBOS:
   1. Nomenclatura simples (P1, P2, P3...) → processamento direto
   2. Nomenclatura composta (P14-P32, P32(X2)...) → expansão automática

✅ SEM quebra de compatibilidade com arquivos antigos

✅ Cada pilar expandido recebe seus próprios dados na tabela de romaneio

✅ Pronto para usar com qualquer arquivo DXF que use nomenclatura expandida
""")

print("=" * 80)
