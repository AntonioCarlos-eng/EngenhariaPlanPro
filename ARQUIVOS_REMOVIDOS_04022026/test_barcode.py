#!/usr/bin/env python3
"""
Teste de geração de código de barras para etiquetas
"""
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import io

def gerar_codigo_barras(texto: str, salvar_arquivo: bool = False):
    """
    Gera código de barras Code128 a partir de texto
    
    Args:
        texto: String para gerar código (ex: "SAGA.001-V301-N1")
        salvar_arquivo: Se True, salva PNG
    
    Returns:
        Image PIL ou caminho do arquivo
    """
    # Code128 aceita alfanuméricos
    code128 = barcode.get_barcode_class('code128')
    
    # Gerar código
    codigo = code128(texto, writer=ImageWriter())
    
    if salvar_arquivo:
        # Salvar arquivo
        filename = codigo.save(f'barcode_{texto.replace("/", "-").replace("=", "-")}')
        print(f"✅ Código de barras salvo: {filename}")
        return filename
    else:
        # Retornar como imagem PIL em memória
        buffer = io.BytesIO()
        codigo.write(buffer)
        buffer.seek(0)
        img = Image.open(buffer)
        return img

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE GERAÇÃO DE CÓDIGO DE BARRAS")
    print("=" * 60)
    
    # Teste 1: Formato etiqueta simples
    print("\n1. Gerando código para: SAGA001-V301-N1-O5")
    img1 = gerar_codigo_barras("SAGA001-V301-N1-05", salvar_arquivo=True)
    
    # Teste 2: Com viga equivalente
    print("\n2. Gerando código para: SAGA001-V307=V311-N3")
    img2 = gerar_codigo_barras("SAGA001-V307=V311-N3", salvar_arquivo=True)
    
    # Teste 3: Em memória
    print("\n3. Gerando código em memória (sem salvar)")
    img3 = gerar_codigo_barras("TEST-001")
    print(f"✅ Imagem gerada: {img3.size[0]}x{img3.size[1]} pixels")
    
    print("\n" + "=" * 60)
    print("✅ TESTES CONCLUÍDOS!")
    print("=" * 60)
