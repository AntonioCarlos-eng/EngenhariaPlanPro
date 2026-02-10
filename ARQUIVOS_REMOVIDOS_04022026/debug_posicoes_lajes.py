# Script para debugar todas as posições encontradas no DXF
import ezdxf
from ezdxf.recover import readfile as recover_readfile
import re
import os

arquivo = r"c:\EngenhariaPlanPro\temp_dxf\laje tipo pos-092.DXF"

print(f"Analisando: {os.path.basename(arquivo)}")
print("=" * 80)

doc, auditor = recover_readfile(arquivo)

# Extrai TODOS os textos
todos_textos = []
for entity in doc.entities:
    if not entity.is_alive:
        continue
    
    txt = ""
    x, y = 0, 0
    
    try:
        if entity.dxftype() == 'TEXT':
            txt = entity.dxf.text
            x = entity.dxf.insert[0]
            y = entity.dxf.insert[1]
        elif entity.dxftype() == 'MTEXT':
            txt = entity.plain_text()
            x = entity.dxf.insert[0]
            y = entity.dxf.insert[1]
    except:
        pass
    
    if txt and txt.strip():
        todos_textos.append((txt.strip(), x, y))

print(f"Total de textos: {len(todos_textos)}")
print()

# Procura por padrões de posições N
posicoes_encontradas = set()
RE_POS = re.compile(r'N\s*(\d+)', re.IGNORECASE)

for txt, x, y in todos_textos:
    match = RE_POS.search(txt.upper())
    if match:
        posicoes_encontradas.add(int(match.group(1)))

posicoes_ordenadas = sorted(list(posicoes_encontradas))
print(f"Posições N encontradas: {len(posicoes_ordenadas)}")
print(f"N: {', '.join([f'N{p}' for p in posicoes_ordenadas])}")
print()

# Agrupa por Y
textos_por_y = {}
for txt, x, y in todos_textos:
    y_round = round(y, 1)
    if y_round not in textos_por_y:
        textos_por_y[y_round] = []
    textos_por_y[y_round].append((txt, x))

# Mostra linhas que têm N + números
print("LINHAS COM POSSÍVEL TABELA:")
print("-" * 80)
cont = 0
for y in sorted(textos_por_y.keys(), reverse=True):
    linha = textos_por_y[y]
    linha_ordenada = sorted(linha, key=lambda t: t[1])
    textos_linha = [txt for txt, x in linha_ordenada]
    linha_str = " | ".join(textos_linha)
    
    # Verifica se tem N + número na linha
    if RE_POS.search(" ".join(textos_linha)):
        cont += 1
        print(f"{cont:3}. Y={y:7.1f}: {linha_str[:120]}")
        if cont >= 30:  # Mostra apenas as primeiras 30 linhas
            break

print()
print(f"Total de linhas com padrão N: {cont}+")
