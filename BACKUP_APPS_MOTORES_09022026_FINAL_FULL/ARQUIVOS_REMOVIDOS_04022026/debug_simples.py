"""
Debug simples: Apenas contar registros do motor
"""
import sys
import os
sys.path.insert(0, r'c:\EngenhariaPlanPro')

print("[1] Importando motor...")
try:
    from core.vigas_motor_v2 import processar_vigas
    print("[OK] Motor importado")
except Exception as e:
    print(f"[ERRO] {e}")
    exit(1)

print("[2] Testando arquivo...")
arquivo = r'c:\EngenhariaPlanPro\core\v4\vig terreo f 1-R2 - Copia.DXF'
if not os.path.exists(arquivo):
    print(f"[ERRO] Arquivo não existe: {arquivo}")
    exit(1)
print(f"[OK] Arquivo encontrado")

print("[3] Processando DXF (pode levar tempo)...")
try:
    dados, total_kg, total_barras = processar_vigas([arquivo])
    print(f"[OK] Processamento concluído")
    print(f"  - Registros: {len(dados)}")
    print(f"  - Barras: {total_barras}")
    print(f"  - Peso: {total_kg:.2f} kg")
    
    if len(dados) > 0:
        print("\n[4] Primeiros 5 registros:")
        for i in range(min(5, len(dados))):
            viga, pos, bitola, qtde, comp, peso = dados[i]
            print(f"  {i+1}. {viga} {pos} Ø{bitola} qtd={qtde} comp={comp}m peso={peso}")
    
except Exception as e:
    print(f"[ERRO] {e}")
    import traceback
    traceback.print_exc()
