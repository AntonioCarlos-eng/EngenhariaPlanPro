"""
Debug: Verificar numeração OS
Testar se os dados vêm agrupados por viga do motor
"""
import sys
import os
sys.path.insert(0, r'c:\EngenhariaPlanPro')

from core.vigas_motor_v2 import processar_vigas
from core.etiquetas_generator import GeradorEtiquetasDinamico

# Tentar processar um arquivo
arquivos_teste = [
    r'c:\EngenhariaPlanPro\P1_COMPLETO.dxf',
    r'c:\EngenhariaPlanPro\P1_DESENHO.dxf',
]

# Verificar qual arquivo existe
arquivo_valido = None
for arq in arquivos_teste:
    if os.path.exists(arq):
        arquivo_valido = arq
        break

if not arquivo_valido:
    print("[ERRO] Nenhum arquivo DXF encontrado para teste")
    exit(1)

print(f"[INFO] Usando arquivo: {arquivo_valido}")
print("\n" + "="*80)
print("DEBUG: NUMERAÇÃO OS - VERIFICANDO AGRUPAMENTO POR VIGA")
print("="*80 + "\n")

# 1. Processar DXF
dados, total_kg, total_barras = processar_vigas([arquivo_valido])

print(f"[MOTOR] Retornou {len(dados)} registros")
print(f"[MOTOR] Total: {total_barras} barras, {total_kg:.2f} kg\n")

# 2. Verificar agrupamento
print("DADOS BRUTOS DO MOTOR:")
print("-" * 80)
for i, (viga, pos, bitola, qtde, comp, peso) in enumerate(dados):
    print(f"{i+1:3d}. {viga:6} {pos:4} Ø{bitola:6.1f} qtd={qtde:2} comp={comp:6.2f}m peso={peso:7.2f}kg")

print("\n" + "="*80)
print("VERIFICAR AGRUPAMENTO")
print("="*80 + "\n")

# 3. Contar por viga
vigas_encontradas = {}
for i, (viga, pos, bitola, qtde, comp, peso) in enumerate(dados):
    if viga not in vigas_encontradas:
        vigas_encontradas[viga] = []
    vigas_encontradas[viga].append(i)

for viga in sorted(vigas_encontradas.keys()):
    indices = vigas_encontradas[viga]
    print(f"VIGA {viga:6}: {len(indices):2} registros | Índices: {indices[0]:3d}..{indices[-1]:3d}")
    
    # Verificar se é contíguo
    contiguos = True
    for j in range(1, len(indices)):
        if indices[j] != indices[j-1] + 1:
            contiguos = False
            break
    
    status = "✓ CONTÍGUO" if contiguos else "✗ DISPERSO"
    print(f"         {status}\n")

print("\n" + "="*80)
print("TESTAR GERADOR COM LÓGICA DE NUMERAÇÃO OS")
print("="*80 + "\n")

# 4. Simular a lógica do gerador
print("SIMULANDO formatar_os_numero(idx) do gerador:\n")

for idx in range(len(dados)):
    viga = dados[idx][0]
    
    # Contar quantas vigas iguais existem ANTES deste índice
    viga_index = 0
    for i in range(idx):
        if dados[i][0] == viga:
            viga_index += 1
    
    # Contar total de vigas iguais
    viga_total = sum(1 for d in dados if d[0] == viga)
    
    os_num = f"{viga_index + 1}-{viga_total}"
    
    print(f"Índice {idx+1:3d}: {viga:6} → OS={os_num:6}  [antes={viga_index}, total={viga_total}]")

print("\n" + "="*80)
print("TESTE COM GERADOR REAL")
print("="*80 + "\n")

try:
    # Criar gerador
    gerador = GeradorEtiquetasDinamico(
        arquivos_dxf=[arquivo_valido],
        obra="TESTE DEBUG",
        pavimento="TESTE"
    )
    
    print(f"[OK] Gerador criado com {len(gerador.dados)} registros\n")
    
    # Verificar alguns índices
    indices_para_testar = [0, 5, 10, 15, -1]  # Primeiros, meio, último
    
    for idx in indices_para_testar:
        if idx < 0:
            if abs(idx) > len(gerador.dados):
                continue
            idx_real = len(gerador.dados) + idx
        else:
            idx_real = idx
        
        if idx_real >= len(gerador.dados) or idx_real < 0:
            continue
        
        dados_etiq = gerador.gerar_dados_etiqueta(idx_real)
        if dados_etiq:
            print(f"[{idx_real+1:3d}] {dados_etiq['viga']:6} {dados_etiq['pos']:4} "
                  f"Ø{dados_etiq['bitola']:6.1f} → OS={dados_etiq['os_num']:6}")

except Exception as e:
    print(f"[ERRO] {e}")
    import traceback
    traceback.print_exc()
