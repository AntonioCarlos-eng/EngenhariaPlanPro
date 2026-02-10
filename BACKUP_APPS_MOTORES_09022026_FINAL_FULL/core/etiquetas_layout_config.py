# ===== DPI PADRÃO FIXO (CRÍTICO) =====
DPI_PADRAO = 300  # DPI fixo para geração e impressão - NÃO ALTERAR
PX_MM = DPI_PADRAO / 25.4  # ~11.81 pixels/mm em 300 DPI

# ===== COMPATIBILIDADE COM TÉRMICAS =====
# Impressoras Argox OS-214 Plus imprimem em modo contínuo com corte automático.
# MARGEM_IMPRESSORA_MM ajusta espaçamento para evitar distorção de escala.
# SE HOUVER CORTE INCORRETO: aumentar valor (ex: 2.5, 3.0)
# SE HOUVER ESPAÇO VAZIO: diminuir valor (ex: 1.5, 1.0)
MARGEM_IMPRESSORA_MM = 2.0  # Offset padrão em mm - medir após impressão

# ===== DIMENSÕES PADRÃO =====
ETIQUETA_MM_LARGURA = 100
ETIQUETA_MM_ALTURA = 150

# ===== FUNÇÕES DE CONVERSÃO =====
def mm_to_px(mm: float, dpi: int = None) -> int:
    """Converte milímetros para pixels com DPI padrão fixo
    SEMPRE usa DPI_PADRAO=300 para garantir consistência
    """
    if dpi is None:
        dpi = DPI_PADRAO
    return int((mm / 25.4) * dpi)

def px_to_mm(px: int, dpi: int = None) -> float:
    """Converte pixels para milímetros"""
    if dpi is None:
        dpi = DPI_PADRAO
    return (px * 25.4) / dpi

# ===== DIMENSÕES EM PIXELS (300 DPI) =====
ETIQUETA_PX_LARGURA = mm_to_px(ETIQUETA_MM_LARGURA, DPI_PADRAO)  # 1181 px
ETIQUETA_PX_ALTURA = mm_to_px(ETIQUETA_MM_ALTURA, DPI_PADRAO)  # 1772 px

# Medidas em milímetros para a etiqueta 10x15 cm
# Escala do app: 4 px por mm (OBSOLETO - usar DPI_PADRAO/25.4)

# Margens e seções
MARGEM_EXTERNA_MM = 10
TOPO_ALTURA_MM = 93
SECAO_MICRO_ALTURA_MM = 19
ESPACO_PICOTE_MM = 2
LARGURA_ETIQUETA_MM = 100

# Blocos do topo
OS_BLOCO_LARGURA_MM = 18
OS_BLOCO_ALTURA_MM = 30
FAIXA_VERTICAL_LARGURA_MM = 10  # faixa com texto vertical (ex.: SAGA.001)

# Tabela técnica (dentro do topo)
TABELA_ALTURA_HEADER_MM = 8
TABELA_ALTURA_LINHA_MM = 10
# Larguras de colunas (somar para caber na área útil do topo)
COL_BITOLA_MM = 16
COL_COMPR_UNIT_MM = 34
COL_PESO_MM = 22
COL_QTDE_MM = 18

# Posição do desenho técnico no topo
DESENHO_X_OFFSET_MM = 8
DESENHO_Y_OFFSET_MM = 40
DESENHO_LARGURA_MM = 55
DESENHO_ALTURA_MM = 45

# Fonte (tamanhos aproximados para 4px/mm)
FONT_PEQ = 6
FONT_MED = 8
FONT_GRD = 10
