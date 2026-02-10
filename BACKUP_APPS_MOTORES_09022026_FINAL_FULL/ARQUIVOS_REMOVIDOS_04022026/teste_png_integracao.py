"""
teste_png_integracao.py
Testa a integração de PNG técnico nas etiquetas
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.etiquetas_helper import localizar_desenho_barra

print("=" * 80)
print("TESTE DE INTEGRAÇÃO DE PNG TÉCNICO - FASE 3")
print("=" * 80)

# Pasta de etiquetas
pasta_etiquetas = r'c:\EngenhariaPlanPro\etiquetas'

# Verificar se pasta existe
if not os.path.exists(pasta_etiquetas):
    print(f"❌ Pasta não encontrada: {pasta_etiquetas}")
    sys.exit(1)

print(f"\n✅ Pasta encontrada: {pasta_etiquetas}")

# Listar alguns PNG disponíveis
pngs = [f for f in os.listdir(pasta_etiquetas) if f.endswith('.png')]
print(f"✅ Total de PNGs disponíveis: {len(pngs)}")

if pngs:
    print("\n📋 Primeiros 10 PNGs:")
    for i, png in enumerate(pngs[:10]):
        print(f"  {i+1}. {png}")

# Testes de busca
print("\n" + "=" * 80)
print("TESTES DE LOCALIZAÇÃO DE PNG:")
print("=" * 80)

testes = [
    {
        'arquivo_dxf': '#vigas t1-069',
        'viga': 'V301',
        'pos': 'N1',
        'bitola': 10.0,
        'qtde': 3,
        'comp': 255,  # cm
    },
    {
        'arquivo_dxf': '#vigas t1-069',
        'viga': 'V307',
        'pos': 'N1',
        'bitola': 6.3,
        'qtde': 8,
        'comp': 330,
    },
    {
        'arquivo_dxf': 'vigas cob-096',
        'viga': 'V501',
        'pos': 'N1',
        'bitola': 12.5,
        'qtde': 4,
        'comp': 522,
    },
]

encontrados = 0
nao_encontrados = 0

for i, teste in enumerate(testes, 1):
    print(f"\n[TESTE {i}]")
    print(f"  Arquivo: {teste['arquivo_dxf']}")
    print(f"  Viga: {teste['viga']:6} | Pos: {teste['pos']:3} | "
          f"Bitola: {teste['bitola']:5.1f} | Qtde: {teste['qtde']:2} | "
          f"Comp: {teste['comp']:3} cm")
    
    caminho = localizar_desenho_barra(
        pasta_etiquetas,
        teste['arquivo_dxf'],
        teste['viga'],
        teste['pos'],
        teste['bitola'],
        teste['qtde'],
        teste['comp']
    )
    
    if caminho:
        print(f"  ✅ PNG ENCONTRADO!")
        print(f"     {os.path.basename(caminho)}")
        encontrados += 1
    else:
        print(f"  ⚠️  PNG não encontrado")
        nao_encontrados += 1

print("\n" + "=" * 80)
print(f"RESULTADOS: {encontrados} encontrados | {nao_encontrados} não encontrados")
print("=" * 80)

if encontrados > 0:
    print("\n✅ INTEGRAÇÃO PRONTA!")
    print("   As etiquetas agora exibirão imagens técnicas PNG quando disponíveis.")
    print("\n🎯 Próximos passos:")
    print("   1. Abra vigas_app.py")
    print("   2. Selecione um DXF")
    print("   3. Clique em '🏷️ Etiquetas'")
    print("   4. Etiquetas com PNG aparecerão! 🖼️")
else:
    print("\n⚠️  Nenhum PNG encontrado!")
    print("   Certifique-se que a pasta etiquetas/ contém os PNGs")
    print(f"   Pasta: {pasta_etiquetas}")

print("\n" + "=" * 80)
