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

# Foco em V10 - deve ter: N1 Ø20 C=607 (qty=18), N2 Ø20 C=511 (qty=7), N3 Ø10 C=225 (qty=20), 
# N4 Ø12.5 C=410 (qty=12), N5 Ø8 C=401 (qty=44), N6 Ø8 C=94 (qty=26), N7 Ø8 C=304 (qty=26)

print("="*80)
print("ANÁLISE ESPECÍFICA DA V10")
print("="*80)

# Título V10
v10_title = None
for t in textos:
    if t["text"].upper().strip() == "V10":
        v10_title = t
        print(f"\nTítulo V10: X={t['x']:8.2f}, Y={t['y']:8.2f}")
        break

if v10_title:
    # Textos próximos à V10 (janela)
    DX_WINDOW = 15.0
    DY_WINDOW = 8.0
    
    janela = [
        t for t in textos
        if abs(t["y"] - v10_title["y"]) <= DY_WINDOW
        and abs(t["x"] - v10_title["x"]) <= DX_WINDOW
    ]
    
    print(f"\nTextos na janela da V10 ({len(janela)} textos):")
    print("-"*80)
    for t in sorted(janela, key=lambda x: (x["y"], x["x"])):
        dx = t["x"] - v10_title["x"]
        dy = t["y"] - v10_title["y"]
        print(f"  X={t['x']:8.2f} Y={t['y']:8.2f}  dX={dx:+7.2f} dY={dy:+7.2f}  => '{t['text']}'")
    
    # Agrupar por linha (mesma altura Y)
    print("\n\nAgrupamento por linha:")
    print("-"*80)
    linhas = {}
    for t in janela:
        y_key = round(t["y"], 1)  # Arredondar Y para agrupar
        if y_key not in linhas:
            linhas[y_key] = []
        linhas[y_key].append(t)
    
    for y_key in sorted(linhas.keys(), reverse=True):
        print(f"\nY≈{y_key:.1f}:")
        for t in sorted(linhas[y_key], key=lambda x: x["x"]):
            print(f"  X={t['x']:7.2f}  '{t['text']}'")
