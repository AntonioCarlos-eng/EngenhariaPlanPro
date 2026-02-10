# Função utilitária para converter números float em inteiros arredondados
def to_int(*args):
    return [int(round(a)) for a in args]
def desenhar_bloco_os(c, x, y, largura, altura, texto_os):
    espacamento = 12
    c.setFont("Helvetica-Bold", 10)
    linhas = texto_os.strip().split("\n")
    y_pos = y + altura - espacamento
    x, y, largura, altura = to_int(x, y, largura, altura)
    c.rect(x, y, largura, altura, stroke=1, fill=0)
    for linha in linhas:
        c.drawCentredString(x + largura // 2, y_pos, linha.strip())
        y_pos -= espacamento
def desenhar_cabecalho_organizado(c, x_start, y_start, obra, desenho, pavimento, elemento):
    from core.etiquetas_layout_config import DPI_PADRAO
    pxmm = DPI_PADRAO / 25.4
    espacamento_px = int(round(7 * pxmm))
    x_label, x_valor, y_pos = to_int(x_start + 5 * pxmm, x_start + 33 * pxmm, y_start)

    # Strings limpas e seguras
    obra_txt = obra.strip() if obra else "OBRA 001"
    desenho_txt = desenho.strip() if desenho else "SEM DESENHO"
    pavimento_txt = pavimento.strip() if pavimento else "TÉRREO"
    viga = elemento if elemento else "-"
    pos = ""
    if isinstance(elemento, (tuple, list)) and len(elemento) == 2:
        viga, pos = elemento

    print(f"[DEBUG] Obra: '{obra_txt}'")
    print(f"[DEBUG] Desenho: '{desenho_txt}'")
    print(f"[DEBUG] Pavimento: '{pavimento_txt}'")
    print(f"[DEBUG] Viga: '{viga}' / POS: '{pos}'")

    c.setFont("Helvetica", 7)
    c.drawString(x_label, y_pos, "Sigla/Obra:")
    c.drawString(x_valor, y_pos, obra_txt)
    y_pos -= espacamento_px
    c.drawString(x_label, y_pos, "Desenho:")
    c.drawString(x_valor, y_pos, desenho_txt)
    y_pos -= espacamento_px
    c.drawString(x_label, y_pos, "Pavimento:")
    c.drawString(x_valor, y_pos, pavimento_txt)
    y_pos -= espacamento_px
    c.drawString(x_label, y_pos, "Elemento:")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x_valor, y_pos, viga)
    # POS destacado, tamanho moderado e posição ajustada
    if pos:
        c.setFont("Helvetica-Bold", 22)
        pos_x = x_valor + int(round(18 * pxmm))
        pos_y = y_pos - int(round(5 * pxmm))
        c.drawString(pos_x, pos_y, str(pos))
"""
Sistema profissional de impressão de etiquetas
- Template com estrutura completa (bordas, divisões, blocos, picotes)
- Preenchimento dinâmico com dados do DXF
- Janela de impressão com opções (impressora, orientação, disposição)
- Impressão direta sem PNG, sem Photo Print
"""

import os
import subprocess
import time
import logging
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# Configurar logging
log_file = "output/impressao/log_impressao.txt"
os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import subprocess
import tempfile


class ImpressaoProfissionalEtiquetas:
    """
    Impressão profissional de etiquetas com PDF e opções de impressão
    Mantém integridade do gerador original - usa dados processados
    """
    
    def __init__(self, dados_etiquetas: List[Dict], obra: str, pavimento: str, 
                 arquivo_dxf_base: str = "", pasta_saida: str = "output/impressao"):
        """
        Args:
            dados_etiquetas: Lista de dicts com dados já processados (do gerador)
            obra: Nome da obra
            pavimento: Pavimento/andar
            arquivo_dxf_base: Nome do arquivo DXF base
            pasta_saida: Pasta para salvar PDFs temporários
        """
        self.dados = dados_etiquetas
        self.obra = obra
        self.pavimento = pavimento
        self.arquivo_dxf_base = arquivo_dxf_base
        self.pasta_saida = pasta_saida
        
        # Criar pasta se não existir
        if not os.path.exists(pasta_saida):
            os.makedirs(pasta_saida)
        
        self.etiqueta_width = 100 * mm  # 100mm
        self.etiqueta_height = 150 * mm  # 150mm
        
        print("[IMPRESSÃO] Sistema de impressão profissional inicializado")
    
    def gerar_pdf_etiquetas(self, opcoes: Dict = None) -> str:
        """
        Gera PDF com etiquetas em layout profissional
        
        Args:
            opcoes: Dict com opções {
                'disposicao': 'uma_por_pagina' | 'duas_por_pagina' | 'tres_por_pagina',
                'orientacao': 'portrait' | 'landscape',
                'margem_mm': float,
                'rotacao': 0 | 90 | 180 | 270  # Graus de rotação
            }
            
        Returns:
            Caminho do PDF gerado
        """
        if opcoes is None:
            opcoes = {
                'disposicao': 'uma_por_pagina',
                'orientacao': 'portrait',
                'margem_mm': 5.0,
                'rotacao': 0
            }
        
        disposicao = opcoes.get('disposicao', 'uma_por_pagina')
        orientacao = opcoes.get('orientacao', 'portrait')
        margem = opcoes.get('margem_mm', 5.0) * mm
        rotacao = opcoes.get('rotacao', 0)
        
        logger.info(f"Gerando PDF com opções:")
        logger.info(f"  - Disposição: {disposicao}")
        logger.info(f"  - Orientação: {orientacao}")
        logger.info(f"  - Rotação: {rotacao}°")
        logger.info(f"  - Margem: {opcoes.get('margem_mm', 5.0)}mm")
        logger.info(f"  - Total de etiquetas: {len(self.dados)}")
        
        # Definir tamanho de página
        if orientacao == 'landscape':
            pagesize = (11.69 * inch, 8.27 * inch)  # A4 landscape
        else:
            pagesize = (8.27 * inch, 11.69 * inch)  # A4 portrait
        
        # Caminho do PDF
        nome_pdf = f"ETIQUETAS_{self.obra.replace(' ', '_')}_{len(self.dados)}_etiq.pdf"
        caminho_pdf = os.path.join(self.pasta_saida, nome_pdf)
        
        print(f"[IMPRESSÃO] Gerando PDF: {caminho_pdf}")
        
        # Criar canvas
        c = canvas.Canvas(caminho_pdf, pagesize=pagesize)
        c.setTitle(f"Etiquetas - {self.obra}")
        
        page_width, page_height = pagesize
        y_position = page_height - margem
        etiq_por_pagina = self._get_etiq_por_pagina(disposicao)
        
        etiq_counter = 0
        
        for idx, dados in enumerate(self.dados):
            try:
                # Se preencheu a página, nova página
                if etiq_counter >= etiq_por_pagina:
                    c.showPage()
                    y_position = page_height - margem
                    etiq_counter = 0
                
                # Desenhar etiqueta
                y_position = self._desenhar_etiqueta_no_pdf(
                    c, dados, idx,
                    x=margem,
                    y=y_position,
                    width=self.etiqueta_width,
                    height=self.etiqueta_height,
                    disposicao=disposicao,
                    page_width=page_width,
                    page_height=page_height,
                    rotacao=rotacao
                )
                
                etiq_counter += 1
                
            except Exception as e:
                logger.error(f"Falha ao desenhar etiqueta {idx+1}: {e}", exc_info=True)
        
        c.save()
        logger.info(f"PDF gerado com sucesso: {caminho_pdf}")
        return caminho_pdf


# Função global padronizada para mm -> px
def mm_to_px(mm_val, dpi=300):
    return int(round((mm_val / 25.4) * dpi))

    def _gerar_imagem_etiqueta(self, dados: Dict, dpi_x: int = 300, dpi_y: int = 300):
        """Gera uma imagem PIL da etiqueta com o mesmo layout (100x150mm).
        FORÇA DPI=300 fixo para garantir dimensões exatas.
        """
        from PIL import Image, ImageDraw, ImageFont
        from core.etiquetas_layout_config import DPI_PADRAO
        import os

        # FORÇAR DPI FIXO = 300 (CRÍTICO)
        dpi_x = dpi_y = DPI_PADRAO



        viga = dados.get('viga', '')
        pos = dados.get('pos', '')
        bitola = dados.get('bitola', 0.0)
        qtde = dados.get('qtde', 0)
        comp = dados.get('comp', 0.0)
        peso = dados.get('peso', 0.0)
        os_num = dados.get('os_num', '')
        barcode_img = dados.get('barcode_img')
        caminho_desenho = dados.get('caminho_desenho')

        label_w = mm_to_px(100, dpi_x)
        label_h = mm_to_px(150, dpi_y)
        img = Image.new("RGB", (label_w, label_h), "white")
        draw = ImageDraw.Draw(img)

        scale = dpi_x / 96.0
        # PASSO 5: Forçar fonte com fallback consistente
        f_tiny = f_small = f_med = f_large = f_xlarge = None
        
        # Tentar Arial (Windows)
        try:
            f_tiny = ImageFont.truetype("arial.ttf", int(10 * scale))
            f_small = ImageFont.truetype("arial.ttf", int(14 * scale))
            f_med = ImageFont.truetype("arial.ttf", int(18 * scale))
            f_large = ImageFont.truetype("arial.ttf", int(22 * scale))
            f_xlarge = ImageFont.truetype("arial.ttf", int(28 * scale))
            print("[FONT] Arial TrueType carregada com sucesso")
        except Exception as e:
            print(f"[FONT] Falha ao carregar Arial.ttf: {e}")
            # Fallback: tentar outras localizações
            arial_paths = [
                r"C:\Windows\Fonts\arial.ttf",
                r"C:\Windows\Fonts\Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/System/Library/Fonts/Arial.ttf"
            ]
            for arial_path in arial_paths:
                try:
                    if os.path.exists(arial_path):
                        f_tiny = ImageFont.truetype(arial_path, int(10 * scale))
                        f_small = ImageFont.truetype(arial_path, int(14 * scale))
                        f_med = ImageFont.truetype(arial_path, int(18 * scale))
                        f_large = ImageFont.truetype(arial_path, int(22 * scale))
                        f_xlarge = ImageFont.truetype(arial_path, int(28 * scale))
                        print(f"[FONT] Fonte carregada de {arial_path}")
                        break
                except Exception:
                    continue
        
        # Último fallback: fonte padrão do PIL
        if f_tiny is None:
            print("[FONT] Usando fonte padrão do PIL (fallback)")
            f_tiny = f_small = f_med = f_large = f_xlarge = ImageFont.load_default()

        margin = mm_to_px(3, dpi_x)
        faixa_larg = mm_to_px(10, dpi_x)
        altura_topo = mm_to_px(92, dpi_y)
        altura_picote = mm_to_px(18, dpi_y)
        espaco_picote = mm_to_px(2, dpi_y)

        # Borda externa
        draw.rectangle([0, 0, label_w - 1, label_h - 1], outline="#ff6f00", width=int(3 * scale))

        # Faixa vertical direita
        faixa_x1 = label_w - faixa_larg - margin
        faixa_x2 = label_w - margin
        draw.rectangle([faixa_x1, margin, faixa_x2, altura_topo], fill="#ff8c00", outline="black", width=1)
        # Faixa vertical com texto centralizado e rotacionado
        try:
            largura_faixa_px = int(round(faixa_larg))
            altura_faixa_px = int(round(altura_topo - margin))
            temp_img = Image.new("RGBA", (largura_faixa_px, altura_faixa_px), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            try:
                fonte = ImageFont.truetype("arial.ttf", int(14 * dpi_x / 96))
            except Exception:
                fonte = ImageFont.load_default()
            # Dividir texto em múltiplas linhas se for muito longo
            texto = self.obra
            linhas = texto.split()
            y_text = 5
            for linha in linhas:
                w, h = temp_draw.textsize(linha, font=fonte)
                temp_draw.text(((largura_faixa_px - w) // 2, y_text), linha, font=fonte, fill="black")
                y_text += h + 2
            # Rotacionar 90 graus
            temp_img_rot = temp_img.rotate(90, expand=True)
            pos_x = faixa_x1 + (largura_faixa_px - temp_img_rot.width) // 2
            pos_y = margin + mm_to_px(12, dpi_y)
            img.paste(temp_img_rot, (pos_x, pos_y), temp_img_rot)
        except Exception:
            pass

        # Bloco OS
        os_w = mm_to_px(22, dpi_x)
        os_h = mm_to_px(26, dpi_y)
        os_x1 = faixa_x1 - os_w - margin
        os_y1 = margin
        os_x2 = os_x1 + os_w
        os_y2 = os_y1 + os_h
        draw.rectangle([os_x1, os_y1, os_x2, os_y2], outline="black", width=2)
        draw.text((os_x1 + mm_to_px(2, dpi_x), os_y1 + mm_to_px(1.5, dpi_y)), "OS", font=f_small, fill="black")
        
        # PASSO 3: Evitar truncamento/quebra de linhas - dividir em múltiplas linhas
        os_num_str = str(os_num)
        linhas_os = os_num_str.split("-") if "-" in os_num_str else [os_num_str]
        start_y = os_y1 + os_h // 2 - mm_to_px(6, dpi_y)
        espaco_linha = mm_to_px(8, dpi_y)
        for i, linha in enumerate(linhas_os):
            y_pos = start_y + i * espaco_linha
            draw.text(((os_x1 + os_x2) // 2, y_pos), linha, font=f_large, fill="black", anchor="mm")

        # Cabeçalho à esquerda
        x_label = margin + mm_to_px(2, dpi_x)
        x_value = x_label + mm_to_px(32, dpi_x)
        y_line = margin + mm_to_px(1, dpi_y)
        header_campos = [
            ("Sigla/Obra", self.obra),
            ("Desenho", self.arquivo_dxf_base or ""),
            ("Pavimento", self.pavimento),
            ("Elemento", viga),
        ]
        for label_txt, value_txt in header_campos:
            draw.text((x_label, y_line), label_txt, font=f_tiny, fill="black")
            draw.text((x_value, y_line), value_txt, font=f_med if label_txt == "Sigla/Obra" else f_small, fill="black")
            y_line += mm_to_px(6.5, dpi_y)

        # POS
        pos_x = os_x1 - mm_to_px(22, dpi_x)
        pos_y = margin + mm_to_px(18, dpi_y)
        draw.text((pos_x, pos_y - mm_to_px(3, dpi_y)), "POS", font=f_tiny, fill="black", anchor="mm")
        draw.text((pos_x, pos_y + mm_to_px(6, dpi_y)), pos, font=f_xlarge, fill="black", anchor="mm")

        # Tabela
        tab_y = margin + mm_to_px(32, dpi_y)
        tab_h = mm_to_px(20, dpi_y)
        col_widths = [mm_to_px(16, dpi_x), mm_to_px(32, dpi_x), mm_to_px(18, dpi_x), mm_to_px(16, dpi_x)]
        tab_w = sum(col_widths)
        tab_x1 = margin + mm_to_px(4, dpi_x)
        tab_x2 = tab_x1 + tab_w
        draw.rectangle([tab_x1, tab_y, tab_x2, tab_y + tab_h], outline="black", width=1)
        x_col = tab_x1
        for w in col_widths[:-1]:
            x_col += w
            draw.line([(x_col, tab_y), (x_col, tab_y + tab_h)], fill="black", width=1)
        draw.line([(tab_x1, tab_y + tab_h // 2), (tab_x2, tab_y + tab_h // 2)], fill="black", width=1)
        headers = ["Bitola", "Compr. Unit.", "Peso", "Qtde"]
        values = [f"{bitola:.2f}", f"{comp:.3f}", f"{peso:.2f}", f"{qtde}"]
        x_col = tab_x1
        for h, v, w in zip(headers, values, col_widths):
            draw.text((x_col + w // 2, tab_y + mm_to_px(1, dpi_y)), h, font=f_tiny, fill="black", anchor="mt")
            draw.text((x_col + w // 2, tab_y + tab_h // 2 + mm_to_px(1.5, dpi_y)), v, font=f_small, fill="black", anchor="mt")
            x_col += w

        # Área do desenho técnico
        draw_y = tab_y + tab_h + mm_to_px(6, dpi_y)
        draw_h = mm_to_px(38, dpi_y)
        area_x1 = margin + mm_to_px(8, dpi_x)
        area_x2 = faixa_x1 - mm_to_px(5, dpi_x)
        draw.rectangle([area_x1, draw_y, area_x2, draw_y + draw_h], outline="#c8102e", width=2)
        avail_w = max(1, (area_x2 - area_x1) - 12)
        avail_h = max(1, draw_h - 12)
        if caminho_desenho and os.path.exists(caminho_desenho):
            try:
                img_png = Image.open(caminho_desenho).convert("RGBA")
                # Definir área alvo em mm
                DESENHO_LARGURA_MM = (area_x2 - area_x1) / mm
                DESENHO_ALTURA_MM = draw_h / mm
                w_target = mm_to_px(DESENHO_LARGURA_MM, dpi_x)
                h_target = mm_to_px(DESENHO_ALTURA_MM, dpi_y)
                # Ajustar proporção sem distorcer
                aspect = img_png.width / img_png.height
                target_aspect = w_target / h_target
                if aspect > target_aspect:
                    new_w = w_target
                    new_h = int(w_target / aspect)
                else:
                    new_h = h_target
                    new_w = int(h_target * aspect)
                img_redim = img_png.resize((new_w, new_h), Image.Resampling.LANCZOS)
                px = int(area_x1 + ((area_x2 - area_x1 - img_redim.width) // 2))
                py = int(draw_y + ((draw_h - img_redim.height) // 2))
                img.paste(img_redim, (px, py), img_redim)
            except Exception as e:
                logger.warning(f"Erro ao carregar desenho {viga}/{pos}: {e}")

        # Separação topo
        draw.line([(margin, altura_topo), (label_w - margin, altura_topo)], fill="#cccccc", width=1)

        # Picotes + código de barras
        y_picote = altura_topo + espaco_picote
        picote_w = label_w - 2 * margin
        for p in range(3):
            box_top = y_picote
            box_bottom = y_picote + altura_picote
            draw.rectangle([margin, box_top, margin + picote_w, box_bottom], outline="#cccccc", width=1)
            if barcode_img:
                try:
                    barcode_rgb = barcode_img.convert("RGB")
                    bw = picote_w - mm_to_px(8, dpi_x)
                    bh = altura_picote - mm_to_px(6, dpi_y)
                    resample = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS
                    # CRÍTICO: usar resize() com tamanho EXATO, não thumbnail()
                    aspect = barcode_rgb.width / barcode_rgb.height
                    if aspect > (bw / bh):
                        new_w = bw
                        new_h = int(bw / aspect)
                    else:
                        new_h = bh
                        new_w = int(bh * aspect)
                    barcode_rgb = barcode_rgb.resize((new_w, new_h), resample=resample)
                    bx = margin + mm_to_px(2, dpi_x)
                    by = box_top + mm_to_px(1, dpi_y)
                    img.paste(barcode_rgb, (bx, by))
                except Exception as e:
                    logger.warning(f"Erro ao desenhar barcode {viga}/{pos}: {e}")
            # Legenda separada do código de barras com espaçamento vertical
            legenda_x = bx + new_w // 2
            legenda_y = by + new_h + mm_to_px(3, dpi_y)
            draw.text((legenda_x, legenda_y), f"Elem: {viga} {pos} OS {os_num} Ø {bitola:.2f}", font=f_tiny, fill="black", anchor="mm")
            comp_x = bx + new_w - mm_to_px(3, dpi_x)
            comp_y = by + new_h + mm_to_px(8, dpi_y)
            draw.text((comp_x, comp_y), "Compr. Corte", font=f_tiny, fill="black", anchor="rm")
            draw.text((comp_x, comp_y - mm_to_px(5, dpi_y)), f"{comp:.3f}", font=f_small, fill="black", anchor="rm")
            if p < 2:
                y_corte = box_bottom
                for x in range(margin, margin + picote_w, 10):
                    draw.line([(x, y_corte), (x + 5, y_corte)], fill="#c8102e", width=1)
            y_picote += altura_picote + espaco_picote

        return img

    def imprimir_direto_gdi(self, impressora: str, rotacao: int = 0, dpi_dest: Optional[int] = None) -> bool:
        """Imprime diretamente via GDI sem diálogos, usando PIL->DIB.
        - Não altera a impressora padrão
        - Usa 100x150mm em DPI nativo da impressora
        """
        try:
            import win32print
            import win32ui
            import win32con
            from PIL import ImageWin

            logger.info(f"[GDI] Impressão direta GDI iniciada: {impressora}")

            # Criar DC da impressora
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(impressora)

            # FORÇAR DPI FIXO = 300 (PASSO 1 - CRÍTICO)
            from core.etiquetas_layout_config import DPI_PADRAO, MARGEM_IMPRESSORA_MM, mm_to_px
            
            dpiX = dpiY = DPI_PADRAO  # SEMPRE 300, nunca usar DPI da impressora
            logger.info(f"[GDI] DPI fixo FORÇADO: {DPI_PADRAO}x{DPI_PADRAO} (ignorar DPI nativo da impressora)")

            # Tamanho alvo em pixels para 100x150mm + margens para térmicas
            tgt_w = mm_to_px(100 + 2 * MARGEM_IMPRESSORA_MM, dpiX)
            tgt_h = mm_to_px(150 + 2 * MARGEM_IMPRESSORA_MM, dpiY)
            logger.info(f"[GDI] Área alvo: {tgt_w}x{tgt_h}px (100x150mm + margens {MARGEM_IMPRESSORA_MM}mm @ DPI {DPI_PADRAO})")

            # Iniciar documento SEM diálogos
            # Para impressoras térmicas (Argox), usar "raw" quando possível
            try:
                hDC.StartDoc("Etiquetas", None)  # None = sem diálogos
            except:
                hDC.StartDoc("Etiquetas")  # Fallback se StartDoc com 2 args falhar

            # Para cada etiqueta
            for idx, dados in enumerate(self.dados):
                try:
                    img = self._gerar_imagem_etiqueta(dados, dpi_x=dpiX, dpi_y=dpiY)
                    if rotacao in (90, 180, 270):
                        img = img.rotate(rotacao, expand=True)

                    # Redimensionar exatamente para área alvo (com margens) usando LANCZOS
                    img = img.resize((tgt_w, tgt_h), Image.Resampling.LANCZOS)

                    dib = ImageWin.Dib(img)

                    hDC.StartPage()
                    # Desenhar ocupando toda a página com margem de segurança
                    # Offset de (0,0) = sem espaço extra, impressora térmica faz o corte
                    dib.draw(hDC.GetHandleOutput(), (0, 0, tgt_w, tgt_h))
                    hDC.EndPage()
                    logger.info(f"[GDI] Página {idx+1} enviada para {impressora} ({tgt_w}x{tgt_h}px)")
                except Exception as e:
                    logger.error(f"[GDI] Falha ao imprimir etiqueta {idx+1}: {e}", exc_info=True)

            hDC.EndDoc()  # Finaliza SEM preview
            hDC.DeleteDC()
            logger.info("[GDI] Documento finalizado com sucesso")
            return True

        except Exception as e:
            logger.error(f"[GDI] Erro geral: {e}", exc_info=True)
            return False
    
    def _get_etiq_por_pagina(self, disposicao: str) -> int:
        """Retorna quantas etiquetas cabem por página"""
        mapping = {
            'uma_por_pagina': 1,
            'duas_por_pagina': 2,
            'tres_por_pagina': 3
        }
        return mapping.get(disposicao, 1)
    
    def _desenhar_etiqueta_no_pdf(self, c, dados: Dict, idx: int, x, y, 
                                   width, height, disposicao: str, 
                                   page_width, page_height, rotacao: int = 0) -> float:
        """
        Desenha UMA etiqueta no PDF
        
        Args:
            rotacao: Graus de rotação (0, 90, 180, 270)
        
        Returns:
            Nova posição Y para próxima etiqueta
        """
        # Dados da etiqueta
        viga = dados.get('viga', '')
        pos = dados.get('pos', '')
        bitola = dados.get('bitola', 0.0)
        qtde = dados.get('qtde', 0)
        comp = dados.get('comp', 0.0)  # metros
        peso = dados.get('peso', 0.0)
        os_num = dados.get('os_num', '')
        barcode_img = dados.get('barcode_img')  # Objeto Image da PIL
        
        # Cores
        color_orange = colors.HexColor("#ff6f00")
        color_orange_light = colors.HexColor("#ff8c00")
        color_red = colors.HexColor("#c8102e")
        
        # Aplicar rotação se necessário
        if rotacao != 0:
            c.saveState()
            # Rotacionar em torno do centro da etiqueta
            center_x = x + width / 2
            center_y = y - height / 2
            c.translate(center_x, center_y)
            c.rotate(rotacao)
            c.translate(-center_x, -center_y)
        
        # ESTRUTURA DA ETIQUETA
        # 1. Borda externa
        c.setLineWidth(2)
        c.setStrokeColor(color_orange)
        c.rect(x, y - height, width, height, stroke=1, fill=0)
        
        # 2. Faixa vertical laranja (lado direito)
        faixa_width = 10 * mm
        faixa_x = x + width - faixa_width - 3 * mm
        c.setFillColor(color_orange_light)
        c.rect(faixa_x, y - height + 3*mm, faixa_width, 65*mm, stroke=1, fill=1)
        
        # 3. Bloco OS (canto superior direito)
        os_width = 22 * mm
        os_height = 26 * mm
        os_x = faixa_x - os_width - 3 * mm
        os_y = y - os_height
        # Montar texto multilinha: "OS" na primeira linha, depois cada parte do número
        os_num_str = str(os_num)
        linhas_os = ["OS"]
        if "-" in os_num_str:
            linhas_os += os_num_str.split("-")
        else:
            linhas_os.append(os_num_str)
        desenhar_bloco_os(c, os_x, os_y, os_width, os_height, "\n".join(linhas_os))
        
        # 4. Cabeçalho à esquerda (Obra, Desenho, Pavimento, Elemento)
        desenhar_cabecalho_organizado(
            c,
            x,
            y - int(round(4 * (300 / 25.4))),
            self.obra,
            self.arquivo_dxf_base or "",
            self.pavimento,
            viga
        )
        
        # 5. POS destacado
        pos_x = os_x - 22 * mm
        pos_y = y - 20 * mm
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(pos_x, pos_y, pos)
        c.setFont("Helvetica", 7)
        c.drawCentredString(pos_x, pos_y + 3*mm, "POS")
        
        # 6. Tabela de especificações
        tab_y = y - 34 * mm  # aumenta o espaçamento do topo
        tab_height = 22 * mm  # aumenta altura da tabela
        tab_x = x + 6 * mm  # aumenta margem esquerda
        
        if caminho_desenho and os.path.exists(caminho_desenho):
                try:
                    with Image.open(caminho_desenho) as img_pil:
                        if img_pil.mode != 'RGB':
                            img_pil = img_pil.convert('RGB')
                        w_px = int(round(draw_width))
                        h_px = int(round(draw_height))
                        # Redimensiona exatamente para a área disponível, sem distorção
                        img_pil = img_pil.resize((w_px, h_px), Image.Resampling.LANCZOS)
                        temp_img = os.path.join(self.pasta_saida, f"temp_draw_{idx}.png")
                        img_pil.save(temp_img)
                        c.drawImage(temp_img, draw_x, draw_y - draw_height, width=draw_width, height=draw_height)
                except Exception as e:
                    print(f"[WARN] Erro ao inserir desenho {viga}/{pos}: {e}")
        draw_y = tab_y - tab_height - 8 * mm  # aumenta espaçamento após tabela
        draw_height = 38 * mm
        draw_x = x + 10 * mm  # aumenta margem esquerda do desenho
        draw_width = faixa_x - draw_x - 7 * mm  # aumenta margem direita
        
        c.setLineWidth(1.5)
        c.setStrokeColor(color_red)
        c.setFillColor(colors.HexColor("#ffffee"))
        c.rect(draw_x, draw_y - draw_height, draw_width, draw_height, stroke=1, fill=1)
        
        # Inserir desenho técnico se disponível (PNG em alta resolução, ancoragem esquerda/topo)
        caminho_desenho = dados.get('caminho_desenho')
        if caminho_desenho and os.path.exists(caminho_desenho):
            try:
                # Redimensionar imagem para caber na área exata (LANCZOS, sem distorção)
                with Image.open(caminho_desenho) as img_pil:
                    if img_pil.mode != 'RGBA':
                        img_pil = img_pil.convert('RGBA')
                    largura_mm = (draw_width - 8*mm) / mm
                    altura_mm = (draw_height - 8*mm) / mm
                    DPI_PADRAO = 300
                    def mm_to_px(mm_val, dpi=DPI_PADRAO):
                        return int(round((mm_val / 25.4) * dpi))
                    largura_px = mm_to_px(largura_mm)
                    altura_px = mm_to_px(altura_mm)
                    img_redim = img_pil.resize((largura_px, altura_px), Image.Resampling.LANCZOS)
                    temp_img = os.path.join(self.pasta_saida, f"temp_draw_{idx}.png")
                    img_redim.save(temp_img)
                    # Ancorar à esquerda e topo do retângulo
                    img_x = draw_x + 4*mm
                    img_y = draw_y - draw_height + 4*mm
                    c.drawImage(temp_img, img_x, img_y, width=largura_px/mm*mm, height=altura_px/mm*mm, mask='auto')
            except Exception as e:
                print(f"[WARN] Erro ao inserir desenho {viga}/{pos}: {e}")
        
        # Texto "Página"
        c.setFont("Helvetica", 6)
        page_x = draw_x + draw_width / 2
        c.drawCentredString(page_x, draw_y - draw_height - 2*mm, f"Página {idx+1} de {len(self.dados)}")
        
        # 8. Picotes com código de barras (3 seções)
        picote_y = y - 92 * mm
        picote_height = 18 * mm
        picote_spacing = 2 * mm
        picote_width = width - 2 * 3 * mm
        
        for p in range(3):
            box_y = picote_y - p * (picote_height + picote_spacing)
            
            # Desenhar box do picote
            c.setLineWidth(0.5)
            c.setStrokeColor(colors.HexColor("#cccccc"))
            c.rect(x + 3*mm, box_y - picote_height, picote_width, picote_height, stroke=1)
            
            # Código de barras
            if barcode_img:
                try:
                    # Redimensionar barcode
                    barcode_w = picote_width - 6*mm
                    barcode_h = picote_height - 4*mm
                    barcode = barcode_img.convert('RGB')
                    # CRÍTICO: usar resize() com tamanho EXATO, não thumbnail()
                    aspect = barcode.width / barcode.height
                    mm_w = barcode_w / mm
                    mm_h = barcode_h / mm
                    if aspect > (mm_w / mm_h):
                        new_w = int(mm_w)
                        new_h = int(mm_w / aspect)
                    else:
                        new_h = int(mm_h)
                        new_w = int(mm_h * aspect)
                    barcode = barcode.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    
                    temp_barcode = os.path.join(self.pasta_saida, f"temp_barcode_{idx}_{p}.png")
                    barcode.save(temp_barcode)
                    
                    barcode_x = x + 3*mm + 2*mm
                    barcode_y = box_y - picote_height + 1*mm
                    c.drawImage(temp_barcode, barcode_x, barcode_y, 
                              width=barcode.width*mm, height=barcode.height*mm)
                except Exception as e:
                    print(f"[WARN] Erro ao inserir barcode: {e}")
            
            # Legenda do código de barras com fonte maior e espaçamento vertical
            c.setFont("Helvetica", 8)
            texto_picote = f"Elem: {viga}  {pos}   OS {os_num}   Ø {bitola:.2f}"
            picote_center_x = x + picote_width / 2
            # Legenda 6mm abaixo do código de barras
            mm_to_px = lambda mm_val: int(round((mm_val / 25.4) * 300))
            legenda_y = barcode_y + barcode_h + 6
            c.drawCentredString(picote_center_x, legenda_y, texto_picote)
            # Campos à direita, espaçados verticalmente
            compr_x = x + picote_width - 2*mm
            c.setFont("Helvetica", 7)
            c.drawRightString(compr_x, legenda_y + 12, "Compr. Corte")
            c.drawRightString(compr_x, legenda_y + 22, f"{comp:.3f}m")
            
            # Linha tracejada vermelha entre picotes
            if p < 2:
                c.setStrokeColor(color_red)
                c.setLineWidth(0.5)
                dash_y = box_y - picote_height
                for dash_x in range(int(x + 3*mm), int(x + picote_width), 10):
                    c.line(dash_x, dash_y, min(dash_x + 5, x + picote_width), dash_y)
        
        # Restaurar estado de rotação
        if rotacao != 0:
            c.restoreState()
        
        # Retornar próxima posição Y
        return picote_y - 3 * (picote_height + picote_spacing) - 5 * mm
    
    def obter_impressoras_disponiveis(self) -> List[str]:
        """Lista impressoras disponíveis no Windows"""
        try:
            import win32print
            impressoras = []
            for printer in win32print.EnumPrinters(2):
                impressoras.append(printer[2])
            return impressoras if impressoras else ["Argox OS-214 Plus"]
        except Exception:
            # Fallback: tentar via wmic
            try:
                result = subprocess.run(['wmic', 'logicaldisk', 'get', 'name'], 
                                      capture_output=True, text=True, timeout=5)
                return ["Argox OS-214 Plus"]  # Default
            except Exception:
                return ["Argox OS-214 Plus"]
    
    def imprimir_pdf(self, caminho_pdf: str, impressora: str) -> bool:
        """
        Envia PDF para impressora via Windows
        
        Args:
            caminho_pdf: Caminho do PDF gerado
            impressora: Nome da impressora
            
        Returns:
            True se sucesso
        """
        try:
            logger.info(f"INICIANDO IMPRESSÃO")
            logger.info(f"Impressora: {impressora}")
            logger.info(f"PDF: {caminho_pdf}")
            
            # Verificar se arquivo existe
            if not os.path.exists(caminho_pdf):
                logger.error(f"Arquivo PDF não encontrado: {caminho_pdf}")
                return False
            
            file_size = os.path.getsize(caminho_pdf)
            logger.info(f"Arquivo encontrado - Tamanho: {file_size} bytes")
            
            # Método 1: Tentar com rundll32 printui (mais confiável)
            try:
                logger.info(f"Tentativa 1: rundll32 printui")
                # Usar aspas simples no nome se tiver espaços
                cmd = [
                    'rundll32', 
                    'printui.dll,PrintUIEntry',
                    '/pt',
                    caminho_pdf,
                    f'/n"{impressora}"'
                ]
                logger.debug(f"Comando: {' '.join(cmd)}")
                
                resultado = subprocess.run(cmd, timeout=15, capture_output=True, text=True)
                
                logger.info(f"rundll32 - ReturnCode: {resultado.returncode}")
                if resultado.stdout:
                    logger.debug(f"STDOUT: {resultado.stdout}")
                if resultado.stderr:
                    logger.debug(f"STDERR: {resultado.stderr}")
                
                if resultado.returncode == 0:
                    logger.info(f"✅ SUCESSO: PDF enviado via rundll32 printui")
                    return True
                else:
                    logger.warning(f"rundll32 retornou código: {resultado.returncode}")
                    
            except subprocess.TimeoutExpired:
                logger.warning(f"rundll32 timeout (15s)")
            except Exception as e:
                logger.warning(f"rundll32 falhou: {e}")
            
            # Método 2: Tentar com win32api usando verbo 'printto'
            try:
                logger.info(f"Tentativa 2: win32api.ShellExecute printto")
                import win32api
                
                # 'printto' tenta enviar diretamente para a impressora especificada,
                # se houver um aplicativo associado ao tipo de arquivo com suporte ao verbo.
                rc = win32api.ShellExecute(
                    0,
                    "printto",
                    caminho_pdf,
                    f'"{impressora}"',
                    ".",
                    0
                )
                logger.info(f"win32api.ShellExecute retorno: {rc}")
                logger.info(f"✅ SUCESSO: PDF enviado via ShellExecute printto")
                time.sleep(1)
                return True
                
            except Exception as e:
                logger.warning(f"win32api falhou: {e}")
            
            # Método 3: Último fallback - usar cmd.exe
            try:
                logger.info(f"Tentativa 3: cmd.exe print")
                resultado = subprocess.run(
                    ['cmd', '/c', f'print /D:"{impressora}" "{caminho_pdf}"'],
                    timeout=15,
                    capture_output=True,
                    text=True
                )
                
                logger.info(f"cmd print - ReturnCode: {resultado.returncode}")
                if resultado.returncode == 0:
                    logger.info(f"✅ SUCESSO: PDF enviado via cmd print")
                    return True
                else:
                    logger.warning(f"cmd print retornou: {resultado.returncode}")
                    if resultado.stderr:
                        logger.debug(f"Erro: {resultado.stderr}")
                        
            except Exception as e:
                logger.warning(f"cmd print falhou: {e}")
            
            # Método 4: Fallback final - apenas abrir com padrão
            try:
                logger.info(f"Tentativa 4: os.startfile (impressora padrão)")
                os.startfile(caminho_pdf, "print")
                logger.info(f"✅ SUCESSO: PDF enviado para impressora padrão do sistema")
                time.sleep(1)
                return True
                
            except Exception as e:
                logger.error(f"os.startfile falhou: {e}")
                
            logger.error(f"❌ FALHA: Todas as tentativas de impressão falharam")
            return False
            
        except Exception as e:
            logger.error(f"Erro geral na impressão: {e}", exc_info=True)
            return False
