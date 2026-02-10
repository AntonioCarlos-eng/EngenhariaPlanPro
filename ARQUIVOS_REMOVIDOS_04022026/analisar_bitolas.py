#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analisar bitolas reais no arquivo DXF"""

import ezdxf
import os
from collections import Counter

# Procurar arquivo
search_paths = [
    r"c:\Users\orqui\OneDrive\Área de Trabalho\projetos\pilares\pilares l1-018 - Copia.DXF",
    r"c:\EngenhariaPlanPro\pilares l1-018 - Copia.DXF"
]

file_path = None
for p in search_paths:
    if os.path.exists(p):
        file_path = p
        print(f"[OK] Arquivo encontrado: {p}")
        break

if not file_path:
    print("[ERRO] Arquivo não encontrado em caminhos padrão")
    # Procurar em toda a pasta de projetos
    base = r"c:\Users\orqui\OneDrive\Área de Trabalho\projetos\pilares"
    if os.path.exists(base):
        for f in os.listdir(base):
            if f.endswith(".DXF"):
                file_path = os.path.join(base, f)
                print(f"[OK] Encontrado: {file_path}")
                break

if not file_path:
    print("Arquivo DXF não encontrado!")
    exit(1)

# Carregar DXF
try:
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    print("[OK] DXF carregado com sucesso")
except Exception as e:
    print(f"[ERRO] Ao carregar DXF: {e}")
    exit(1)

# Extrair todos os textos
all_texts = []
for entity in msp:
    if entity.dxftype() in ("TEXT", "MTEXT"):
        try:
            x = entity.dxf.insert.x if hasattr(entity.dxf.insert, "x") else entity.dxf.insert[0]
            y = entity.dxf.insert.y if hasattr(entity.dxf.insert, "y") else entity.dxf.insert[1]
            if entity.dxftype() == "TEXT":
                text = entity.dxf.text
            else:
                text = entity.text
            all_texts.append({"text": str(text).strip(), "x": x, "y": y})
        except:
            pass

print(f"[OK] Total de textos extraidos: {len(all_texts)}")

# Filtrar números na coluna BIT (X ~ 100-115)
print("\n" + "="*60)
print("ANALISE DE BITOLAS (X entre 100-115)")
print("="*60)

bit_candidates = []
for t in all_texts:
    try:
        val = float(t["text"])
        # Aceitar valores no range típico de bitolas (1-100mm)
        if 100 <= t["x"] <= 115 and 0 < val < 100:
            bit_candidates.append({"val": val, "x": t["x"], "y": t["y"], "text": t["text"]})
    except:
        pass

if bit_candidates:
    # Contar valores únicos
    unique_vals = Counter([round(b["val"], 1) for b in bit_candidates])
    print(f"\n[OK] Bitolas encontradas na tabela:")
    for val in sorted(unique_vals.keys()):
        count = unique_vals[val]
        print(f"  {val:6.1f} mm: {count:3d} ocorrencias")
    
    print(f"\nRESUMO:")
    print(f"  Bitolas unicas: {len(unique_vals)}")
    print(f"  Total de linhas com bitola: {len(bit_candidates)}")
    
    # Mostrar primeiras ocorrências
    print(f"\nPRIMEIRAS 10 OCORRENCIAS:")
    sorted_bits = sorted(bit_candidates, key=lambda x: (x["y"], x["x"]))
    for i, b in enumerate(sorted_bits[:10]):
        print(f"  {i+1}. {b['val']:6.1f} mm (X={b['x']:.1f}, Y={b['y']:.1f})")
else:
    print("\n[ERRO] Nenhuma bitola encontrada no range X=100-115")
    print("\nTentando analisar outros ranges...")
    
    # Mostrar distribuição de X
    print("\nDistribuicao de coordenadas X com numeros:")
    x_dist = Counter()
    for t in all_texts:
        try:
            float(t["text"])
            x_dist[round(t["x"], 0)] += 1
        except:
            pass
    
    print("Top 10 ranges de X com numeros:")
    for x, count in x_dist.most_common(10):
        print(f"  X aprox {x}: {count} valores")

print("\n[OK] Analise completa!")

