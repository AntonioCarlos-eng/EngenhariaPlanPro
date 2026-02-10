"""
DEBUG SIMPLIFICADO - Testar gerar_e_imprimir_direto
"""
import os
import sys
sys.path.insert(0, r'c:\EngenhariaPlanPro')

print("=" * 80)
print("DEBUG: TESTE DO MÉTODO gerar_e_imprimir_direto")
print("=" * 80)

# 1. Preparar teste
print("\n[1] Preparando...")
dxf_dir = r'c:\EngenhariaPlanPro\dxf'
dxf_files = [f for f in os.listdir(dxf_dir) if f.lower().endswith('.dxf')][:1]
arquivo_teste = os.path.join(dxf_dir, dxf_files[0])
print(f"✅ Arquivo: {arquivo_teste}")

# 2. Criar gerador
print("\n[2] Criando gerador...")
from core.etiquetas_generator import GeradorEtiquetasDinamico
gerador = GeradorEtiquetasDinamico([arquivo_teste])
print(f"✅ Gerador com {len(gerador.dados)} etiqueta(s)")

# 3. Filtrar primeiras 2
print("\n[3] Filtrando 2 primeiras etiquetas...")
gerador.dados = gerador.dados[:2]
print(f"✅ Agora temos {len(gerador.dados)} etiqueta(s)")

# 4. Testar método
print("\n[4] Testando gerar_e_imprimir_direto...")
print("   (NÃO vai imprimir, só simular impressão)")
try:
    resultado = gerador.gerar_e_imprimir_direto(
        impressora="Argox OS-214 plus series PPLA",
        dpi_x=300,
        dpi_y=300
    )
    print(f"\n✅ Resultado: {resultado}")
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("FIM DO DEBUG")
print("=" * 80)
