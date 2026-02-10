"""
Debug: Verificar numeração OS com arquivo real de múltiplas vigas
"""
import sys
import os
sys.path.insert(0, r'c:\EngenhariaPlanPro')

from core.vigas_motor_v2 import processar_vigas
from core.etiquetas_generator import GeradorEtiquetasDinamico

arquivo_teste = r'c:\EngenhariaPlanPro\core\v4\vig terreo f 1-R2 - Copia.DXF'

if not os.path.exists(arquivo_teste):
    print(f"[ERRO] Arquivo não encontrado: {arquivo_teste}")
    exit(1)

print(f"[INFO] Usando arquivo: {arquivo_teste}")
print("\n" + "="*80)
print("DEBUG: NUMERAÇÃO OS - ARQUIVO COM MÚLTIPLAS VIGAS")
print("="*80 + "\n")

# 1. Processar DXF
dados, total_kg, total_barras = processar_vigas([arquivo_teste])

print(f"[MOTOR] Retornou {len(dados)} registros")
print(f"[MOTOR] Total: {total_barras} barras, {total_kg:.2f} kg\n")

# 2. Verificar agrupamento
print("PRIMEIROS 30 REGISTROS DO MOTOR:")
print("-" * 80)
for i, (viga, pos, bitola, qtde, comp, peso) in enumerate(dados[:30]):
    print(f"{i+1:3d}. {viga:10} {pos:4} Ø{bitola:6.1f} qtd={qtde:2} comp={comp:6.2f}m peso={peso:7.2f}kg")

if len(dados) > 30:
    print(f"... ({len(dados) - 30} mais registros)")

print("\n" + "="*80)
print("VERIFICAR AGRUPAMENTO POR VIGA")
print("="*80 + "\n")

# 3. Contar por viga
vigas_encontradas = {}
for i, (viga, pos, bitola, qtde, comp, peso) in enumerate(dados):
    if viga not in vigas_encontradas:
        vigas_encontradas[viga] = []
    vigas_encontradas[viga].append(i)

for viga in sorted(vigas_encontradas.keys()):
    indices = vigas_encontradas[viga]
    print(f"VIGA {viga:10}: {len(indices):2} registros | Índices: {indices[0]:3d}..{indices[-1]:3d}")
    
    # Verificar se é contíguo
    contiguos = True
    for j in range(1, len(indices)):
        if indices[j] != indices[j-1] + 1:
            contiguos = False
            print(f"  ⚠️ FUROS: {indices}")
            break
    
    if contiguos:
        print(f"  ✓ Dados contíguos\n")
    else:
        print()

print("\n" + "="*80)
print("SIMULANDO NUMERAÇÃO OS DO GERADOR")
print("="*80 + "\n")

# 4. Simular a lógica do gerador para os primeiros 20
for idx in range(min(20, len(dados))):
    viga = dados[idx][0]
    
    # Contar quantas vigas iguais existem ANTES deste índice
    viga_index = 0
    for i in range(idx):
        if dados[i][0] == viga:
            viga_index += 1
    
    # Contar total de vigas iguais
    viga_total = sum(1 for d in dados if d[0] == viga)
    
    os_num = f"{viga_index + 1}-{viga_total}"
    
    print(f"Índice {idx+1:3d}: {viga:10} → OS={os_num:8}  [antes={viga_index:2d}, total={viga_total:2d}]")

print("\n" + "="*80)
print("TESTE COM GERADOR REAL")
print("="*80 + "\n")

try:
    # Criar gerador
    gerador = GeradorEtiquetasDinamico(
        arquivos_dxf=[arquivo_teste],
        obra="TESTE DEBUG",
        pavimento="TESTE"
    )
    
    print(f"[OK] Gerador criado com {len(gerador.dados)} registros\n")
    
    # Mostrar OS de alguns pontos chave
    print("PRIMEIRAS 10 ETIQUETAS:")
    print("-" * 80)
    for idx in range(min(10, len(gerador.dados))):
        dados_etiq = gerador.gerar_dados_etiqueta(idx)
        if dados_etiq:
            print(f"[{idx+1:3d}] {dados_etiq['viga']:10} {dados_etiq['pos']:4} "
                  f"Ø{dados_etiq['bitola']:6.1f} → OS={dados_etiq['os_num']:8}")

except Exception as e:
    print(f"[ERRO] {e}")
    import traceback
    traceback.print_exc()
