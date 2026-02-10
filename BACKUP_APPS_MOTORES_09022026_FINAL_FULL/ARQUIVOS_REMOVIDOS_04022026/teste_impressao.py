"""
Script de teste para janela de impressão profissional
"""

import sys
sys.path.insert(0, 'c:\\EngenhariaPlanPro')

from core.impressao_etiquetas import ImpressaoProfissionalEtiquetas

# Dados de teste (mesma estrutura que o gerador produz)
dados_teste = [
    {
        'viga': 'V8',
        'pos': 'N1',
        'bitola': 10.0,
        'qtde': 2,
        'comp': 2.950,
        'peso': 9.45,
        'os_num': '1-8',
        'codigo_id': 'OBRA_001_OS1-8',
        'barcode_img': None,
        'caminho_desenho': None
    },
    {
        'viga': 'V9',
        'pos': 'N2',
        'bitola': 12.5,
        'qtde': 3,
        'comp': 3.200,
        'peso': 12.50,
        'os_num': '1-9',
        'codigo_id': 'OBRA_001_OS1-9',
        'barcode_img': None,
        'caminho_desenho': None
    }
]

# Criar objeto de impressão
impressao = ImpressaoProfissionalEtiquetas(
    dados_etiquetas=dados_teste,
    obra="OBRA 001",
    pavimento="TÉRREO",
    arquivo_dxf_base="P1_COMPLETO.dxf"
)

# Testar gerações com diferentes rotações
rotacoes = [0, 90, 180, 270]

for rotacao_graus in rotacoes:
    try:
        opcoes = {
            'disposicao': 'uma_por_pagina',
            'orientacao': 'portrait',
            'margem_mm': 5.0,
            'rotacao': rotacao_graus
        }
        
        pdf_path = impressao.gerar_pdf_etiquetas(opcoes)
        print(f"✅ PDF gerado com rotação {rotacao_graus}°: {pdf_path}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF com rotação {rotacao_graus}°: {e}")
        import traceback
        traceback.print_exc()

print("\n✅ Testes concluídos!")

