import sys
sys.path.insert(0, r'c:\EngenhariaPlanPro')

from core.vigas_motor_v2 import processar_vigas

arquivo = r'c:\EngenhariaPlanPro\core\v4\vig terreo f 1-R2 - Copia.DXF'
dados, total_kg, total_barras = processar_vigas([arquivo])

print("="*80)
print("AGRUPAMENTO POR VIGA")
print("="*80)

vigas = {}
for viga, pos, bit, qty, comp, peso in dados:
    if viga not in vigas:
        vigas[viga] = []
    vigas[viga].append((pos, bit, qty, comp, peso))

for viga_nome in sorted(vigas.keys()):
    print(f"\n>>> {viga_nome}")
    print(f"    Total de posições: {len(vigas[viga_nome])}")
    for pos, bit, qty, comp, peso in vigas[viga_nome]:
        print(f"    {pos:6s} Ø{bit:5.1f}   Qtd: {qty:2d}    Comp: {comp:5.2f} m  Peso: {peso:6.2f} kg")
