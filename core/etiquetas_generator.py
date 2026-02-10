# Função utilitária para converter números float em inteiros arredondados
def to_int(*args):
    return [int(round(a)) for a in args]
"""
etiquetas_generator.py
----------------------
Gerador dinâmico de etiquetas a partir de arquivos DXF reais
Processa os DXF e gera etiquetas instantaneamente com código de barras e desenhos
"""
import os
import sys
import re
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageTk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.vigas_motor_v2 import processar_vigas
from core.etiquetas_helper import (
    gerar_codigo_identificador,
    gerar_codigo_barras_imagem,
    localizar_desenho_barra,
    formatar_os_numero
)
from core.peso import peso_linear_kg_m
from core.desenho_extractor import localizar_desenho_viga_no_dxf


class GeradorEtiquetasDinamico:
    """
    Gera etiquetas dinamicamente a partir de arquivos DXF reais
    """
    
    def __init__(self, arquivos_dxf: List[str], pasta_etiquetas: str = None, 
                 obra: str = "OBRA 001", pavimento: str = "TÉRREO",
                 dados_override: List[Tuple] = None, processar_func=None):
        """
        Inicializa gerador
        
        Args:
            arquivos_dxf: Lista de caminhos DXF
            pasta_etiquetas: Caminho da pasta com desenhos PNG (default: {projeto}/etiquetas/)
            obra: Nome da obra
            pavimento: Nome do pavimento
        """
        self.arquivos_dxf = arquivos_dxf
        self.obra = obra
        self.pavimento = pavimento
        
        # Detectar pasta de etiquetas automaticamente
        if pasta_etiquetas is None:
            projeto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.pasta_etiquetas = os.path.join(projeto_root, "etiquetas")
        else:
            self.pasta_etiquetas = pasta_etiquetas
        
        # Processar DXF
        self.dados = []
        self.total_kg = 0
        self.total_barras = 0
        self.arquivo_dxf_base = None
        
        # Customizações de medidas e formas
        self.medidas_customizadas = {}
        self.formas_customizadas = {}
        
        # Função de processamento (padrão: vigas)
        self._processar_func = processar_func or processar_vigas

        if dados_override is not None:
            self.dados = list(dados_override)
            self.total_barras = sum(int(round(d[3])) for d in self.dados) if self.dados else 0
            self.total_kg = sum(float(d[5]) for d in self.dados) if self.dados else 0.0
            if self.arquivos_dxf:
                self.arquivo_dxf_base = os.path.splitext(
                    os.path.basename(self.arquivos_dxf[0])
                )[0]
        else:
            self._processar_dxf()
    
    def _processar_dxf(self):
        """Processa os arquivos DXF usando vigas_motor_v2"""
        try:
            self.dados, self.total_kg, self.total_barras = self._processar_func(self.arquivos_dxf)
            
            # Guardar base do nome do arquivo para localizar desenhos
            if self.arquivos_dxf:
                self.arquivo_dxf_base = os.path.splitext(
                    os.path.basename(self.arquivos_dxf[0])
                )[0]
            
            print(f"[OK] Processados {len(self.dados)} registros de barras")
            print(f"   Total: {self.total_barras} barras, {self.total_kg:.2f} kg")
            
        except Exception as e:
            print(f"[ERRO] Erro ao processar DXF: {e}")
            raise
    
    def gerar_dados_etiqueta(self, idx: int) -> dict:
        """
        Gera dados completos para uma etiqueta
        
        Args:
            idx: Índice da barra (0-based)
        
        Returns:
            Dict com todos os dados para desenhar a etiqueta
        """
        if idx >= len(self.dados):
            return None
        
        viga, pos, bitola, qtde, comp, peso = self.dados[idx]
        
        # ✅ APLICAR CUSTOMIZAÇÕES DO EDITOR (se existirem)
        chave = (viga, pos)
        if hasattr(self, 'medidas_customizadas') and chave in self.medidas_customizadas:
            custom = self.medidas_customizadas[chave]
            if 'bitola' in custom:
                bitola = float(custom['bitola'])
                print(f"[CUSTOM] Aplicando bitola customizada: {bitola}")
            if 'qtde' in custom:
                qtde = int(custom['qtde'])
                print(f"[CUSTOM] Aplicando qtde customizada: {qtde}")
            if 'comp' in custom:
                comp = float(custom['comp'])
                print(f"[CUSTOM] Aplicando comp customizado: {comp}")
            # Recalcular peso com novos valores
            from core.peso import peso_linear_kg_m
            peso_unit = peso_linear_kg_m(bitola)
            peso = peso_unit * comp * qtde
            print(f"[CUSTOM] Peso recalculado: {peso:.2f} kg")
        
        # Calcular número OS agrupado por viga (não global)
        # Contar quantas etiquetas da mesma viga existem ANTES desta
        viga_index = 0
        for i in range(idx):
            if self.dados[i][0] == viga:  # Comparar viga
                viga_index += 1
        
        # Contar total de etiquetas para ESTA viga
        viga_total = sum(1 for d in self.dados if d[0] == viga)
        
        # Formatar OS: "N-T" onde N é índice na viga, T é total de vigas
        os_num = f"{viga_index + 1}-{viga_total}"
        
        codigo_id = gerar_codigo_identificador(
            obra=self.obra,
            os_num=os_num,
            elemento=viga,
            pos=pos,
            bitola=bitola,
            comp=comp
        )
        
        # Gerar código de barras (PASSO 5: alta resolução para térmicas)
        try:
            from core.etiquetas_layout_config import mm_to_px, DPI_PADRAO
            # Barcode em alta resolução: 80mm x 15mm @ 300 DPI
            barcode_w = mm_to_px(80, DPI_PADRAO)
            barcode_h = mm_to_px(15, DPI_PADRAO)
            barcode_w_int, barcode_h_int = to_int(barcode_w, barcode_h)
            barcode_img = gerar_codigo_barras_imagem(codigo_id, largura_px=barcode_w_int, altura_px=barcode_h_int)
            print(f"[BARCODE] Gerado {barcode_w_int}x{barcode_h_int}px (alta resolução)")
        except Exception as e:
            print(f"[BARCODE] Erro ao gerar barcode: {e}")
            barcode_img = None
        
        # Localizar desenho técnico ou extrair do DXF
        caminho_desenho = None
        if self.arquivo_dxf_base and os.path.exists(self.pasta_etiquetas):
            caminho_desenho = localizar_desenho_barra(
                self.pasta_etiquetas,
                self.arquivo_dxf_base,
                viga,
                pos,
                bitola,
                qtde,
                comp * 100  # converter m para cm
            )
        
        # Obter medidas e formas customizadas
        medidas_custom = self.medidas_customizadas.get((viga, pos), {})
        forma_custom = self.formas_customizadas.get((viga, pos), "Reta")
        
        return {
            'indice': idx,
            'viga': viga,
            'pos': pos,
            'bitola': bitola,
            'qtde': qtde,
            'comp': comp,
            'peso': peso,
            'os_num': os_num,
            'codigo_id': codigo_id,
            'barcode_img': barcode_img,
            'caminho_desenho': caminho_desenho,
            'obra': self.obra,
            'pavimento': self.pavimento,
            'total_etiquetas': len(self.dados),
            'medidas_customizadas': medidas_custom,
            'forma_customizada': forma_custom
        }
    
    def listar_todas(self) -> List[dict]:
        """Retorna lista com dados de todas as etiquetas"""
        return [self.gerar_dados_etiqueta(i) for i in range(len(self.dados))]
    
    def gerar_e_salvar_etiquetas_png(self, dpi_x=300, dpi_y=300) -> List[str]:
        """
        Gera e salva as etiquetas completas em PNG na pasta_etiquetas
        Retorna lista com caminhos dos PNGs gerados
        """

        def mm_to_px(mm, dpi):
            return int((mm / 25.4) * dpi)

        caminhos_salvos = []

        for idx in range(len(self.dados)):
            try:
                dados = self.gerar_dados_etiqueta(idx)
                if not dados:
                    continue

                # Alias de dados
                viga = dados['viga']
                pos = dados['pos']
                bitola = dados['bitola']
                qtde = dados['qtde']
                comp = dados['comp']  # metros
                peso = dados['peso']
                os_num = dados['os_num']
                obra = dados['obra']
                pavimento = dados.get('pavimento', self.pavimento)
                codigo_id = dados.get('codigo_id', '')
                barcode_img = dados.get('barcode_img')
                caminho_desenho = dados.get('caminho_desenho')

                comp_cm = int(round(comp * 100))

                # Dimensões principais e canvas
                label_w = int(round(mm_to_px(100, dpi_x)))
                label_h = int(round(mm_to_px(150, dpi_y)))
                img = Image.new("RGB", (label_w, label_h), "white")
                draw = ImageDraw.Draw(img)

                # Fontes (aumentadas para melhor leitura)
                scale = dpi_x / 96.0
                try:
                    f_tiny = ImageFont.truetype("arial.ttf", int(16 * scale))
                    f_small = ImageFont.truetype("arial.ttf", int(20 * scale))
                    f_med = ImageFont.truetype("arial.ttf", int(26 * scale))
                    f_large = ImageFont.truetype("arial.ttf", int(32 * scale))
                    f_xlarge = ImageFont.truetype("arial.ttf", int(40 * scale))
                except Exception:
                    f_tiny = f_small = f_med = f_large = f_xlarge = ImageFont.load_default()

                # Layout base
                margin = int(round(mm_to_px(3, dpi_x)))
                faixa_larg = int(round(mm_to_px(10, dpi_x)))
                altura_topo = int(round(mm_to_px(92, dpi_y)))
                altura_picote = int(round(mm_to_px(18, dpi_y)))
                espaco_picote = int(round(mm_to_px(2, dpi_y)))

                # Borda externa
                draw.rectangle([0, 0, label_w - 1, label_h - 1], outline="#ff6f00", width=int(round(3 * scale)))

                # Faixa vertical (lado direito)
                faixa_x1 = int(round(label_w - faixa_larg - margin))
                faixa_x2 = int(round(label_w - margin))
                draw.rectangle([faixa_x1, margin, faixa_x2, altura_topo], fill="#ff8c00", outline="black", width=1)
                try:
                    temp_img = Image.new("RGBA", (int(round(mm_to_px(10, dpi_x))), int(round(mm_to_px(65, dpi_y)))), (0, 0, 0, 0))
                    temp_draw = ImageDraw.Draw(temp_img)
                    temp_draw.text((temp_img.width // 2, temp_img.height // 2), obra, font=f_small, fill="black", anchor="mm")
                    temp_img = temp_img.rotate(90, expand=True)
                    img.paste(temp_img, (faixa_x1 + (faixa_larg - temp_img.width) // 2, margin + mm_to_px(12, dpi_y)), temp_img)
                except Exception:
                    pass

                # Bloco OS com fundo amarelo
                os_w = int(round(mm_to_px(22, dpi_x)))
                os_h = int(round(mm_to_px(26, dpi_y)))
                os_x1 = int(round(faixa_x1 - os_w - margin))
                os_y1 = margin
                os_x2 = os_x1 + os_w
                os_y2 = os_y1 + os_h
                draw.rectangle([os_x1, os_y1, os_x2, os_y2], fill="#ffff00", outline="black", width=3)
                draw.text((os_x1 + int(round(mm_to_px(2, dpi_x))), os_y1 + int(round(mm_to_px(1.5, dpi_y)))), "OS", font=f_small, fill="black")
                draw.text(((os_x1 + os_x2) // 2, os_y1 + os_h // 2 + int(round(mm_to_px(1, dpi_y)))), os_num, font=f_large, fill="black", anchor="mm")

                # Cabeçalho à esquerda
                x_label = margin + int(round(mm_to_px(2, dpi_x)))
                x_value = x_label + int(round(mm_to_px(28, dpi_x)))

                # Linha de identificação grande (impressão/preview)
                info_y = margin + int(round(mm_to_px(1.5, dpi_y)))
                draw.text((x_label, info_y), f"E {idx+1} | OS: {viga}/{pos}", font=f_med, fill="black", anchor="lm")
                info_y2 = info_y + int(round(mm_to_px(6, dpi_y)))
                draw.text((x_label, info_y2), f"Ø {bitola:.1f}mm | Q: {qtde} | C: {comp:.2f}m", font=f_small, fill="black", anchor="lm")
                info_y3 = info_y2 + int(round(mm_to_px(6, dpi_y)))
                draw.text((x_label, info_y3), f"P: {peso:.2f}kg", font=f_small, fill="black", anchor="lm")

                y_line = info_y3 + int(round(mm_to_px(6.5, dpi_y)))
                espacamento_mm = 6.5
                pxmm = dpi_x / 25.4
                def mm(v): return int(round(v * pxmm))
                campos = [
                    ("Sigla/Obra", obra),
                    ("Desenho", self.arquivo_dxf_base or ""),
                    ("Pavimento", pavimento),
                    ("Elemento", viga),
                ]
                for label, valor in campos:
                    draw.text((x_label, y_line), label + ":", font=f_small, fill="black", anchor="lm")
                    draw.text((x_value, y_line), str(valor), font=f_small, fill="black", anchor="lm")
                    y_line += mm(espacamento_mm)

                # POS destacado
                pos_x = int(round(os_x1 - mm_to_px(22, dpi_x)))
                pos_y = margin + int(round(mm_to_px(18, dpi_y)))
                draw.text((pos_x, pos_y - int(round(mm_to_px(3, dpi_y)))), "POS", font=f_tiny, fill="black", anchor="mm")
                draw.text((pos_x, pos_y + int(round(mm_to_px(6, dpi_y)))), pos, font=f_xlarge, fill="black", anchor="mm")

                # Tabela principal
                tab_y = margin + int(round(mm_to_px(32, dpi_y)))
                tab_h = int(round(mm_to_px(20, dpi_y)))
                col_widths = [int(round(mm_to_px(16, dpi_x))), int(round(mm_to_px(34, dpi_x))), int(round(mm_to_px(22, dpi_x))), int(round(mm_to_px(18, dpi_x)))]
                tab_w = sum(col_widths)
                tab_x1 = margin + int(round(mm_to_px(4, dpi_x)))
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
                for idx_col, (h, v, w) in enumerate(zip(headers, values, col_widths)):
                    draw.text((x_col + w // 2, tab_y + int(round(mm_to_px(3, dpi_y)))), h, font=f_small, fill="black", anchor="mm")
                    # Peso em vermelho, outros em azul
                    cor_valor = "#d32f2f" if idx_col == 2 else "black"
                    draw.text((x_col + w // 2, tab_y + tab_h // 2 + int(round(mm_to_px(3, dpi_y)))), v, font=f_small, fill=cor_valor, anchor="mm")
                    x_col += w

                # Área do desenho técnico
                draw_y = tab_y + tab_h + int(round(mm_to_px(6, dpi_y)))
                draw_h = int(round(mm_to_px(38, dpi_y)))
                area_x1 = margin + int(round(mm_to_px(8, dpi_x)))
                area_x2 = int(round(faixa_x1 - mm_to_px(5, dpi_x)))
                draw.rectangle([area_x1, draw_y, area_x2, draw_y + draw_h], outline="#c8102e", width=2)

                # Tamanho disponível para renderização
                avail_w = int(round(max(1, (area_x2 - area_x1) - 12)))
                avail_h = int(round(max(1, draw_h - 12)))

                # 1) Preferir PNG localizado
                desenhado = False
                if caminho_desenho and os.path.exists(caminho_desenho) and "placeholder" not in caminho_desenho.lower():
                    try:
                        with Image.open(caminho_desenho) as png_raw:
                            png_rgb = png_raw.convert("RGB")
                            resample = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS
                            # CRÍTICO: usar resize() com tamanho EXATO, não thumbnail() que pode distorcer
                            # Manter proporção: calcular dimensão para caber em avail_w x avail_h
                            aspect = png_rgb.width / png_rgb.height
                            if aspect > (avail_w / avail_h):  # Mais largo que alto
                                new_w = avail_w
                                new_h = int(round(avail_w / aspect))
                            else:
                                new_h = avail_h
                                new_w = int(round(avail_h * aspect))
                            new_w, new_h = to_int(new_w, new_h)
                            png_rgb = png_rgb.resize((new_w, new_h), resample=resample)
                            px, py = to_int(area_x1 + ((area_x2 - area_x1 - png_rgb.width) // 2), draw_y + ((draw_h - png_rgb.height) // 2))
                            img.paste(png_rgb, (px, py))
                            desenhado = True
                    except Exception as e:
                        print(f"❌ Erro ao abrir desenho técnico real: {e}")
                if not desenhado:
                    # Aviso visual: desenho não encontrado
                    draw.rectangle([area_x1, draw_y, area_x2, draw_y + draw_h], outline="red", width=2)
                    cx, cy = to_int(area_x1 + (area_x2 - area_x1) / 2, draw_y + draw_h / 2)
                    try:
                        font_erro = ImageFont.truetype("arial.ttf", 14)
                    except Exception:
                        font_erro = ImageFont.load_default()
                    draw.text((cx, cy), "DESENHO NÃO ENCONTRADO", fill="red", font=font_erro, anchor="mm")

                # 2) Se não houver PNG, extrair diretamente do DXF
                if not desenhado:
                    try:
                        dxf_path = self.arquivos_dxf[0] if self.arquivos_dxf else None
                        if dxf_path:
                            extra = localizar_desenho_viga_no_dxf(dxf_path, viga, pos, largura_px=avail_w, altura_px=avail_h)
                            if extra is not None:
                                px, py = to_int(area_x1 + ((area_x2 - area_x1 - extra.width) // 2), draw_y + ((draw_h - extra.height) // 2))
                                img.paste(extra.convert("RGB"), (px, py))
                                desenhado = True
                    except Exception as e:
                        print(f"[WARN] Falha na extração DXF para {viga}/{pos}: {e}")

                # Página
                page_y, page_x = to_int(draw_y + draw_h + mm_to_px(1.5, dpi_y), (area_x1 + area_x2) // 2)
                draw.text((page_x, page_y), f"Página {idx+1} de {len(self.dados)}", font=f_tiny, fill="black", anchor="mt")

                # Linha de separação
                draw.line([(margin, altura_topo), (label_w - margin, altura_topo)], fill="#cccccc", width=1)

                # Picotes com código de barras amplo
                y_picote, picote_w = to_int(altura_topo + espaco_picote, label_w - 2 * margin)
                for p in range(3):
                    box_top, box_bottom = to_int(y_picote, y_picote + altura_picote)
                    draw.rectangle([margin, box_top, margin + picote_w, box_bottom], outline="#cccccc", width=1)

                    # Código de barras grande
                    if barcode_img:
                        try:
                            barcode_rgb = barcode_img.convert("RGB")
                            avail_w, avail_h = to_int(picote_w - mm_to_px(8, dpi_x), altura_picote - mm_to_px(6, dpi_y))
                            resample = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS
                            # CRÍTICO: usar resize() com tamanho EXATO, mantendo proporção
                            aspect = barcode_rgb.width / barcode_rgb.height
                            if aspect > (avail_w / avail_h):
                                new_w = avail_w
                                new_h = int(round(avail_w / aspect))
                            else:
                                new_h = avail_h
                                new_w = int(round(avail_h * aspect))
                            new_w, new_h = to_int(new_w, new_h)
                            barcode_rgb = barcode_rgb.resize((new_w, new_h), resample=resample)
                            bx, by = to_int(margin + mm_to_px(2, dpi_x), box_top + mm_to_px(1, dpi_y))
                            img.paste(barcode_rgb, (bx, by))
                        except Exception as e:
                            print(f"[WARN] Erro ao desenhar barcode {viga}/{pos}: {e}")

                    # Textos inferiores
                    # PASSO 6: Centralizar legenda do picote com espaçamento adequado
                    texto_picote = f"Elem: {viga}  {pos}   OS {os_num}   Ø {bitola:.2f}"
                    picote_center_x = int(round(margin + picote_w // 2))
                    picote_text_y = int(round(box_bottom - mm_to_px(3, dpi_y)))  # Aumentado espaço do código
                    draw.text((picote_center_x, picote_text_y), texto_picote, font=f_tiny, fill="black", anchor="mm")

                    compr_x = int(round(margin + picote_w - mm_to_px(2, dpi_x)))
                    draw.text((compr_x, int(round(box_top + mm_to_px(2, dpi_y)))), "Compr. Corte", font=f_tiny, fill="black", anchor="rm")
                    draw.text((compr_x, int(round(box_top + mm_to_px(10, dpi_y)))), f"{comp:.3f}", font=f_small, fill="black", anchor="rm")

                    # Linha tracejada vermelha entre picotes
                    if p < 2:
                        y_corte = box_bottom
                        for x in range(margin, margin + picote_w, 10):
                            draw.line([(int(round(x)), int(round(y_corte))), (int(round(x + 5)), int(round(y_corte)))], fill="#c8102e", width=1)

                    y_picote += altura_picote + espaco_picote

                # Salvar PNG
                if not os.path.exists(self.pasta_etiquetas):
                    os.makedirs(self.pasta_etiquetas)

                nome_arquivo = f"ETIQUETA_{viga}_{pos}_b{bitola:.1f}_q{qtde}_c{comp_cm}cm_{idx+1:04d}.png"
                nome_arquivo = re.sub(r'[\\/:*?"<>|]', '-', nome_arquivo)
                caminho_saida = os.path.join(self.pasta_etiquetas, nome_arquivo)

                # Salvar com metadado de DPI para manter 100x150mm nos visualizadores/impressoras
                try:
                    img.save(caminho_saida, dpi=(dpi_x, dpi_y))
                except Exception:
                    img.save(caminho_saida)
                caminhos_salvos.append(caminho_saida)
                print(f"[OK] Etiqueta {idx+1}/{len(self.dados)} salva: {nome_arquivo}")

            except Exception as e:
                print(f"[ERRO] Erro ao gerar etiqueta {idx+1}: {e}")
                import traceback
                traceback.print_exc()

        print(f"\n[OK] Total de etiquetas geradas: {len(caminhos_salvos)}")
        return caminhos_salvos

    @staticmethod
    def listar_impressoras_disponiveis():
        """
        Lista todas as impressoras disponíveis no Windows
        
        Returns:
            Lista de nomes de impressoras
        """
        try:
            import win32print
            impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            return impressoras if impressoras else ["Argox OS-214 Plus"]
        except ImportError:
            # Fallback: usar wmic se win32print não disponível
            try:
                import subprocess
                result = subprocess.run(['wmic', 'printer', 'get', 'name'], 
                                      capture_output=True, text=True, check=True)
                linhas = result.stdout.strip().split('\n')[1:]  # Pular cabeçalho
                impressoras = [linha.strip() for linha in linhas if linha.strip()]
                return impressoras if impressoras else ["Argox OS-214 Plus"]
            except Exception as e:
                print(f"[ERRO] Não foi possível listar impressoras: {e}")
                return ["Argox OS-214 Plus"]  # Default
    
    @staticmethod
    def obter_impressora_padrao():
        """
        Obtém a impressora padrão do Windows
        
        Returns:
            Nome da impressora padrão
        """
        try:
            import win32print
            return win32print.GetDefaultPrinter()
        except:
            try:
                import subprocess
                result = subprocess.run(['wmic', 'printer', 'where', 'default=TRUE', 'get', 'name'],
                                      capture_output=True, text=True, check=True)
                linhas = result.stdout.strip().split('\n')
                if len(linhas) > 1:
                    return linhas[1].strip()
            except Exception:
                pass
        impressoras = GeradorEtiquetasDinamico.listar_impressoras_disponiveis()
        if impressoras:
            return impressoras[0]
        return "Argox OS-214 Plus"  # Fallback

    def gerar_e_imprimir_direto(self, impressora: str = None, dpi_x=300, dpi_y=300) -> bool:
        """
        Gera etiquetas COMPLETAS (com desenho, barcode, etc) e imprime DIRETO
        
        Args:
            impressora: Nome da impressora (None = usar padrão do sistema)
            dpi_x: DPI horizontal (300)
            dpi_y: DPI vertical (300)
            
        Returns:
            True se sucesso, False caso contrário
        """
        if impressora is None:
            impressora = self.obter_impressora_padrao()
            print(f"[INFO] Usando impressora padrão: {impressora}")
        else:
            print(f"[INFO] Usando impressora selecionada: {impressora}")
        
        import os
        
        print(f"\n[IMPRESSÃO DIRETA] Gerando {len(self.dados)} etiqueta(s) COMPLETAS...")
        print(f"[IMPRESSÃO DIRETA] Impressora: {impressora}")
        
        # Criar pasta se não existir
        if not os.path.exists(self.pasta_etiquetas):
            os.makedirs(self.pasta_etiquetas)
        
        try:
            # Usar o método completo que já gera tudo (desenho, barcode, etc)
            print("[DEBUG] Gerando etiquetas completas com gerar_e_salvar_etiquetas_png...")
            arquivos_temp = self.gerar_e_salvar_etiquetas_png(dpi_x=dpi_x, dpi_y=dpi_y)
            
            if not arquivos_temp:
                print("[ERRO] Nenhuma etiqueta foi gerada!")
                return False

            print(f"[DEBUG] {len(arquivos_temp)} etiqueta(s) gerada(s)")
            print(f"[DEBUG] Primeira: {arquivos_temp[0]}")

            # IMPRIMIR
            print(f"\n[IMPRIMIR] Enviando {len(arquivos_temp)} para '{impressora}'...")

            original_printer = None
            win32_ok = False
            try:
                import win32print
                original_printer = win32print.GetDefaultPrinter()
                win32print.SetDefaultPrinter(impressora)
                win32_ok = True
                print(f"[DEBUG] Impressora padrão mudada para: {impressora}")
            except Exception as e:
                print(f"[AVISO] win32print falhou: {e}")

            try:
                for temp_file in arquivos_temp:
                    try:
                        import os as os_module
                        os_module.startfile(temp_file, "print")
                        print(f"[OK] Enviado: {os.path.basename(temp_file)}")
                    except Exception as e:
                        print(f"[ERRO] {temp_file}: {e}")

                print(f"[SUCESSO] {len(arquivos_temp)} etiqueta(s) enviada(s)!")
                return True
            finally:
                if win32_ok and original_printer:
                    try:
                        import win32print
                        win32print.SetDefaultPrinter(original_printer)
                        print(f"[DEBUG] Impressora padrão restaurada: {original_printer}")
                    except Exception as e:
                        print(f"[AVISO] Erro ao restaurar impressora: {e}")

        except Exception as e:
            print(f"[ERRO] Erro geral: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    # Teste
    print("=" * 70)
    print("TESTE DE GERADOR DINÂMICO DE ETIQUETAS")
    print("=" * 70)
    
    arquivo_teste = r'c:\EngenhariaPlanPro\dxf\#vigas t1-069.DXF'
    
    gerador = GeradorEtiquetasDinamico([arquivo_teste])
    
    print(f"\n📋 Total de etiquetas a gerar: {len(gerador.dados)}\n")
    
    for i in range(min(3, len(gerador.dados))):
        dados = gerador.gerar_dados_etiqueta(i)
        print(f"Etiqueta {i+1}:")
        print(f"  Viga: {dados['viga']} | Pos: {dados['pos']}")
        print(f"  OS: {dados['os_num']} | Código: {dados['codigo_id']}")
        print(f"  Codigo de barras: {'SIM' if dados['barcode_img'] else 'NAO'}")
        print(f"  Desenho: {'SIM' if dados['caminho_desenho'] else 'NAO encontrado'}")
        print()
    
    print("=" * 70)

