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

# Título V10
v10_title = None
for t in textos:
    if t["text"].upper().strip() == "V10":
        v10_title = t
        break

print("="*80)
print("BUSCA POR POSIÇÕES DA V10")
print("="*80)
print(f"\nTítulo V10: X={v10_title['x']:8.2f}, Y={v10_title['y']:8.2f}")

# Buscar por N2, N4, N5, N6, N7 relacionadas à V10
posicoes_procuradas = ["N2", "N4", "N5", "N6", "N7"]

for pos_nome in posicoes_procuradas:
    print(f"\n\nProcurando {pos_nome}:")
    print("-"*80)
    
    encontrados = [t for t in textos if pos_nome == t["text"].upper().strip()]
    
    if not encontrados:
        print(f"  NÃO ENCONTRADO")
        continue
    
    for t in encontrados:
        dx = abs(t["x"] - v10_title["x"])
        dy = abs(t["y"] - v10_title["y"])
        print(f"  X={t['x']:8.2f} Y={t['y']:8.2f}  dX={dx:7.2f} dY={dy:7.2f}")
        
        # Ver textos próximos a esta posição
        MAX_DX = 2.0
        MAX_DY = 1.5
        proximos = [
            tt for tt in textos 
            if abs(tt["x"] - t["x"]) <= 3.0  # Distância maior para busca
            and abs(tt["y"] - t["y"]) <= 2.0
            and tt["text"] != t["text"]
        ]
        
        print(f"    Textos próximos:")
        for tt in sorted(proximos, key=lambda x: (abs(x["y"] - t["y"]), abs(x["x"] - t["x"]))):
            ddx = tt["x"] - t["x"]
            ddy = tt["y"] - t["y"]
            print(f"      X={tt['x']:7.2f} Y={tt['y']:7.2f}  dX={ddx:+6.2f} dY={ddy:+6.2f}  '{tt['text']}'")
