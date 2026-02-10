#!/usr/bin/env python3
"""
teste_fluxo_etiquetas.py
Testa o fluxo completo de geração de etiquetas PNG
"""

import os
import sys
import shutil
from pathlib import Path

# Adicionar o diretório principal ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.etiquetas_generator import GeradorEtiquetasDinamico
from core.vigas_motor_v2 import processar_vigas as motor_v2

def main():
    print("=" * 80)
    print("TESTE DO FLUXO COMPLETO DE ETIQUETAS PNG")
    print("=" * 80)
    
    # Localizar um arquivo DXF para teste
    dxf_dir = Path(__file__).parent / "dxf"
    dxf_file = dxf_dir / "#vigas t1-069.DXF"
    
    if not dxf_file.exists():
        print(f"[ERRO] Arquivo DXF não encontrado: {dxf_file}")
        return False
    
    print(f"\n[1] Arquivo DXF encontrado: {dxf_file.name}")
    
    # Diretório de saída para etiquetas
    etiquetas_dir = Path(__file__).parent / "etiquetas"
    print(f"\n[2] Diretório de etiquetas: {etiquetas_dir}")
    print(f"   - Existe: {'SIM' if etiquetas_dir.exists() else 'NAO'}")
    
    # Listar arquivos PNG existentes antes
    print(f"\n[3] PNG existentes ANTES:")
    if etiquetas_dir.exists():
        pngs_antes = list(etiquetas_dir.glob("ETIQUETA_*.png"))
        print(f"   - Total de ETIQUETA_*.png: {len(pngs_antes)}")
        if pngs_antes:
            for png in pngs_antes[:3]:
                print(f"     * {png.name}")
            if len(pngs_antes) > 3:
                print(f"     ... e mais {len(pngs_antes) - 3}")
    
    # Criar gerador
    print(f"\n[4] Criando GeradorEtiquetasDinamico...")
    try:
        gerador = GeradorEtiquetasDinamico(
            [str(dxf_file)],
            obra="OBRA 001",
            pavimento="TERREO"
        )
        print(f"   [OK] Gerador criado com sucesso")
        print(f"   - Total de barras: {len(gerador.dados)}")
        print(f"   - pasta_etiquetas: {gerador.pasta_etiquetas}")
    except Exception as e:
        print(f"   [ERRO] Erro ao criar gerador: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Mostrar primeira etiqueta
    if gerador.dados:
        print(f"\n[5] Primeiras 3 etiquetas:")
        for i in range(min(3, len(gerador.dados))):
            dados = gerador.gerar_dados_etiqueta(i)
            if dados:
                print(f"   [{i+1}] {dados['viga']:20} POS:{dados['pos']:3} | O{dados['bitola']:6.1f} | Q:{dados['qtde']:2} | C:{dados['comp']:6.3f}m")
    
    # Gerar PNGs
    print(f"\n[6] Gerando etiquetas PNG (DPI 300x300)...")
    try:
        caminhos = gerador.gerar_e_salvar_etiquetas_png(dpi_x=300, dpi_y=300)
        print(f"   [OK] {len(caminhos)} etiquetas PNG geradas!")
        if caminhos:
            print(f"   - Primeira: {Path(caminhos[0]).name}")
            print(f"   - Ultima: {Path(caminhos[-1]).name}")
    except Exception as e:
        print(f"   [ERRO] Erro ao gerar PNGs: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Verificar arquivo gerado
    print(f"\n[7] Verificando PNGs gerados:")
    if etiquetas_dir.exists():
        pngs_depois = list(etiquetas_dir.glob("ETIQUETA_*.png"))
        print(f"   - Total de ETIQUETA_*.png: {len(pngs_depois)}")
        if pngs_depois:
            # Verificar tamanho
            for png in pngs_depois[:1]:
                try:
                    from PIL import Image
                    img = Image.open(png)
                    print(f"   - Primeiro PNG: {png.name}")
                    print(f"     * Tamanho: {img.size} pixels")
                    print(f"     * Modo: {img.mode}")
                    print(f"     * Arquivo: {os.path.getsize(png) / 1024:.1f} KB")
                except Exception as e:
                    print(f"   [AVISO] Erro ao analisar PNG: {e}")
    
    # Teste de carregamento
    print(f"\n[8] Testando carregamento de PNG:")
    if etiquetas_dir.exists() and list(etiquetas_dir.glob("ETIQUETA_*.png")):
        try:
            from PIL import Image
            png_test = list(etiquetas_dir.glob("ETIQUETA_*.png"))[0]
            img = Image.open(png_test).convert("RGB")
            print(f"   [OK] PNG carregado com sucesso: {png_test.name}")
            print(f"   - Tamanho: {img.size}")
        except Exception as e:
            print(f"   [ERRO] Erro ao carregar PNG: {e}")
            return False
    
    print("\n" + "=" * 80)
    print("[OK] TESTE CONCLUIDO COM SUCESSO")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
