# Debug para identificar por que N9 e N10 não foram lidos

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

# Encontrar região de P1
print("=== ANÁLISE DE REGIÃO P1 ===\n")
p1_tokens = [t for t in raw_tokens if t["x"] > 60 and "P1" in t["text"].upper()]
if p1_tokens:
    p1_y = p1_tokens[0]["y"]
    print(f"P1 encontrado em Y={p1_y:.2f}\n")
    
    # Encontrar P2 para delimitar região
    p2_tokens = [t for t in raw_tokens if t["x"] > 60 and "P2" in t["text"].upper()]
    p2_y = p2_tokens[0]["y"] if p2_tokens else -1e9
    print(f"P2 encontrado em Y={p2_y:.2f}\n")
    
    # Tokens na região P1 (entre P1 e P2)
    regiao_p1 = [t for t in raw_tokens if t["y"] < p1_y and t["y"] > p2_y and t["x"] > 65]
    
    print(f"Total de tokens na região P1: {len(regiao_p1)}\n")
    
    # Procurar especificamente por valores que podem ser N9 ou N10
    print("=== TOKENS POSSIVELMENTE RELACIONADOS A N9/N10 ===\n")
    candidatos = []
    for t in regiao_p1:
        txt = t["text"].replace(" ", "").replace(",", ".")
        # Procurar por números que podem ser POS (9 ou 10)
        if re.search(r'\b(9|10)\b', txt):
            candidatos.append(t)
            print(f"Y={t['y']:.2f}  X={t['x']:.2f}  => '{t['text']}'")
    
    print(f"\n{len(candidatos)} tokens candidatos encontrados\n")
    
    # Agrupar por Y próximo (tolerância 0.2)
    print("=== AGRUPAMENTO POR LINHA (Y próximo) ===\n")
    linhas = []
    for t in sorted(regiao_p1, key=lambda x: -x["y"]):
        placed = False
        for linha in linhas:
            if abs(t["y"] - linha["y"]) <= 0.2:
                linha["tokens"].append(t)
                placed = True
                break
        if not placed:
            linhas.append({"y": t["y"], "tokens": [t]})
    
    print(f"Total de linhas agrupadas: {len(linhas)}\n")
    
    # Mostrar linhas que contenham 9 ou 10 como POS
    for idx, linha in enumerate(linhas):
        tokens_linha = sorted(linha["tokens"], key=lambda x: x["x"])
        textos = [t["text"] for t in tokens_linha]
        
        # Verificar se há 9 ou 10 na linha
        tem_9_ou_10 = any(re.search(r'\b(9|10)\b', t["text"]) for t in tokens_linha)
        
        if tem_9_ou_10:
            print(f"Linha {idx+1} (Y={linha['y']:.2f}):")
            for t in tokens_linha:
                print(f"  X={t['x']:.2f}  => '{t['text']}'")
            print()
    
    # Verificar cabeçalhos
    print("=== CABEÇALHOS DETECTADOS ===\n")
    header_keywords = {"POS", "BIT", "BITOLA", "QUANT", "QTD", "QTDE", "COMP", "COMPRIMENTO"}
    headers = [t for t in raw_tokens if t["x"] > 65 and 
               any(kw in t["text"].upper().replace(" ", "") for kw in header_keywords)]
    
    for h in headers[:10]:
        print(f"Y={h['y']:.2f}  X={h['x']:.2f}  => '{h['text']}'")
