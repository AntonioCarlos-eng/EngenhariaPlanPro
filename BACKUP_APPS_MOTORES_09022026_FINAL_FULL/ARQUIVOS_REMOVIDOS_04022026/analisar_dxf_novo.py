#!/usr/bin/env python3
"""
Análise do arquivo DXF para entender nomenclatura de pilares
Identifica padrões não reconhecidos
"""

import sys
sys.path.insert(0, r"c:\EngenhariaPlanPro")

try:
    import ezdxf
except ImportError:
    print("ezdxf não disponível")
    sys.exit(1)

# Carregar arquivo
arquivo = r"c:\EngenhariaPlanPro\pilares_l1-020.DXF"

print("=" * 80)
print("ANÁLISE DO ARQUIVO DXF")
print("=" * 80)
print(f"\nArquivo: {arquivo}\n")

try:
    doc = ezdxf.readfile(arquivo)
except Exception as e:
    print(f"❌ Erro ao ler arquivo: {e}")
    sys.exit(1)

msp = doc.modelspace()

# Extrair todos os textos
textos = []
for entity in msp.query('TEXT'):
    try:
        x = entity.dxf.insert[0]
        y = entity.dxf.insert[1]
        texto = entity.dxf.text.strip()
        if texto:
            textos.append({"x": x, "y": y, "text": texto})
    except:
        pass

for entity in msp.query('MTEXT'):
    try:
        x = entity.dxf.insert[0]
        y = entity.dxf.insert[1]
        texto = entity.text.strip()
        if texto:
            textos.append({"x": x, "y": y, "text": texto})
    except:
        pass

print(f"Total de textos encontrados: {len(textos)}\n")

# Procurar por nomenclaturas de pilares (P seguido de número)
import re

pilares_encontrados = set()
nomenclaturas_compostas = set()

for t in textos:
    # Procurar P seguido de número(s)
    matches = re.findall(r'P\d+', t["text"], re.IGNORECASE)
    for m in matches:
        pilares_encontrados.add(m.upper())
    
    # Procurar nomenclaturas compostas
    compostas = re.findall(r'P\d+[-;/]P\d+|P\d+\([X\d]+\)', t["text"], re.IGNORECASE)
    for c in compostas:
        nomenclaturas_compostas.add(c.upper())

print("PILARES ENCONTRADOS:")
print("-" * 80)

pilares_sorted = sorted(list(pilares_encontrados), key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0)
for p in pilares_sorted:
    print(f"  {p}")

print(f"\nTotal de pilares únicos: {len(pilares_sorted)}")

if nomenclaturas_compostas:
    print("\n" + "=" * 80)
    print("NOMENCLATURAS COMPOSTAS ENCONTRADAS:")
    print("-" * 80)
    for nc in nomenclaturas_compostas:
        print(f"  {nc}")
else:
    print("\n⚠️  Nenhuma nomenclatura composta encontrada")

print("\n" + "=" * 80)
print("ANÁLISE DETALHADA DE TEXTOS:")
print("-" * 80)

# Procurar textos que contenham P seguido de números
p_textos = [t for t in textos if re.search(r'P\d+', t["text"], re.IGNORECASE)]

if p_textos:
    for t in sorted(p_textos, key=lambda x: -x["y"])[:30]:  # Top 30
        print(f"X={t['x']:7.1f}  Y={t['y']:7.1f}  Texto: {t['text']}")
else:
    print("Nenhum texto com P encontrado")

print("\n" + "=" * 80)
