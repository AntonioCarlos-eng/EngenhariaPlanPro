import ezdxf
import sys
from collections import Counter

# Arquivo que não lê nada
arquivo = r"C:\Users\orgu\OneDrive\Área de Trabalho\projetos\pilares\novos pilares.DWG"

output = []
output.append(f"Analisando: {arquivo}")
output.append("=" * 80)

doc = ezdxf.readfile(arquivo)
msp = doc.modelspace()

# Coletar todos os textos
textos = []
for entity in msp:
    if entity.dxftype() == 'TEXT':
        try:
            txt = entity.dxf.text.strip()
            x = entity.dxf.insert.x
            y = entity.dxf.insert.y
            textos.append((txt, x, y, 'TEXT'))
        except:
            pass
    elif entity.dxftype() == 'MTEXT':
        try:
            txt = entity.text.strip()
            x = entity.dxf.insert.x
            y = entity.dxf.insert.y
            textos.append((txt, x, y, 'MTEXT'))
        except:
            pass

output.append(f"\nTotal de textos encontrados: {len(textos)}")

# Buscar cabeçalhos de tabelas de pilares
cabecalhos = []
for txt, x, y, tipo in textos:
    txt_upper = txt.upper()
    if any(palavra in txt_upper for palavra in ['POS', 'BIT', 'QUANT', 'COMP', 'PILAR']):
        cabecalhos.append((txt, x, y, tipo))

output.append(f"\nPossíveis cabeçalhos encontrados: {len(cabecalhos)}")
output.append("\nPrimeiros 20 cabeçalhos:")
for i, (txt, x, y, tipo) in enumerate(sorted(cabecalhos, key=lambda t: t[2], reverse=True)[:20]):
    output.append(f"{i+1:2d}. X={x:8.2f} Y={y:8.2f} [{tipo:5s}] '{txt}'")

# Buscar palavras-chave específicas
print("\n" + "=" * 80)
print("Análise de cabeçalhos de colunas:")
print("=" * 80)

pos_textos = [t for t in textos if 'POS' in t[0].upper()]
bit_textos = [t for t in textos if 'BIT' in t[0].upper()]
quant_textos = [t for t in textos if 'QUANT' in t[0].upper() or 'QTD' in t[0].upper()]
comp_textos = [t for t in textos if 'COMP' in t[0].upper()]

print(f"\nTextos com 'POS': {len(pos_textos)}")
for txt, x, y, tipo in pos_textos[:5]:
    print(f"  X={x:8.2f} Y={y:8.2f} [{tipo:5s}] '{txt}'")

print(f"\nTextos com 'BIT': {len(bit_textos)}")
for txt, x, y, tipo in bit_textos[:5]:
    print(f"  X={x:8.2f} Y={y:8.2f} [{tipo:5s}] '{txt}'")

print(f"\nTextos com 'QUANT'/'QTD': {len(quant_textos)}")
for txt, x, y, tipo in quant_textos[:5]:
    print(f"  X={x:8.2f} Y={y:8.2f} [{tipo:5s}] '{txt}'")

print(f"\nTextos com 'COMP': {len(comp_textos)}")
for txt, x, y, tipo in comp_textos[:5]:
    print(f"  X={x:8.2f} Y={y:8.2f} [{tipo:5s}] '{txt}'")

# Análise de faixas X
print("\n" + "=" * 80)
print("Distribuição de coordenadas X dos textos:")
print("=" * 80)

from collections import Counter
x_coords = [round(x, 1) for _, x, _, _ in textos]
x_counter = Counter(x_coords)

print("\nCoordenadas X mais comuns (top 20):")
for x, count in x_counter.most_common(20):
    print(f"X={x:8.1f}: {count:4d} ocorrências")

# Buscar região de tabelas (x > 65 como no código original)
print("\n" + "=" * 80)
print("Textos na região X > 65 (região de tabelas):")
print("=" * 80)

textos_tabela = [t for t in textos if t[1] > 65.0]
print(f"\nTotal de textos com X > 65: {len(textos_tabela)}")

if textos_tabela:
    print("\nPrimeiros 30 textos nesta região:")
    for i, (txt, x, y, tipo) in enumerate(sorted(textos_tabela, key=lambda t: -t[2])[:30]):
        print(f"{i+1:3d}. X={x:8.2f} Y={y:8.2f} [{tipo:5s}] '{txt}'")

# Análise de valores numéricos na região de bitolas
print("\n" + "=" * 80)
print("Valores numéricos na faixa X=100-120 (região de bitola):")
print("=" * 80)

valores_bit = []
for txt, x, y, tipo in textos:
    if 100 <= x <= 120:
        try:
            val = float(txt.replace(',', '.'))
            valores_bit.append((val, x, y, tipo))
        except:
            pass

print(f"\nTotal de valores numéricos: {len(valores_bit)}")
if valores_bit:
    valores_unicos = Counter([v[0] for v in valores_bit])
    print("\nValores únicos encontrados:")
    for val, count in sorted(valores_unicos.items()):
        print(f"  {val:6.1f}: {count:3d} ocorrências")
