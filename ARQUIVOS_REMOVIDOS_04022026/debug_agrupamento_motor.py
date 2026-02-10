"""
DEBUG: Verificar se os dados do motor estão agrupados por viga
Teste direto com o arquivo que o user está usando
"""
import sys
import os
sys.path.insert(0, r'c:\EngenhariaPlanPro')

print("[1] Importando...")
from core.vigas_motor_v2 import processar_vigas

# Usar arquivo que tem múltiplas vigas
arquivo = r'c:\EngenhariaPlanPro\P1_COMPLETO.dxf'

if not os.path.exists(arquivo):
    print(f"Arquivo não existe: {arquivo}")
    # Tentar encontrar outro
    arquivos = [
        r'c:\EngenhariaPlanPro\core\v4\vig terreo f 1-R2 - Copia.DXF',
        r'c:\EngenhariaPlanPro\P1_DESENHO.dxf',
    ]
    for arq in arquivos:
        if os.path.exists(arq):
            arquivo = arq
            break
    else:
        print("Nenhum arquivo DXF encontrado!")
        exit(1)

print(f"[2] Processando: {arquivo}")
print("    (Pode levar tempo...)")

dados, total_kg, total_barras = processar_vigas([arquivo])

print(f"\n[OK] Processado: {len(dados)} registros")

# Verificar agrupamento
print("\n" + "="*80)
print("VERIFICAR AGRUPAMENTO POR VIGA")
print("="*80)

vigas_ranges = {}
for i, (viga, pos, bitola, qtde, comp, peso) in enumerate(dados):
    if viga not in vigas_ranges:
        vigas_ranges[viga] = {'inicio': i, 'fim': i, 'qtd': 0}
    else:
        vigas_ranges[viga]['fim'] = i
    vigas_ranges[viga]['qtd'] += 1

print("\nOrdenação por viga:")
for viga in sorted(vigas_ranges.keys()):
    info = vigas_ranges[viga]
    inicio = info['inicio']
    fim = info['fim']
    qtd = info['qtd']
    contiguos = (fim - inicio + 1 == qtd)
    status = "✓ CONTÍGUO" if contiguos else "✗ DISPERSO"
    
    print(f"  {viga:10}: índices {inicio:3d}-{fim:3d} ({qtd:2d} registros) {status}")

# Mostrar sequência
print("\n" + "="*80)
print("SEQUÊNCIA DE DADOS (Primeiros 20)")
print("="*80)

for i in range(min(20, len(dados))):
    viga, pos, bitola, qtde, comp, peso = dados[i]
    print(f"{i:3d}. {viga:10} {pos:4} Ø{bitola:6.1f}")

# Simular cálculo de OS número
print("\n" + "="*80)
print("SIMULAÇÃO DE NUMERAÇÃO OS")
print("="*80)

for i in range(min(20, len(dados))):
    viga = dados[i][0]
    
    # Contar antes
    antes = 0
    for j in range(i):
        if dados[j][0] == viga:
            antes += 1
    
    # Total
    total = sum(1 for d in dados if d[0] == viga)
    
    os_num = f"{antes + 1}-{total}"
    print(f"{i:3d}. {viga:10} → OS={os_num:6}")

if len(dados) > 20:
    print(f"\n... ({len(dados) - 20} mais registros)")
