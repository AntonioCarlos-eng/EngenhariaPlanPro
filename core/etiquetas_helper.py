# Função utilitária para converter números float em inteiros arredondados
def to_int(*args):
    return [int(round(a)) for a in args]
"""
etiquetas_helper.py
-------------------
Funções auxiliares para geração de etiquetas com código de barras e desenhos técnicos
"""
import os

try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_DISPONIVEL = True
except ImportError as e:
    BARCODE_DISPONIVEL = False

from PIL import Image, ImageTk
import io

# Importar extrator de desenhos do DXF
try:
    from core.desenho_extractor import localizar_desenho_viga_no_dxf
    DESENHO_EXTRACTOR_DISPONIVEL = True
except ImportError as e:
    DESENHO_EXTRACTOR_DISPONIVEL = False


def gerar_codigo_identificador(obra: str, os_num: str, elemento: str, pos: str, bitola: float, comp: float) -> str:
    """
    Gera código identificador único para a barra
    
    Formato: OBRA-OS-ELEM-POS-DBITOLA-COMP
    Exemplo: SAGA001-2-4-ESTx18-N05-D5.00-94113
    
    Args:
        obra: Código da obra (ex: "SAGA 001" -> "SAGA001")
        os_num: Número da OS (ex: "2-4")
        elemento: Nome do elemento (ex: "EST x 18", "V301")
        pos: Posição (ex: "N05")
        bitola: Bitola em mm (ex: 5.0)
        comp: Comprimento em cm (ex: 94.113)
    
    Returns:
        String código identificador
    """
    # Limpar e formatar
    obra_clean = obra.replace(" ", "").replace("/", "-")
    os_clean = os_num.replace(" ", "")
    elem_clean = elemento.replace(" ", "").replace("=", "-")
    pos_clean = pos.replace(" ", "")
    
    # Formatar bitola e comprimento
    bitola_str = f"D{bitola:.1f}".replace(".", "")  # D50 para 5.0mm
    comp_str = f"{int(comp * 100)}"  # Converter m para cm inteiro
    
    codigo = f"{obra_clean}-{os_clean}-{elem_clean}-{pos_clean}-{bitola_str}-{comp_str}"
    
    return codigo


def gerar_codigo_barras_imagem(codigo: str, largura_px: int = 300, altura_px: int = 80) -> Image:
    """
    Gera imagem de código de barras Code128
    
    Args:
        codigo: Texto do código de barras
        largura_px: Largura desejada em pixels
        altura_px: Altura desejada em pixels
    
    Returns:
        PIL Image do código de barras
    """
    if not BARCODE_DISPONIVEL:
        print(f"⚠️ barcode não disponível - retornando imagem em branco")
        return Image.new('RGB', (largura_px, altura_px), 'white')
    
    try:
        # Gerar código de barras Code128
        code128_class = barcode.get_barcode_class('code128')
        
        # Opções do writer
        # Opções do writer (PASSO 5: otimizado para térmicas)
        options = {
            'module_width': 0.5,        # Barras mais largas = menos distorsão
            'module_height': 12,        # Altura fixa para legibilidade
            'quiet_zone': 3,            # Mais margem para segurança de leitura
            'font_size': 10,            # Fonte maior para textos visível
            'text_distance': 4,         # Mais espaço entre barcode e texto
            'write_text': True          # Manter texto para referência visual
        }
        
        codigo_obj = code128_class(codigo, writer=ImageWriter())
        
        # Gerar em memória
        buffer = io.BytesIO()
        codigo_obj.write(buffer, options=options)
        buffer.seek(0)
        
        # Carregar como PIL Image
        img = Image.open(buffer)
        
        # Redimensionar se necessário
        largura_px, altura_px = to_int(largura_px, altura_px)
        if img.size[0] != largura_px or img.size[1] != altura_px:
            img = img.resize((largura_px, altura_px), Image.Resampling.LANCZOS)
        
        return img
        
    except Exception as e:
        print(f"⚠️ Erro ao gerar código de barras: {e}")
        # Retornar imagem em branco como fallback
        return Image.new('RGB', (largura_px, altura_px), 'white')


def localizar_desenho_barra(pasta_etiquetas: str, arquivo_dxf: str, viga: str, pos: str, 
                             bitola: float, qtde: int, comp_cm: float) -> str:
    """
    Localiza desenho técnico da barra exclusivamente a partir dos artefatos
    gerados pelo fluxo real do programa (sem usar banco_desenhos).
    
    Busca PNGs na ordem:
    1. Desenho com detalhe específico: export/desenhos_vigas/{viga}_{detalhe}.png
    2. Desenho genérico da viga: export/desenhos_vigas/{viga}_desenho.png
    3. PNG específico legado com padrão completo dentro de `pasta_etiquetas`
    """
    
    # Mapear posição para tipo de detalhe (N1, N2, N3)
    detalhe_map = {
        'N1': 'N1',
        'N2': 'N2',
        'N3': 'N3',
        '11': 'N3',  # Estribo N3
    }
    
    detalhe = detalhe_map.get(pos, 'N1')  # Default N1
    
    # 2. Tentar desenho com detalhe específico
    pasta_desenhos = "export/desenhos_vigas"
    if os.path.exists(pasta_desenhos):
        arquivo_detalhe = os.path.join(pasta_desenhos, f"{viga}_{detalhe}.png")
        if os.path.exists(arquivo_detalhe):
            return arquivo_detalhe
    
    # 3. Tentar desenho genérico da viga
    if os.path.exists(pasta_desenhos):
        arquivo_desenho = os.path.join(pasta_desenhos, f"{viga}_desenho.png")
        if os.path.exists(arquivo_desenho):
            return arquivo_desenho
    
    # 4. Buscar PNG legado pré-gerado com padrão específico
    if os.path.exists(pasta_etiquetas):
        arq_base = os.path.splitext(os.path.basename(arquivo_dxf))[0]
        comp_int = int(round(comp_cm))
        padrao = f"{arq_base}_{viga}_{pos}_b{bitola}_q{qtde}_c{comp_int}cm_"
        try:
            for arq in os.listdir(pasta_etiquetas):
                if arq.startswith(padrao) and arq.endswith('.png'):
                    return os.path.join(pasta_etiquetas, arq)
        except Exception as e:
            print(f"⚠️ Erro ao buscar desenho: {e}")

    return None


def carregar_desenho_redimensionado(caminho_png: str, largura_px: int, altura_px: int) -> ImageTk.PhotoImage:
    """
    Carrega e redimensiona desenho técnico para tkinter
    
    ATUALIZADO: Suporta extração dinâmica do DXF se caminho começar com "DXF:"
    
    Args:
        caminho_png: Caminho do arquivo PNG ou "DXF:{caminho_dxf}|{viga}|{pos}"
        largura_px: Largura desejada
        altura_px: Altura desejada
    
    Returns:
        ImageTk.PhotoImage pronto para canvas.create_image()
    """
    try:
        # Verificar se é extração dinâmica do DXF
        if caminho_png and caminho_png.startswith("DXF:"):
            if not DESENHO_EXTRACTOR_DISPONIVEL:
                print(f"⚠️ Extrator de desenho não disponível")
                return None
            
            # Parse: DXF:{caminho}|{viga}|{pos}
            partes = caminho_png[4:].split('|')
            dxf_path = partes[0]
            viga = partes[1] if len(partes) > 1 else ""
            pos = partes[2] if len(partes) > 2 else ""
            
            print(f"   🖼️ DXF: {viga}/{pos} ({largura_px}x{altura_px}px)")
            
            # Extrair desenho do DXF
            img = localizar_desenho_viga_no_dxf(dxf_path, viga, pos, largura_px, altura_px)
            if img:
                print(f"      ✅ Imagem extraída: {img.size}")
                return ImageTk.PhotoImage(img)
            else:
                print(f"      ❌ Extração retornou None")
            return None
        
        # Caminho normal de PNG
        img = Image.open(caminho_png)
        img = img.convert("RGBA")
        
        # PASSO 4: Redimensionar com filtro LANCZOS para melhor qualidade (sem pixelização)
        # Usar resize() com tamanho EXATO, não thumbnail() que pode não forçar dimensões
        img = img.resize((largura_px, altura_px), Image.Resampling.LANCZOS)
        
        # Converter para PhotoImage
        return ImageTk.PhotoImage(img)
        
    except Exception as e:
        print(f"⚠️ Erro ao carregar desenho {caminho_png}: {e}")
        return None


def formatar_os_numero(indice: int, total: int) -> str:
    """
    Formata número da OS no padrão "2-4" (item 2 de 4)
    
    Args:
        indice: Índice da barra (0-based)
        total: Total de barras
    
    Returns:
        String no formato "X-Y"
    """
    return f"{indice + 1}-{total}"
