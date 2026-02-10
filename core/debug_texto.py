# debug_tokens.py
# Uso: python core\debug_tokens.py "C:\caminho\para\arquivo.dxf"
# Produz:
# - saída no terminal com todos os tokens importantes (índice, texto, x, y)
# - arquivo vigas_tokens_debug.csv com colunas: idx,text,x,y,type,flags
# Filtra e marca tokens que interessam (Nn, C=, C/, xNN, AxB, (NN), shapes, Viga labels).

import sys, csv, re, os
from pathlib import Path

if len(sys.argv) < 2:
    print('Uso: python core\\debug_tokens.py "C:\\caminho\\arquivo.dxf"')
    sys.exit(1)

dxf_path = sys.argv[1]
try:
    from core import vigas_motor_v2_simples as m
except Exception as e:
    print("ERRO ao importar core.vigas_motor_v2_simples:", e)
    import traceback; traceback.print_exc()
    sys.exit(1)

RE_POS = re.compile(r'\bN(\d{1,4})\b', re.IGNORECASE)
RE_C_EQ = re.compile(r'\bC\s*=\s*([0-9]{1,4}(?:[.,][0-9]+)?)\b', re.IGNORECASE)
RE_C_DIST = re.compile(r'\bC\s*[\/\\]\s*\d+\b', re.IGNORECASE)
RE_X_QTY = re.compile(r'[x×]\s*(\d{1,6})', re.IGNORECASE)
RE_AXB = re.compile(r'\b(\d{1,4})\s*[xX×]\s*(\d{1,4})\b')
RE_PAREN = re.compile(r'^\(\s*(\d{1,4})\s*\)$')
RE_SHAPE = re.compile(r'\b\d{1,3}\s*[xX×]\s*\d{1,3}\b')
RE_VIGA = re.compile(r'^(V[A-Za-z0-9]*\d+)', re.IGNORECASE)

out_csv = "vigas_tokens_debug.csv"

print(f"[DEBUG] extraindo tokens de: {dxf_path}")
tokens = m.extrair_textos_dxf(dxf_path)
print(f"[DEBUG] tokens extraídos: {len(tokens)}")

# annotate flags
rows = []
for i,t in enumerate(tokens):
    txt = t.get('text') or ''
    flags = []
    if RE_POS.search(txt): flags.append('POS')
    if RE_C_EQ.search(txt): flags.append('C_EQ')
    if RE_C_DIST.search(txt): flags.append('C_SLASH')
    if RE_X_QTY.search(txt): flags.append('X_QTY')
    if RE_AXB.search(txt): flags.append('AXB')
    if RE_PAREN.match(txt): flags.append('PAREN_SIMPLE')
    if RE_SHAPE.search(txt): flags.append('SHAPE')
    if RE_VIGA.match(txt): flags.append('VIGA')
    rows.append((i, txt, t.get('x'), t.get('y'), t.get('type'), ';'.join(flags)))

# write CSV
try:
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['idx','text','x','y','type','flags'])
        for r in rows:
            w.writerow(r)
    print(f"[DEBUG] arquivo gerado: {out_csv}")
except Exception as e:
    print("ERRO ao gravar CSV:", e)

# print subsections of interest (vigas V8 and VM1) and POS tokens nearby
def print_section(title, pred):
    print("\n" + "-"*80)
    print(title)
    print("-"*80)
    for i,(idx,txt,x,y,et,flags) in enumerate(rows):
        if pred(txt, flags):
            print(f"{idx:4d} | {txt!r:40s} | x={x!s:8s} y={y!s:8s} | type={et:6s} | flags={flags}")
    print("-"*80 + "\n")

# show tokens that are likely to be misinterpreted
print_section("TOKENS COM POS (Nn), C=, C/, xNN, AxB, PAREN, SHAPE, VIGA",
              lambda txt, flags: any(k in flags for k in ['POS','C_EQ','C_SLASH','X_QTY','AXB','PAREN_SIMPLE','SHAPE','VIGA']))

# show all tokens for quick manual inspection (first 200)
print("\n[DEBUG] Primeiros 200 tokens (índice | texto | x | y | flags):")
for idx,txt,x,y,et,flags in rows[:200]:
    print(f"{idx:4d} | {txt!r:40s} | {x!s:8s} | {y!s:8s} | {flags}")
print("\n[DEBUG] fim.")