"""
Test PNG localization para etiquetas - v2 (Busca flexível)
Verifica se os PNGs estão sendo encontrados corretamente com padrão flexível
"""
import os
from pathlib import Path

pasta_etiq = r"c:\EngenhariaPlanPro\etiquetas"

# Dados de teste
test_cases = [
    {
        'viga': 'V10',
        'pos': 'N1',
        'bitola': 12.5,
        'qtde': 120,
        'comp_m': 8.0
    },
    {
        'viga': 'V8',
        'pos': 'N1',
        'bitola': 10.0,
        'qtde': 40,
        'comp_m': 10.0
    },
    {
        'viga': 'V301',
        'pos': 'N1',
        'bitola': 10.0,
        'qtde': 40,
        'comp_m': 10.0
    },
    {
        'viga': 'VM1',
        'pos': 'N1',
        'bitola': 12.5,
        'qtde': 118,
        'comp_m': 12.5
    }
]

print("=" * 80)
print("TESTE DE LOCALIZAÇÃO DE PNGs DE ETIQUETAS (v2 - Busca Flexível)")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    viga = test['viga']
    pos = test['pos']
    bitola = test['bitola']
    qtde = test['qtde']
    comp_m = test['comp_m']
    comp_cm = int(round(comp_m * 100))
    
    print(f"\n[Test {i}]")
    print(f"  Elemento: {viga}/{pos}, Bitola: {bitola}, Qtde: {qtde}, Comp: {comp_cm}cm")
    
    # Padrão flexível de busca
    target_pattern = f"_{viga}_{pos}_b{bitola:.1f}_q{qtde}_c{comp_cm}cm_"
    
    print(f"  Padrão: *{target_pattern}*.png")
    
    encontrados = []
    if os.path.exists(pasta_etiq):
        for arq in os.listdir(pasta_etiq):
            if arq.endswith('.png') and target_pattern in arq:
                encontrados.append(arq)
    
    if encontrados:
        print(f"  ✅ Encontrado: {len(encontrados)} arquivo(s)")
        for arq in encontrados[:3]:  # Mostrar apenas 3 primeiros
            print(f"     - {arq[:70]}...")
    else:
        print(f"  ❌ NÃO ENCONTRADO")
        # Mostrar arquivos similares para debug
        print(f"\n     Procurando por similaridade...")
        similar = []
        for arq in os.listdir(pasta_etiq):
            if viga in arq and pos in arq:
                similar.append(arq)
        
        if similar:
            print(f"     Encontrados {len(similar)} arquivos com {viga}/{pos}:")
            for arq in similar[:3]:
                print(f"     - {arq[:70]}...")
        else:
            print(f"     Nenhum arquivo com {viga}/{pos} encontrado")

print("\n" + "=" * 80)
print(f"Pasta testada: {pasta_etiq}")
print(f"Total de PNGs na pasta: {len([f for f in os.listdir(pasta_etiq) if f.endswith('.png')])}")
print("=" * 80)

