import os
from core.vigas_motor_v2_simples import extrair_textos_dxf

ARQ = r"####ES-007-R2 - Copia.DXF"  # ajuste para o nome exato do DXF

if not os.path.exists(ARQ):
    print("Arquivo não encontrado:", ARQ)
    raise SystemExit(1)

tokens = extrair_textos_dxf(ARQ)
print("TOTAL TOKENS:", len(tokens))

for t in tokens:
    txt = t.get("text", "")
    up = txt.upper()
    # heurística mínima: tem N e tem C (comprimento)
    if ("N" in up) and ("C=" in up or "C:" in up):
        print("----")
        print("TEXTO:", repr(txt))
        print("LAYER:", t.get("layer"), "X:", t.get("x"), "Y:", t.get("y"))