import ezdxf
from ezdxf.recover import readfile as recover_readfile
import re

arquivo = r"c:\Users\orqui\OneDrive\Área de Trabalho\projetos\pilares\###pilares l1-018 - Copia.DXF"

print(f"Analisando tabela de pilares: {arquivo}\n")

doc, auditor = recover_readfile(arquivo)

# Coletar todos os textos com coordenadas x > 65 (região da tabela)
textos_tabela = []

for entity in doc.modelspace():
    if entity.dxftype() in ['TEXT', 'MTEXT']:
        try:
            if entity.dxftype() == 'MTEXT':
                texto = entity.plain_text()
            else:
                texto = entity.dxf.text
            
            x = entity.dxf.insert.x if hasattr(entity.dxf, 'insert') else 0
            y = entity.dxf.insert.y if hasattr(entity.dxf, 'insert') else 0
            
            if x > 65:  # Região da tabela
                textos_tabela.append({
                    'texto': texto.strip(),
                    'x': x,
                    'y': y,
                    'tipo': entity.dxftype()
                })
        except:
            pass

# Ordenar por Y (de cima para baixo)
textos_tabela.sort(key=lambda t: -t['y'])

print(f"Textos na região da tabela (x > 65): {len(textos_tabela)}\n")

# Agrupar por linha (Y próximo)
linhas = []
linha_atual = []
y_anterior = None

for item in textos_tabela:
    if y_anterior is None or abs(item['y'] - y_anterior) <= 0.5:
        linha_atual.append(item)
        y_anterior = item['y']
    else:
        if linha_atual:
            linhas.append(linha_atual)
        linha_atual = [item]
        y_anterior = item['y']

if linha_atual:
    linhas.append(linha_atual)

print(f"Total de linhas agrupadas: {len(linhas)}\n")

# Mostrar primeiras 30 linhas
for i, linha in enumerate(linhas[:30]):
    linha_sorted = sorted(linha, key=lambda t: t['x'])
    y_medio = sum(t['y'] for t in linha) / len(linha)
    
    print(f"\n--- Linha {i+1} (Y={y_medio:.1f}) ---")
    for item in linha_sorted:
        print(f"  X={item['x']:6.1f}  '{item['texto']}'")
