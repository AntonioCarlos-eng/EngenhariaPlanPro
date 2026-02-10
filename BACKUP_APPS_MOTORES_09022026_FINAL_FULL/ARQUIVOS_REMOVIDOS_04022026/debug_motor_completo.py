import ezdxf
from ezdxf.recover import readfile as recover_readfile
import re

arquivo = r"c:\Users\orqui\OneDrive\Área de Trabalho\projetos\pilares\####pilares l1-018 - Copia.DXF"

doc, auditor = recover_readfile(arquivo)

# Coletar todos os textos x > 100
raw_tokens = []

for entity in doc.entities:
    if entity.dxftype() in ['TEXT', 'MTEXT']:
        try:
            if entity.dxftype() == 'MTEXT':
                texto = entity.plain_text()
            else:
                texto = entity.dxf.text
            
            x = entity.dxf.insert.x if hasattr(entity.dxf, 'insert') else 0
            y = entity.dxf.insert.y if hasattr(entity.dxf, 'insert') else 0
            
            if x > 100:
                raw_tokens.append({"text": texto.strip(), "x": x, "y": y})
        except:
            pass

# Detectar títulos P1, P2, etc
RE_PILAR = re.compile(r'^P\d+$', re.IGNORECASE)
table_titles = [t for t in raw_tokens if RE_PILAR.match(t["text"])]
table_titles.sort(key=lambda t: -t["y"])

print(f"TÍTULOS ENCONTRADOS: {len(table_titles)}")
for t in table_titles:
    print(f"  {t['text']} em Y={t['y']:.1f}")

# Para cada pilar, mostrar TODAS as linhas
print(f"\n{'='*80}")
print("ANÁLISE DETALHADA POR PILAR")
print('='*80)

for idx, title in enumerate(table_titles):
    y_top = title["y"]
    y_bottom = table_titles[idx+1]["y"] if idx+1 < len(table_titles) else -1e9
    
    print(f"\n{'='*80}")
    print(f">>> {title['text']} (Y_TOP={y_top:.1f}, Y_BOTTOM={y_bottom:.1f})")
    print('='*80)
    
    # Textos neste bloco
    bloco = [t for t in raw_tokens if y_bottom < t["y"] < y_top]
    bloco.sort(key=lambda t: -t["y"])
    
    print(f"Total de textos: {len(bloco)}")
    
    # Agrupar por linha (Y próximo ± 0.2)
    linhas = []
    current = []
    current_y = None
    
    for t in bloco:
        if current_y is None or abs(t["y"] - current_y) <= 0.2:
            current.append(t)
            current_y = t["y"]
        else:
            if current:
                linhas.append(current)
            current = [t]
            current_y = t["y"]
    
    if current:
        linhas.append(current)
    
    print(f"Total de linhas agrupadas: {len(linhas)}\n")
    
    # Mostrar cada linha
    for i, linha in enumerate(linhas):
        linha_sorted = sorted(linha, key=lambda t: t["x"])
        y_medio = sum(t["y"] for t in linha) / len(linha)
        
        # Extrair apenas números
        numeros = []
        for item in linha_sorted:
            txt = item["text"].replace(" ", "").replace(",", ".")
            
            # Procurar números
            matches = re.findall(r'\d+\.?\d*', txt)
            for m in matches:
                try:
                    val = float(m)
                    numeros.append(f"{val}@X{item['x']:.0f}")
                except:
                    pass
        
        if numeros:
            print(f"Linha {i+1:2d} (Y={y_medio:5.1f}): {' | '.join(numeros)}")
