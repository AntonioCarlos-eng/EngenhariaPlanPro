#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug para testar geração de etiquetas
"""

import sys
from pathlib import Path

# Simular dados de teste
dados_teste = [
    ("V1", "4", 12.5, 2, 2.80, 0.617),
    ("V1", "1", 10.0, 4, 3.50, 0.494),
    ("V2", "2", 8.0, 3, 4.00, 0.237),
]

# Verificar se as imagens podem ser geradas
try:
    from PIL import Image, ImageDraw, ImageFont
    print("✅ PIL está disponível")
except Exception as e:
    print(f"❌ PIL não disponível: {e}")
    sys.exit(1)

def _mm_to_px(mm, dpi):
    return int((mm / 25.4) * dpi)

def gerar_imagem_teste(dado, idx, total):
    """Testa geração básica de imagem."""
    if not dado or len(dado) < 5:
        print(f"❌ Erro: dado vazio ou incompleto na posição {idx}")
        return None
    
    try:
        dpi_x = dpi_y = 300
        label_w = _mm_to_px(100, dpi_x)
        label_h = _mm_to_px(150, dpi_y)
        img = Image.new("RGB", (label_w, label_h), "white")
        draw = ImageDraw.Draw(img)
        
        # Extrair dados
        viga = str(dado[0])
        pos = str(dado[1])
        bitola = float(dado[2])
        qtde = int(dado[3])
        comp = float(dado[4])
        peso = float(dado[5]) if len(dado) > 5 else 0.0
        
        print(f"✅ Gerando imagem {idx+1}: VIGA={viga} POS={pos} BITOLA={bitola} QTDE={qtde} COMP={comp}m PESO={peso}kg")
        
        # Desenhar algo básico
        draw.rectangle([0, 0, label_w-1, label_h-1], outline="black", width=2)
        draw.text((10, 50), f"VIGA: {viga}", fill="black")
        draw.text((10, 70), f"POS: {pos}", fill="black")
        draw.text((10, 90), f"BITOLA: {bitola}", fill="black")
        draw.text((10, 110), f"QTDE: {qtde}", fill="black")
        draw.text((10, 130), f"COMP: {comp}m", fill="black")
        
        return img
    except Exception as e:
        print(f"❌ Erro ao gerar imagem {idx+1}: {e}")
        import traceback
        traceback.print_exc()
        return None

# Testar geração
print("\n" + "="*60)
print("TESTE DE GERAÇÃO DE ETIQUETAS")
print("="*60 + "\n")

for idx, dado in enumerate(dados_teste):
    img = gerar_imagem_teste(dado, idx, len(dados_teste))
    if img:
        # Salvar temporária
        temp_file = f"test_etiqueta_{idx}.png"
        img.save(temp_file)
        print(f"   Salvo: {temp_file}\n")

print("✅ Teste concluído com sucesso!")
