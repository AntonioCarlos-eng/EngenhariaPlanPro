"""
DEBUG PROFUNDO - Verificar se PNG tem conteúdo
"""
import os
import sys
sys.path.insert(0, r'c:\EngenhariaPlanPro')

print("=" * 80)
print("DEBUG: VERIFICAR CONTEÚDO DE PNG")
print("=" * 80)

# 1. Preparar
dxf_dir = r'c:\EngenhariaPlanPro\dxf'
dxf_files = [f for f in os.listdir(dxf_dir) if f.lower().endswith('.dxf')][:1]
arquivo_teste = os.path.join(dxf_dir, dxf_files[0])

# 2. Criar gerador
from core.etiquetas_generator import GeradorEtiquetasDinamico
gerador = GeradorEtiquetasDinamico([arquivo_teste])
gerador.dados = gerador.dados[:1]  # Apenas 1 etiqueta

# 3. Gerar PNG usando método direto
print("\n[1] Gerando PNG com gerar_e_salvar_etiquetas_png...")
try:
    import tempfile
    temp_dir = tempfile.mkdtemp()
    gerador.pasta_etiquetas = temp_dir
    
    caminhos = gerador.gerar_e_salvar_etiquetas_png(dpi_x=300, dpi_y=300)
    
    if caminhos:
        caminho_png = caminhos[0]
        print(f"✅ PNG gerado: {caminho_png}")
        
        # Verificar tamanho
        tamanho = os.path.getsize(caminho_png)
        print(f"   Tamanho: {tamanho} bytes")
        
        # Verificar com PIL
        from PIL import Image
        img = Image.open(caminho_png)
        print(f"   Dimensões: {img.size}")
        print(f"   Modo: {img.mode}")
        
        # Verificar cores (se tem algo além de branco)
        pixels = list(img.getdata())
        branco_count = sum(1 for p in pixels if p == (255, 255, 255) or p == (255, 255, 255, 255))
        total_pixels = len(pixels)
        percentual_branco = (branco_count / total_pixels * 100) if total_pixels > 0 else 0
        
        print(f"   Pixels brancos: {branco_count}/{total_pixels} ({percentual_branco:.1f}%)")
        
        if percentual_branco > 95:
            print(f"   ⚠️ IMAGEM QUASE TODA BRANCA!")
        else:
            print(f"   ✅ Imagem tem conteúdo")
    else:
        print("❌ Nenhum PNG gerado!")
        
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
