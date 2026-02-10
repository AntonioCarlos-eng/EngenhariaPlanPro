"""
Teste definitivo: Verificar agrupamento de dados em self.dados do gerador
"""
import sys
import os
sys.path.insert(0, r'c:\EngenhariaPlanPro')

from core.etiquetas_generator import GeradorEtiquetasDinamico

arquivo = r'c:\EngenhariaPlanPro\P1_COMPLETO.dxf'

if not os.path.exists(arquivo):
    print(f"Arquivo não encontrado: {arquivo}")
    exit(1)

print(f"[INFO] Testando agrupamento em: {arquivo}")
print()

# Criar gerador
gerador = GeradorEtiquetasDinamico(
    arquivos_dxf=[arquivo],
    obra="TEST",
    pavimento="TEST"
)

print(f"[OK] Gerador criado com {len(gerador.dados)} registros\n")

# Analisar agrupamento
if len(gerador.dados) > 0:
    print("PRIMEIROS 10 REGISTROS:")
    print("-"*80)
    for i in range(min(10, len(gerador.dados))):
        viga = gerador.dados[i][0]
        pos = gerador.dados[i][1]
        print(f"{i+1:3d}. {viga:10} {pos:4}")
    
    print("\n" + "="*80)
    print("ANÁLISE DE AGRUPAMENTO:")
    print("="*80)
    
    vigas_ranges = {}
    for i, (viga, pos, bitola, qtde, comp, peso) in enumerate(gerador.dados):
        if viga not in vigas_ranges:
            vigas_ranges[viga] = {'primeiro': i, 'ultimo': i}
        else:
            vigas_ranges[viga]['ultimo'] = i
    
    for viga in sorted(vigas_ranges.keys()):
        primeiro = vigas_ranges[viga]['primeiro']
        ultimo = vigas_ranges[viga]['ultimo']
        qtd = ultimo - primeiro + 1
        print(f"\n{viga:10}: índices {primeiro:3d} a {ultimo:3d} (total={qtd})")
        
        # Verificar se é contíguo
        contiguos = True
        atual_viga = None
        for j in range(primeiro, ultimo + 1):
            if gerador.dados[j][0] != viga:
                contiguos = False
                print(f"  ⚠️  ALERTA: Índice {j} tem viga '{gerador.dados[j][0]}' em vez de '{viga}'!")
                break
        
        if contiguos:
            print(f"  ✓ CONTÍGUO: Todos os {qtd} registros estão juntos")
        else:
            print(f"  ✗ DISPERSO: Registros estão misturados!")
    
    # Testar numeração OS
    print("\n" + "="*80)
    print("TESTE DE NUMERAÇÃO OS:")
    print("="*80)
    
    for i in range(min(15, len(gerador.dados))):
        dados_etiq = gerador.gerar_dados_etiqueta(i)
        print(f"{i+1:3d}. {dados_etiq['viga']:10} {dados_etiq['pos']:4} → OS={dados_etiq['os_num']:6}")
else:
    print("[ERRO] Nenhum dado carregado!")
