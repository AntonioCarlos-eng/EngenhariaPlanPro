import os
from core.vigas_motor_v2_simples import extrair_textos_dxf

# Ajuste o nome do DXF aqui:
ARQ = r"vigas cob-100.DXF"  # ou r"vig terreo f 1-R2 - Copia.DXF"

if not os.path.exists(ARQ):
    print("Arquivo não encontrado:", ARQ)
    raise SystemExit(1)

tokens = extrair_textos_dxf(ARQ)
print("TOTAL TOKENS:", len(tokens))

hits_nc = []
hits_n = []

for t in tokens:
    txt = t.get("text", "")
    up = txt.upper()
    if ("C=" in up or "C:" in up) and "N" in up:
        hits_nc.append(t)
    if "N" in up:
        hits_n.append(t)

def show(label, arr, limit=40):
    print(f"\n== {label} ({len(arr)}) ==")
    for h in arr[:limit]:
        print("TXT:", repr(h.get("text", "")), "LAYER:", h.get("layer"), "X:", h.get("x"), "Y:", h.get("y"))

show("N_and_C", hits_nc)
show("N_any", hits_n)