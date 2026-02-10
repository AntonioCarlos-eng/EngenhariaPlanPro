import ezdxf
import sys
import re

print("\n=== TESTE DE LEITURA DXF ===")

arquivo = input("Arraste o arquivo DXF aqui e aperte ENTER:\n").strip('"')

print(f"\n>> Abrindo: {arquivo}\n")

try:
    doc = ezdxf.readfile(arquivo)
    msp = doc.modelspace()
except Exception as e:
    print(f"ERRO AO ABRIR: {e}")
    sys.exit()

print("\n--- LISTANDO TODOS OS TEXTOS ---\n")

for e in msp:
    if e.dxftype() == "TEXT":
        print("TEXT:", e.dxf.text)

print("\n--- LISTANDO TODAS AS POLYLINES E COMPRIMENTOS ---\n")

for e in msp:
    if e.dxftype() == "LWPOLYLINE":
        try:
            print("LWPOLYLINE comprimento:", round(e.length(), 2))
        except:
            print("Erro ao medir polyline")

print("\n=== FIM ===")
input("\nPressione ENTER para sair...")
