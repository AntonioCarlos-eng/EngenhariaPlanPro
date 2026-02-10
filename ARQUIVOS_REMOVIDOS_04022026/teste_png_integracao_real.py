"""
teste_png_integracao_real.py
Testa a integração de PNG técnico com dados REAIS disponíveis
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
    print("\n📋 Alguns PNGs disponíveis:")
    for i, png in enumerate(pngs[:5]):
        print(f"  1. {png[:70]}...")

# Detectar arquivo base dos PNGs
arquivo_base = None
if pngs:
    primeiro_png = pngs[0]
    # Extrair nome do arquivo DXF
    partes = primeiro_png.split('_')
    arquivo_base = partes[0]
    print(f"\n📄 Arquivo DXF base detectado: {arquivo_base}")

# Testes com arquivo base real
print("\n" + "=" * 80)
print("TESTES DE LOCALIZAÇÃO DE PNG (COM ARQUIVO BASE REAL):")
print("=" * 80)

if arquivo_base:
    testes = [
        {
            'arquivo_dxf': arquivo_base,
            'viga': 'V10',
            'pos': 'N1',
            'bitola': 12.5,
            'qtde': 120,
            'comp': 800,  # cm
        },
        {
            'arquivo_dxf': arquivo_base,
            'viga': 'V10',
            'pos': 'N1',
            'bitola': 12.5,
            'qtde': 240,
            'comp': 800,
        },
        {
            'arquivo_dxf': arquivo_base,
            'viga': 'V10',
            'pos': 'N1',
            'bitola': 20.0,
            'qtde': 10,
            'comp': 607,
        },
    ]

    encontrados = 0
    nao_encontrados = 0

    for i, teste in enumerate(testes, 1):
        print(f"\n[TESTE {i}]")
        print(f"  Arquivo: {teste['arquivo_dxf']}")
        print(f"  Viga: {teste['viga']:6} | Pos: {teste['pos']:3} | "
              f"Bitola: {teste['bitola']:5.1f} | Qtde: {teste['qtde']:3} | "
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
            # Tentar buscar com padrão mais flexível
            pattern_flexivel = f"{teste['arquivo_dxf']}_V{teste['viga'].replace('V','')}_N{teste['pos'].replace('N','')}_b{int(teste['bitola']*10)}"
            pngs_similares = [p for p in pngs if pattern_flexivel.replace('.0','').replace('.','') in p]
            if pngs_similares:
                print(f"     (Mas encontrados {len(pngs_similares)} similar(es))")
            nao_encontrados += 1

    print("\n" + "=" * 80)
    print(f"RESULTADOS: {encontrados} encontrados | {nao_encontrados} não encontrados")
    print("=" * 80)

    if encontrados > 0:
        print("\n✅ INTEGRAÇÃO FUNCIONANDO!")
        print("   As etiquetas exibirão imagens técnicas PNG quando encontradas.")
else:
    print("\n⚠️  Nenhum PNG encontrado na pasta etiquetas/")

print("\n" + "=" * 80)
print("INFORMAÇÕES IMPORTANTES:")
print("=" * 80)
print("""
📌 Padrão dos PNGs:
   {arquivo_dxf}_{viga}_{pos}_b{bitola}_q{qtde}_c{comp}cm_*.png

📌 Integração implementada:
   ✅ Função localizar_desenho_barra() já procura este padrão
   ✅ Integrada em vigas_app.py no método desenhar_pagina_etiquetas_vigas()
   ✅ Exibe placeholder cinza se PNG não encontrado
   ✅ Label verde "[DESENHO TÉCNICO]" quando encontrado

📌 Comportamento:
   • Se PNG encontrado → exibe na etiqueta (lado superior direito)
   • Se PNG não encontrado → exibe placeholder cinza
   • Se pasta não existe → mostra aviso, não quebra

🎯 Próximas fases:
   FASE 4: Layout 10x15cm com 3 picotes
   FASE 5: Exportar PDF
""")
print("=" * 80)
