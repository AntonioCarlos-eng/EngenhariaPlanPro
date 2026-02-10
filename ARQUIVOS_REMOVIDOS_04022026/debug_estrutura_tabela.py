import ezdxf
from ezdxf.recover import readfile as recover_readfile
import re

arquivo = r"c:\Users\orqui\OneDrive\Área de Trabalho\projetos\pilares\###pilares l1-018 - Copia.DXF"

print(f"Análise completa dos títulos de pilares\n")

doc, auditor = recover_readfile(arquivo)

# Coletar títulos de pilares na região x > 65
titulos_pilares = []

for entity in doc.modelspace():
    if entity.dxftype() in ['TEXT', 'MTEXT']:
        try:
            if entity.dxftype() == 'MTEXT':
                texto = entity.plain_text()
            else:
                texto = entity.dxf.text
            
            x = entity.dxf.insert.x if hasattr(entity.dxf, 'insert') else 0
            y = entity.dxf.insert.y if hasattr(entity.dxf, 'insert') else 0
            
            # Buscar P1, P2, P3, etc na região da tabela
            if x > 65 and re.match(r'^P\d+$', texto.strip(), re.IGNORECASE):
                titulos_pilares.append({
                    'nome': texto.strip().upper(),
                    'x': x,
                    'y': y
                })
        except:
            pass

# Ordenar por Y decrescente
titulos_pilares.sort(key=lambda t: -t['y'])

print(f"Títulos de pilares encontrados: {len(titulos_pilares)}\n")

for i, titulo in enumerate(titulos_pilares):
    print(f"{i+1}. {titulo['nome']} em ({titulo['x']:.1f}, {titulo['y']:.1f})")

# Agora pegar todos os textos numéricos entre esses títulos
print(f"\n{'='*80}")
print("ANÁLISE DE DADOS POR PILAR")
print('='*80)

# Coletar TODOS os textos da tabela
todos_textos = []

for entity in doc.modelspace():
    if entity.dxftype() in ['TEXT', 'MTEXT']:
        try:
            if entity.dxftype() == 'MTEXT':
                texto = entity.plain_text()
            else:
                texto = entity.dxf.text
            
            x = entity.dxf.insert.x if hasattr(entity.dxf, 'insert') else 0
            y = entity.dxf.insert.y if hasattr(entity.dxf, 'insert') else 0
            
            if x > 65:
                todos_textos.append({
                    'texto': texto.strip(),
                    'x': x,
                    'y': y
                })
        except:
            pass

for i, titulo in enumerate(titulos_pilares):
    print(f"\n{'='*80}")
    print(f">>> {titulo['nome']} (Y={titulo['y']:.1f})")
    print('='*80)
    
    # Definir limites
    y_top = titulo['y']
    y_bottom = titulos_pilares[i+1]['y'] if i+1 < len(titulos_pilares) else -1e9
    
    # Textos nesta região
    textos_bloco = [t for t in todos_textos if y_bottom < t['y'] < y_top]
    textos_bloco.sort(key=lambda t: -t['y'])
    
    # Agrupar por linha (Y próximo)
    linhas = []
    linha_atual = []
    y_ant = None
    
    for t in textos_bloco:
        if y_ant is None or abs(t['y'] - y_ant) <= 0.5:
            linha_atual.append(t)
            y_ant = t['y']
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = [t]
            y_ant = t['y']
    
    if linha_atual:
        linhas.append(linha_atual)
    
    print(f"\nLinhas encontradas: {len(linhas)}")
    
    for j, linha in enumerate(linhas[:10]):  # Mostrar primeiras 10 linhas
        linha_sorted = sorted(linha, key=lambda t: t['x'])
        y_medio = sum(t['y'] for t in linha) / len(linha)
        
        # Extrair apenas valores numéricos principais
        valores = []
        for item in linha_sorted:
            txt = item['texto']
            
            # Procurar por padrões específicos
            if re.match(r'^N\d+$', txt, re.IGNORECASE):
                valores.append(f"[POS:{txt}]")
            elif re.match(r'^%%C\s*[\d.]+$', txt):
                bit = re.search(r'([\d.]+)', txt).group(1)
                valores.append(f"[BIT:{bit}]")
            elif re.match(r'^C=\d+$', txt):
                comp = re.search(r'(\d+)', txt).group(1)
                valores.append(f"[COMP:{comp}]")
            elif re.match(r'^\d+$', txt) and len(txt) <= 3:
                valores.append(f"[NUM:{txt}]")
        
        if valores:
            print(f"  Linha {j+1} (Y={y_medio:.1f}): {' '.join(valores)}")
