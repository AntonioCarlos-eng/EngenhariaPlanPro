import ezdxf
from ezdxf.recover import readfile as recover_readfile
import re

arquivo = r"c:\Users\orqui\OneDrive\Área de Trabalho\projetos\pilares\####pilares l1-018 - Copia.DXF"

doc, auditor = recover_readfile(arquivo)

BITOLAS_VALIDAS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0, 40.0]

def _eh_bitola_valida(valor):
    for b in BITOLAS_VALIDAS:
        if abs(valor - b) < 0.3:
            return True
    return False

# Coletar tokens
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

# Detectar títulos
RE_PILAR = re.compile(r'^P\d+$', re.IGNORECASE)
table_titles = [t for t in raw_tokens if RE_PILAR.match(t["text"])]
table_titles.sort(key=lambda t: -t["y"])

# Colunas conhecidas (do debug anterior)
col_x = {
    "POS": 110,
    "BIT": 111,
    "QUANT": 113,
    "COMP": 114
}
needed = ["POS", "BIT", "QUANT", "COMP"]

print(f"{'='*80}")
print("ANÁLISE DE VALIDAÇÃO - Por que linhas são rejeitadas?")
print('='*80)

for idx, title in enumerate(table_titles):
    y_top = title["y"]
    y_bottom = table_titles[idx+1]["y"] if idx+1 < len(table_titles) else -1e9
    
    print(f"\n{'='*80}")
    print(f">>> {title['text']}")
    print('='*80)
    
    bloco = [t for t in raw_tokens if y_bottom < t["y"] < y_top]
    bloco.sort(key=lambda t: -t["y"])
    
    # Agrupar por linha
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
    
    linha_num = 0
    for linha in linhas:
        linha_num += 1
        cols = {k: None for k in needed}
        
        # Coletar números ignorando X≈108
        numeros_linha = []
        
        for t in sorted(linha, key=lambda tt: tt["x"]):
            if 107 <= t["x"] <= 109:
                continue
            
            txt = t["text"].replace(" ", "").replace(",", ".")
            mnum = re.search(r'[\d\.]+', txt)
            if not mnum:
                continue
            
            try:
                val = float(mnum.group(0))
                numeros_linha.append({"x": t["x"], "val": val})
            except:
                continue
        
        # Mapear para colunas
        for num in numeros_linha:
            nearest_col = min(needed, key=lambda k: abs(num["x"] - col_x[k]))
            
            if cols[nearest_col] is None:
                val = num["val"]
                
                if nearest_col == "BIT":
                    if 40 <= val <= 700:
                        bit_norm = val / 10.0
                        cols[nearest_col] = bit_norm if _eh_bitola_valida(bit_norm) else val
                    else:
                        cols[nearest_col] = val if _eh_bitola_valida(val) else val
                else:
                    cols[nearest_col] = val
        
        # Verificar se tem todas as colunas
        if any(cols[k] is None for k in needed):
            print(f"  ❌ Linha {linha_num}: FALTAM COLUNAS - {cols}")
            continue
        
        # Tentar extrair valores
        try:
            pos = int(cols["POS"])
            bit = float(cols["BIT"])
            qty = int(cols["QUANT"])
            comp_cm = float(cols["COMP"])
        except Exception as e:
            print(f"  ❌ Linha {linha_num}: ERRO AO CONVERTER - {cols} - {e}")
            continue
        
        # Validações
        rejeicoes = []
        
        if not _eh_bitola_valida(bit):
            rejeicoes.append(f"bitola_invalida({bit})")
        
        if not (10 <= comp_cm <= 5000):
            rejeicoes.append(f"comprimento_fora({comp_cm})")
        
        if not (1 <= pos <= 100):
            rejeicoes.append(f"pos_invalida({pos})")
        
        if not (qty > 0 and qty <= 500):
            rejeicoes.append(f"qtd_invalida({qty})")
        
        if rejeicoes:
            print(f"  ❌ N{pos}: REJEITADA - {', '.join(rejeicoes)} - POS={pos} BIT={bit} QTY={qty} COMP={comp_cm}")
        else:
            print(f"  ✅ N{pos}: OK - BIT={bit} QTY={qty} COMP={comp_cm}")
