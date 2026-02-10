# Analisar P4 especificamente para entender a duplicação/mudança

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

# Encontrar P4
print("=== ANÁLISE P4 ===\n")
p4_tokens = [t for t in raw_tokens if t["x"] > 60 and "P4" in t["text"].upper()]
if p4_tokens:
    p4_y = p4_tokens[0]["y"]
    print(f"P4 em Y={p4_y:.2f}\n")
    
    # Encontrar P5
    p5_tokens = [t for t in raw_tokens if t["x"] > 60 and "P5" in t["text"].upper()]
    p5_y = p5_tokens[0]["y"] if p5_tokens else -1e9
    
    # Pegar blocos P4
    regiao_p4_65 = [t for t in raw_tokens if t["y"] < p4_y and t["y"] > p5_y and t["x"] > 65]
    regiao_p4_100 = [t for t in raw_tokens if t["y"] < p4_y and t["y"] > p5_y and t["x"] > 100]
    
    print(f"Tokens P4 com X>65: {len(regiao_p4_65)}")
    print(f"Tokens P4 com X>100: {len(regiao_p4_100)}\n")
    
    # Agrupar e mostrar
    def agrupar_linhas(tokens):
        linhas = []
        for t in sorted(tokens, key=lambda x: -x["y"]):
            placed = False
            for linha in linhas:
                if abs(t["y"] - linha["y"]) <= 0.2:
                    linha["tokens"].append(t)
                    placed = True
                    break
            if not placed:
                linhas.append({"y": t["y"], "tokens": [t]})
        return linhas
    
    linhas_65 = agrupar_linhas(regiao_p4_65)
    linhas_100 = agrupar_linhas(regiao_p4_100)
    
    print(f"Linhas P4 com X>65: {len(linhas_65)}")
    for idx, linha in enumerate(linhas_65):
        tokens = sorted(linha["tokens"], key=lambda x: x["x"])
        vals = [f"{t['text']}@{t['x']:.1f}" for t in tokens]
        print(f"  Linha {idx+1}: {' | '.join(vals)}")
    
    print(f"\nLinhas P4 com X>100: {len(linhas_100)}")
    for idx, linha in enumerate(linhas_100):
        tokens = sorted(linha["tokens"], key=lambda x: x["x"])
        vals = [f"{t['text']}@{t['x']:.1f}" for t in tokens]
        print(f"  Linha {idx+1}: {' | '.join(vals)}")
