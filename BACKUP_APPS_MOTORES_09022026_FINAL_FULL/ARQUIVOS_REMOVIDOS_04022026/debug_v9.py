import sys, ezdxf
sys.path.insert(0, r'c:\EngenhariaPlanPro')

arquivo = r'c:\EngenhariaPlanPro\core\v4\vig terreo f 1-R2 - Copia.DXF'
doc = ezdxf.readfile(arquivo)
msp = doc.modelspace()

textos = []
for e in msp.query("TEXT MTEXT ATTRIB"):
    try:
        txt = e.dxf.text if e.dxftype() == 'TEXT' else e.plain_text()
    except:
        txt = getattr(e, "text", "")
    if txt:
        x, y = float(e.dxf.insert[0]), float(e.dxf.insert[1])
        textos.append({"text": txt.strip(), "x": x, "y": y})

# Título V9
v9_title = [t for t in textos if t["text"].upper().strip() == "V9"][0]

print("="*80)
print("ANÁLISE DA V9")
print("="*80)
print(f"\nTítulo V9: X={v9_title['x']:8.2f}, Y={v9_title['y']:8.2f}")

DX_WINDOW = 15.0
DY_WINDOW = 8.0

janela = [
    t for t in textos
    if abs(t["y"] - v9_title["y"]) <= DY_WINDOW
    and abs(t["x"] - v9_title["x"]) <= DX_WINDOW
]

print(f"\nTextos na janela da V9 ({len(janela)} textos):")
print("-"*80)

# Agrupar por linha
linhas = {}
for t in janela:
    y_key = round(t["y"], 1)
    if y_key not in linhas:
        linhas[y_key] = []
    linhas[y_key].append(t)

for y_key in sorted(linhas.keys(), reverse=True):
    print(f"\nY≈{y_key:.1f}:")
    for t in sorted(linhas[y_key], key=lambda x: x["x"]):
        print(f"  X={t['x']:7.2f}  '{t['text']}'")
