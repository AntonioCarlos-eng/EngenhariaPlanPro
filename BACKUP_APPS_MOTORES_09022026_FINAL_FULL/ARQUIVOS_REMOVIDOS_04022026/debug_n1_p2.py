# Verificar exatamente quais linhas de N1 estão no DXF de P2

import ezdxf
from ezdxf.recover import readfile as recover_readfile

arquivo = r"c:\EngenhariaPlanPro\ODA\in\#pilares l1-018 - Copia.DXF"
doc, auditor = recover_readfile(arquivo)

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

raw_tokens = sorted(raw_tokens, key=lambda t: -t["y"])

# Encontrar P2 e P3
p2_tokens = [t for t in raw_tokens if t["x"] > 60 and "P2" in t["text"].upper()]
p3_tokens = [t for t in raw_tokens if t["x"] > 60 and "P3" in t["text"].upper()]

if p2_tokens and p3_tokens:
    p2_y = p2_tokens[0]["y"]
    p3_y = p3_tokens[0]["y"]
    
    print(f"P2 Y={p2_y:.2f}, P3 Y={p3_y:.2f}\n")
    
    # Tokens de P2 com X > 65
    regiao_p2 = [t for t in raw_tokens if t["y"] < p2_y and t["y"] > p3_y and t["x"] > 65]
    
    # Agrupar por linha
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
    
    print(f"Total linhas P2: {len(linhas)}\n")
    
    # Procurar por linhas de N1
    print("=== LINHAS DE N1 EM P2 ===\n")
    for idx, linha in enumerate(linhas):
        tokens = sorted(linha["tokens"], key=lambda x: x["x"])
        textos = " | ".join([f"{t['text']}@{t['x']:.1f}" for t in tokens])
        
        # Verificar se é linha de N1
        if any("1" in t["text"] and not t["text"].isspace() for t in tokens):
            print(f"Linha {idx+1} (Y={linha['y']:.2f}):")
            print(f"  {textos}")
            
            # Extrair valores de cada posição de coluna
            pos_vals = []
            for t in tokens:
                if 110 < t["x"] < 111:  # Coluna POS
                    pos_vals.append(f"POS={t['text']}")
                elif 111 < t["x"] < 112:  # Coluna BIT
                    pos_vals.append(f"BIT={t['text']}")
                elif 112 < t["x"] < 114:  # Coluna QUANT
                    pos_vals.append(f"QTD={t['text']}")
                elif 114 < t["x"] < 116:  # Coluna COMP
                    pos_vals.append(f"COMP={t['text']}")
            
            print(f"  => {', '.join(pos_vals)}")
            print()
