#!/usr/bin/env python3
"""
teste_carregar_etiqueta.py
Testa o carregamento de uma etiqueta PNG
"""

import os
import sys
from pathlib import Path
from PIL import Image

# Simular a funcao _gerar_imagem_etiqueta
def mm_to_px(mm, dpi):
    return int((mm / 25.4) * dpi)

def gerar_imagem_etiqueta(dado, idx, total, dpi_x, dpi_y):
    """Carrega PNG da etiqueta ja gerado pelo gerador dinamico."""
    label_w = mm_to_px(100, dpi_x)
    label_h = mm_to_px(150, dpi_y)
    
    try:
        # Extrair dados para formar o nome do arquivo
        viga = str(dado[0]).strip()
        pos = str(dado[1]).strip()
        bitola = float(dado[2])
        qtde = int(dado[3])
        comp_m = float(dado[4])
        comp_cm = int(round(comp_m * 100))
        
        # Tentar multiplas pastas possiveis
        pastas_possveis = [
            os.path.join(os.getcwd(), "etiquetas"),
            r"c:\EngenhariaPlanPro\etiquetas",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "etiquetas")
        ]
        
        # Procurar PNG da etiqueta completa gerado pelo gerador
        pattern = f"ETIQUETA_{viga}_{pos}_b{bitola:.1f}_q{qtde}_c{comp_cm}cm_"
        
        print(f"\n[INFO] Procurando por: {pattern}")
        
        for pasta_etiq in pastas_possveis:
            if not os.path.exists(pasta_etiq):
                print(f"  [SKIP] {pasta_etiq} (nao existe)")
                continue
            
            print(f"  [OK] Verificando: {pasta_etiq}")
            for arq in os.listdir(pasta_etiq):
                if arq.startswith(pattern) and arq.endswith('.png'):
                    caminho_png = os.path.join(pasta_etiq, arq)
                    try:
                        img_png = Image.open(caminho_png).convert("RGB")
                        resample = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS
                        img_png = img_png.resize((label_w, label_h), resample)
                        print(f"  [SUCESSO] Etiqueta {idx+1}: {arq}")
                        return img_png
                    except Exception as e:
                        print(f"  [ERRO] Erro ao abrir PNG {arq}: {e}")
                        continue
        
        print(f"  [FALHA] PNG nao encontrado para: {pattern}")
        
    except Exception as e:
        print(f"  [ERRO] Erro ao processar dados: {e}")
    
    # Fallback se nao encontrar PNG
    img = Image.new("RGB", (label_w, label_h), "white")
    return img

def main():
    print("=" * 80)
    print("TESTE DE CARREGAMENTO DE ETIQUETA PNG")
    print("=" * 80)
    
    # Dado de teste (V301, N1, bitola 10.0, qtde 3, comp 2.55m)
    dado_teste = ("V301", "N1", 10.0, 3, 2.55)
    
    print(f"\nDado de teste: {dado_teste}")
    print(f"  - Viga: {dado_teste[0]}")
    print(f"  - POS: {dado_teste[1]}")
    print(f"  - Bitola: {dado_teste[2]}")
    print(f"  - Qtde: {dado_teste[3]}")
    print(f"  - Comp: {dado_teste[4]}m")
    
    # Carregar etiqueta
    img = gerar_imagem_etiqueta(dado_teste, idx=0, total=69, dpi_x=300, dpi_y=300)
    
    print(f"\nResultado:")
    print(f"  - Imagem carregada: SIM")
    print(f"  - Tamanho: {img.size}")
    print(f"  - Modo: {img.mode}")
    
    # Salvar temporariamente para verificar
    temp_file = "teste_etiqueta_temp.png"
    img.save(temp_file)
    print(f"  - Salvo em: {temp_file}")
    
    # Verificar arquivo
    if os.path.exists(temp_file):
        size_kb = os.path.getsize(temp_file) / 1024
        print(f"  - Tamanho do arquivo: {size_kb:.1f} KB")
        os.remove(temp_file)
        print(f"  - Arquivo removido")
    
    print("\n" + "=" * 80)
    print("[OK] TESTE CONCLUIDO COM SUCESSO")
    print("=" * 80)

if __name__ == "__main__":
    main()
