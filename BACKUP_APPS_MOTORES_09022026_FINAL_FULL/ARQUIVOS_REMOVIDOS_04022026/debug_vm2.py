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

print("="*80)
print("ANÁLISE DAS VIGAS VM2")
print("="*80)

# Buscar todos os títulos VM2
vm2_titles = [t for t in textos if t["text"].upper().strip() == "VM2"]

print(f"\nEncontrados {len(vm2_titles)} títulos VM2:")
for i, t in enumerate(vm2_titles, 1):
    print(f"\n{i}. VM2 em X={t['x']:8.2f}, Y={t['y']:8.2f}")
    
    # Textos próximos
    DX_WINDOW = 15.0
    DY_WINDOW = 8.0
    janela = [
        tt for tt in textos
        if abs(tt["y"] - t["y"]) <= DY_WINDOW
        and abs(tt["x"] - t["x"]) <= DX_WINDOW
        and tt["text"] != "VM2"
    ]
    
    print(f"   Textos na janela ({len(janela)} itens):")
    for tt in sorted(janela, key=lambda x: (x["y"], x["x"]))[:15]:  # Mostrar primeiros 15
        dx = tt["x"] - t["x"]
        dy = tt["y"] - t["y"]
        print(f"     X={tt['x']:7.2f} Y={tt['y']:7.2f}  dX={dx:+6.2f} dY={dy:+6.2f}  '{tt['text']}'")
