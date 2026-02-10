import sys
sys.path.insert(0, r'c:\EngenhariaPlanPro')

from core.vigas_motor_v2 import processar_vigas
from datetime import datetime

arquivo = r'c:\EngenhariaPlanPro\dxf\#vigas t1-069.DXF'
dados, total_kg, total_barras = processar_vigas([arquivo])

print("="*80)
print("                    ROMANEIO DE VIGAS - GERAL")
print("="*80)
print(f"Obra:      OBRA 001")
print(f"Pavimento: TÉRREO")
print(f"Data:      {datetime.now().strftime('%d/%m/%Y %H:%M')}")
print("="*80)
print()

viga_atual = None
for viga, pos, bit, qty, comp, peso in dados:
    if viga != viga_atual:
        if viga_atual is not None:
            print()
        print(f"\n>>> {viga}")
        print("-"*60)
        viga_atual = viga
    print(f"    {pos:6s} Ø{bit:5.1f}   Qtd: {qty:<4d} Comp: {comp:5.2f} m  Peso: {peso:8.2f} kg")

print()
print("="*80)
print(f"TOTAL GERAL: {total_kg:.2f} kg")
print("="*80)
