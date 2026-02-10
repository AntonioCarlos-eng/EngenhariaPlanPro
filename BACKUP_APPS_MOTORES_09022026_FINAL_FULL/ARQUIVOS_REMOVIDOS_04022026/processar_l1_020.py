#!/usr/bin/env python3
"""
Processamento do arquivo pilares_l1-020.DXF com suporte ao padrão P14=P32
"""

import sys
sys.path.insert(0, r"c:\EngenhariaPlanPro")

from core.pilares_motor_dual import processar_pilares

print("=" * 80)
print("PROCESSANDO: pilares_l1-020.DXF COM PADRÃO P14=P32")
print("=" * 80)

arquivos = [r"c:\EngenhariaPlanPro\pilares_l1-020.DXF"]

resultado = processar_pilares(arquivos)

# Desempacotar resultado
dados_pilares, peso_total, qtd_total = resultado

print(f"\nTotal de linhas processadas: {len(dados_pilares)}")
print(f"Peso total: {peso_total:.2f} kg")
print(f"Quantidade total: {qtd_total} barras")

print("\n" + "=" * 80)
print("PILARES RECONHECIDOS E EXPANDIDOS")
print("=" * 80)

pilares_dict = {}
for pilar_nome, pos, bitola, qty, comp, peso, formato, medidas in dados_pilares:
    if pilar_nome not in pilares_dict:
        pilares_dict[pilar_nome] = []
    pilares_dict[pilar_nome].append({
        "pos": pos,
        "bitola": bitola,
        "qty": qty,
        "comp": comp,
        "peso": peso,
        "formato": formato,
        "medidas": medidas
    })

# Ordenar pilares
import re
pilares_sorted = sorted(pilares_dict.keys(), 
                       key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0)

for pilar in pilares_sorted:
    dados = pilares_dict[pilar]
    print(f"\n>>> {pilar}")
    print("-" * 60)
    for d in sorted(dados, key=lambda x: int(re.search(r'\d+', x['pos']).group())):
        print(f"    {d['pos']:5}  Ø{d['bitola']:5.1f}  Qtd: {d['qty']:5}  Comp: {d['comp']:6.2f}m  Peso: {d['peso']:7.2f}kg")

print("\n" + "=" * 80)
print(f"RESULTADO: {len(pilares_dict)} pilares processados")
print(f"           {len(dados_pilares)} linhas totais")
print(f"           {peso_total:.2f} kg")
print("=" * 80)

# Verificar P34
print("\nANÁLISE:")
if "P34" in pilares_dict:
    print("OK - P34 foi reconhecido!")
else:
    print("AVISO - P34 não aparece no resultado")
    print(f"   Pilares encontrados: {list(pilares_dict.keys())}")
