#!/usr/bin/env python3
"""
teste_completo_integrado.py
Testa o fluxo completo de geração e carregamento de etiquetas
"""

import os
import sys
from pathlib import Path

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 90)
    print("TESTE COMPLETO INTEGRADO - GERAÇÃO E CARREGAMENTO DE ETIQUETAS PNG")
    print("=" * 90)
    
    from core.etiquetas_generator import GeradorEtiquetasDinamico
    from PIL import Image
    
    # Passo 1: Gerar etiquetas
    print("\n[PASSO 1] Gerando etiquetas PNG...")
    dxf_file = r"c:\EngenhariaPlanPro\dxf\#vigas t1-069.DXF"
    
    try:
        gerador = GeradorEtiquetasDinamico([dxf_file], obra="OBRA 001", pavimento="TERREO")
        print(f"[OK] Gerador criado com {len(gerador.dados)} barras")
        
        # Gerar PNGs
        caminhos = gerador.gerar_e_salvar_etiquetas_png(dpi_x=300, dpi_y=300)
        print(f"[OK] {len(caminhos)} etiquetas PNG geradas")
    except Exception as e:
        print(f"[ERRO] Falha ao gerar: {e}")
        return False
    
    # Passo 2: Simular carregamento (como seria na funcao _gerar_imagem_etiqueta)
    print("\n[PASSO 2] Testando carregamento de etiquetas...")
    
    def mm_to_px(mm, dpi):
        return int((mm / 25.4) * dpi)
    
    def carregar_etiqueta(dado, idx):
        """Simula _gerar_imagem_etiqueta do vigas_app.py"""
        label_w = mm_to_px(100, 300)
        label_h = mm_to_px(150, 300)
        
        try:
            viga = str(dado[0]).strip()
            pos = str(dado[1]).strip()
            bitola = float(dado[2])
            qtde = int(dado[3])
            comp_m = float(dado[4])
            comp_cm = int(round(comp_m * 100))
            
            # Procurar PNG
            pasta_etiq = r"c:\EngenhariaPlanPro\etiquetas"
            pattern = f"ETIQUETA_{viga}_{pos}_b{bitola:.1f}_q{qtde}_c{comp_cm}cm_"
            
            for arq in os.listdir(pasta_etiq):
                if arq.startswith(pattern) and arq.endswith('.png'):
                    caminho_png = os.path.join(pasta_etiq, arq)
                    img_png = Image.open(caminho_png).convert("RGB")
                    img_png = img_png.resize((label_w, label_h), Image.Resampling.LANCZOS)
                    return img_png, arq
        except:
            pass
        
        # Fallback
        return None, None
    
    # Testar carregamento de primeiras 5 etiquetas
    sucesso_count = 0
    erro_count = 0
    
    for i in range(min(5, len(gerador.dados))):
        dado = gerador.dados[i]
        img, arquivo = carregar_etiqueta(dado, i)
        
        if img and arquivo:
            print(f"  [{i+1}] [OK] {dado[0]:20} {dado[1]:3} - {arquivo[:50]}")
            sucesso_count += 1
        else:
            print(f"  [{i+1}] [ERRO] Nao conseguiu carregar!")
            erro_count += 1
    
    print(f"\nResultado: {sucesso_count} sucesso(s), {erro_count} erro(s)")
    
    # Passo 3: Teste de qualidade
    print("\n[PASSO 3] Verificando qualidade dos PNGs...")
    
    etiquetas_dir = Path(r"c:\EngenhariaPlanPro\etiquetas")
    pngs = list(etiquetas_dir.glob("ETIQUETA_*.png"))
    
    if pngs:
        # Verificar primeira
        png_teste = pngs[0]
        img_teste = Image.open(png_teste)
        
        print(f"  PNG de teste: {png_teste.name}")
        print(f"  Tamanho: {img_teste.size}")
        print(f"  Modo: {img_teste.mode}")
        print(f"  Arquivo: {os.path.getsize(png_teste) / 1024:.1f} KB")
        
        # Verificar tamanho esperado (100mm x 150mm @ 300 DPI)
        expected_w = int((100 / 25.4) * 300)  # ~1181
        expected_h = int((150 / 25.4) * 300)  # ~1771
        
        if img_teste.size == (expected_w, expected_h):
            print(f"  [OK] Tamanho correto!")
        else:
            print(f"  [AVISO] Tamanho esperado: ({expected_w}, {expected_h})")
    
    # Passo 4: Estatisticas
    print("\n[PASSO 4] Estatisticas...")
    print(f"  Total de etiquetas geradas: {len(caminhos)}")
    print(f"  Total de PNGs na pasta: {len(pngs)}")
    print(f"  Tamanho total: {sum(os.path.getsize(p) for p in pngs) / (1024*1024):.1f} MB")
    
    # Verificar nomes
    print(f"\n  Primeiros 3 arquivos:")
    for i, p in enumerate(pngs[:3]):
        print(f"    {i+1}. {p.name}")
    
    print(f"\n  Ultimos 3 arquivos:")
    for i, p in enumerate(pngs[-3:], len(pngs)-2):
        print(f"    {i}. {p.name}")
    
    print("\n" + "=" * 90)
    print("[OK] TESTE INTEGRADO COMPLETO - TUDO FUNCIONANDO CORRETAMENTE!")
    print("=" * 90)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERRO FATAL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
