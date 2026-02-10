# Debug para analisar duplicação de N

import ezdxf
from ezdxf.recover import readfile as recover_readfile
import re

arquivo = r"c:\EngenhariaPlanPro\ODA\in\#pilares l1-018 - Copia.DXF"

doc, auditor = recover_readfile(arquivo)

# Coletar todos os tokens com coordenadas
raw_tokens = []
for entity in doc.entities:
    if not entity.is_alive:
        continue
    txt = ""
    x, y = 0.0, 0.0
    
    try:
        if entity.dxftype() in ['TEXT', 'ATTRIB', 'ATTDEF']:
            txt = entity.dxf.text
            if hasattr(entity.dxf, 'insert'):
                x, y = entity.dxf.insert.x, entity.dxf.insert.y
        elif entity.dxftype() == 'MTEXT':
            txt = entity.plain_text()
            if hasattr(entity.dxf, 'insert'):
                x, y = entity.dxf.insert.x, entity.dxf.insert.y
    except:
        pass
    
    if txt:
        raw_tokens.append({"text": txt.strip(), "x": x, "y": y})

# Ordenar por Y decrescente
raw_tokens = sorted(raw_tokens, key=lambda t: -t["y"])

# Encontrar região de P2 (onde há duplicação)
print("=== ANÁLISE DE DUPLICAÇÃO - P2 ===\n")
p2_tokens = [t for t in raw_tokens if t["x"] > 60 and "P2" in t["text"].upper()]
if p2_tokens:
    p2_y = p2_tokens[0]["y"]
    print(f"P2 encontrado em Y={p2_y:.2f}\n")
    
    # Encontrar P3 para delimitar região
    p3_tokens = [t for t in raw_tokens if t["x"] > 60 and "P3" in t["text"].upper()]
    p3_y = p3_tokens[0]["y"] if p3_tokens else -1e9
    print(f"P3 encontrado em Y={p3_y:.2f}\n")
    
    # Tokens na região P2 (entre P2 e P3)
    regiao_p2 = [t for t in raw_tokens if t["y"] < p2_y and t["y"] > p3_y and t["x"] > 65]
    
    print(f"Total de tokens na região P2: {len(regiao_p2)}\n")
    
    # Agrupar por Y próximo (tolerância 0.2)
    print("=== LINHAS DA TABELA P2 ===\n")
    linhas = []
    for t in sorted(regiao_p2, key=lambda x: -x["y"]):
        placed = False
        for linha in linhas:
            if abs(t["y"] - linha["y"]) <= 0.2:
                linha["tokens"].append(t)
                placed = True
                break
        if not placed:
            linhas.append({"y": t["y"], "tokens": [t]})
    
    print(f"Total de linhas agrupadas: {len(linhas)}\n")
    
    # Mostrar todas as linhas de P2
    for idx, linha in enumerate(linhas):
        tokens_linha = sorted(linha["tokens"], key=lambda x: x["x"])
        print(f"Linha {idx+1} (Y={linha['y']:.2f}):")
        for t in tokens_linha:
            print(f"  X={t['x']:.2f}  => '{t['text']}'")
        print()
    
    # Procurar especificamente por padrões de POS e BIT
    print("\n=== ANÁLISE DE POS E BIT ===\n")
    pos_col_x = None
    bit_col_x = None
    
    # Encontrar cabeçalhos
    header_keywords = {"POS", "BIT", "BITOLA", "QUANT", "QTD", "QTDE", "COMP", "COMPRIMENTO"}
    headers = [t for t in raw_tokens if t["x"] > 65 and 
               any(kw in t["text"].upper().replace(" ", "") for kw in header_keywords) and
               t["y"] < p2_y and t["y"] > p3_y]
    
    for h in headers:
        print(f"Header: Y={h['y']:.2f}  X={h['x']:.2f}  => '{h['text']}'")
        if "POS" in h["text"].upper():
            pos_col_x = h["x"]
        if "BIT" in h["text"].upper():
            bit_col_x = h["x"]
    
    print(f"\nPOS coluna X aprox: {pos_col_x:.2f}")
    print(f"BIT coluna X aprox: {bit_col_x:.2f}\n")
    
    # Mostrar valores em cada linha para POS e BIT
    print("=== VALORES EXTRAÍDOS ===\n")
    for idx, linha in enumerate(linhas):
        tokens_linha = sorted(linha["tokens"], key=lambda x: x["x"])
        pos_val = None
        bit_val = None
        
        for t in tokens_linha:
            if pos_col_x and abs(t["x"] - pos_col_x) < 2:
                try:
                    pos_val = int(float(t["text"]))
                except:
                    pass
            if bit_col_x and abs(t["x"] - bit_col_x) < 2:
                try:
                    bit_val = float(t["text"])
                except:
                    pass
        
        if pos_val or bit_val:
            print(f"Linha {idx+1}: POS={pos_val}, BIT={bit_val}")
