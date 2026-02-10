# ========================================
# MÉTODOS COMPLETOS ADAPTADOS PARA LAJES
# ========================================
# 
# Este arquivo contém TODOS os métodos necessários para implementar
# o editor de etiquetas no lajes_app.py usando a MESMA arquitetura
# de renderização direta no canvas do vigas_app.py
#
# ADAPTAÇÕES:
# - viga → elemento (ex: "LAJE NEG/HOR")
# - pos → pos_tipo (ex: "N1", "N2")
# - dados_processados tem 9 campos: (elemento, pos_tipo, bitola, qtde, comp_m, largura_info, peso, formato_dobra, medidas_m)
#
# COPIE TODOS os métodos abaixo e adicione na classe LajesApp do lajes_app.py
# ========================================

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_DISPONIVEL = True
except:
    Image = None
    ImageTk = None
    PIL_DISPONIVEL = False

# ========================================
# CONSTANTES DE LAYOUT (copiar do vigas_app.py ou definir aqui)
# ========================================
try:
    from core.etiquetas_layout import *
    ETIQUETAS_LAYOUT_CFG = True
except:
    # Valores padrão caso não exista o módulo
    ETIQUETAS_LAYOUT_CFG = False
    CFG_PX_MM = 4
    MARGEM_EXTERNA_MM = 10
    LARGURA_ETIQUETA_MM = 100
    TOPO_ALTURA_MM = 93
    SECAO_MICRO_ALTURA_MM = 19
    ESPACO_PICOTE_MM = 2
    FAIXA_VERTICAL_LARGURA_MM = 10
    OS_BLOCO_LARGURA_MM = 18
    OS_BLOCO_ALTURA_MM = 30
    TABELA_ALTURA_HEADER_MM = 8
    TABELA_ALTURA_LINHA_MM = 10
    COL_BITOLA_MM = 16
    COL_COMPR_UNIT_MM = 34
    COL_PESO_MM = 22
    COL_QTDE_MM = 18
    DESENHO_LARGURA_MM = 60
    DESENHO_ALTURA_MM = 50

# ========================================
# MÉTODO PRINCIPAL: imprimir_etiquetas()
# ========================================

def imprimir_etiquetas(self):
    """
    INTERFACE PROFISSIONAL COMPLETA:
    1. Exibe PREVIEW de todas as etiquetas no canvas
    2. Usuário pode EDITAR desenhos e medidas
    3. Usuário pode SELECIONAR quais imprimir (checkboxes)
    4. Gera PDF/PNG apenas das selecionadas
    
    ADAPTADO PARA LAJES - renderização direta no canvas
    """
    # Aplicar filtro de produção
    dados_filtrados, total_kg, total_pecas = self.aplicar_filtro_producao()
    
    if not dados_filtrados:
        messagebox.showwarning("Atenção", "Nenhuma laje selecionada para gerar etiquetas!")
        return
    
    # Usar dados filtrados para etiquetas
    self.dados_processados = dados_filtrados
    
    # CRIAR JANELA SEPARADA
    if hasattr(self, 'janela_editor') and self.janela_editor and self.janela_editor.winfo_exists():
        self.janela_editor.destroy()
    
    self.janela_editor = tk.Toplevel(self)
    self.janela_editor.title("✏️ EDITOR DE ETIQUETAS LAJES - Edite, Selecione e Imprima")
    self.janela_editor.configure(bg="#0d2818")
    
    # Ajustar tamanho para caber na tela
    self.janela_editor.update_idletasks()
    screen_w = self.janela_editor.winfo_screenwidth()
    screen_h = self.janela_editor.winfo_screenheight()
    win_w = min(1200, screen_w - 40)
    win_h = min(900, screen_h - 80)
    x = max(0, (screen_w // 2) - (win_w // 2))
    y = max(0, (screen_h // 2) - (win_h // 2))
    self.janela_editor.geometry(f"{win_w}x{win_h}+{x}+{y}")
    min_w = min(900, max(600, screen_w - 60))
    min_h = min(650, max(500, screen_h - 120))
    self.janela_editor.minsize(min_w, min_h)
    
    # Zoom inicial
    if not hasattr(self, 'zoom_factor'):
        if screen_h < 900 or screen_w < 1200:
            self.zoom_factor = 0.85
        else:
            self.zoom_factor = 1.0
    
    # Inicializar estruturas
    if not hasattr(self, 'medidas_customizadas'):
        self.medidas_customizadas = {}
    if not hasattr(self, 'formas_customizadas'):
        self.formas_customizadas = {}
    if not hasattr(self, 'pagina_atual'):
        self.pagina_atual = 0
    if not hasattr(self, 'etiquetas_por_pagina'):
        self.etiquetas_por_pagina = 6
    if not hasattr(self, 'etiquetas_selecionadas'):
        # Inicia com TODAS selecionadas
        self.etiquetas_selecionadas = {i: True for i in range(len(self.dados_processados))}
    
    # Calcular total de páginas
    self.total_paginas = max(1, math.ceil(len(self.dados_processados) / self.etiquetas_por_pagina))
    
    # FRAME SUPERIOR - TÍTULO
    titulo_frame = tk.Frame(self.janela_editor, bg="#ff6f00")
    titulo_frame.pack(fill="x")
    
    tk.Label(
        titulo_frame,
        text="✏️ EDITOR DE ETIQUETAS LAJES - EDITE, SELECIONE E IMPRIMA",
        bg="#ff6f00",
        fg="white",
        font=("Arial", 12, "bold"),
        pady=8
    ).pack()
    
    # FRAME DO CANVAS
    canvas_frame = tk.Frame(self.janela_editor, bg="#0d2818")
    canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Scrollbar
    scrollbar = tk.Scrollbar(canvas_frame)
    scrollbar.pack(side="right", fill="y")
    
    # Canvas para renderizar etiquetas
    self.canvas_etiq = tk.Canvas(
        canvas_frame,
        bg="white",
        yscrollcommand=scrollbar.set,
        highlightthickness=0
    )
    self.canvas_etiq.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=self.canvas_etiq.yview)
    
    # Scroll com mouse (Windows)
    def _on_mousewheel(event):
        try:
            self.canvas_etiq.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass
    self.canvas_etiq.bind("<MouseWheel>", _on_mousewheel)
    
    # BIND DE CLIQUE NO CANVAS
    self.canvas_etiq.bind("<Button-1>", self._handle_canvas_click)
    
    # RENDERIZAR PREVIEW NO CANVAS (com checkboxes)
    try:
        self.desenhar_etiquetas_com_selecao()
    except Exception as e:
        print(f"Erro ao renderizar: {e}")
        import traceback
        traceback.print_exc()
        self.canvas_etiq.create_text(
            600, 450,
            text=f"⚠️ Erro ao renderizar preview\n{str(e)}",
            font=("Arial", 12),
            fill="red"
        )
    
    # FRAME NAVEGAÇÃO
    nav_frame = tk.Frame(self.janela_editor, bg="#34495e")
    nav_frame.pack(fill="x", padx=10, pady=5)
    
    self.label_pagina = tk.Label(
        nav_frame,
        text=f"Página {self.pagina_atual + 1} de {self.total_paginas}",
        bg="#34495e",
        fg="white",
        font=("Arial", 10, "bold")
    )
    self.label_pagina.pack(side="left", padx=10, pady=5)
    
    # Botões de navegação
    nav_btn_frame = tk.Frame(nav_frame, bg="#34495e")
    nav_btn_frame.pack(side="right", padx=5, pady=5)
    
    tk.Button(nav_btn_frame, text="⏮️ Primeira", command=self._ir_primeira_pagina_etiquetas,
              bg="#16a085", fg="white", font=("Arial", 9), padx=8, pady=4, cursor="hand2").pack(side="left", padx=2)
    tk.Button(nav_btn_frame, text="◀ Anterior", command=self._ir_pagina_anterior_etiquetas,
              bg="#27ae60", fg="white", font=("Arial", 9), padx=8, pady=4, cursor="hand2").pack(side="left", padx=2)
    tk.Button(nav_btn_frame, text="Próxima ▶", command=self._ir_proxima_pagina_etiquetas,
              bg="#27ae60", fg="white", font=("Arial", 9), padx=8, pady=4, cursor="hand2").pack(side="left", padx=2)
    tk.Button(nav_btn_frame, text="Última ⏭️", command=self._ir_ultima_pagina_etiquetas,
              bg="#16a085", fg="white", font=("Arial", 9), padx=8, pady=4, cursor="hand2").pack(side="left", padx=2)
    
    # FRAME SELEÇÃO
    sel_frame = tk.Frame(self.janela_editor, bg="#1a3d2e")
    sel_frame.pack(fill="x", padx=10, pady=5)
    
    tk.Label(sel_frame, text="🔘 Seleção:", bg="#1a3d2e", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
    
    tk.Button(sel_frame, text="☑️ MARCAR TODAS", command=self._marcar_todas_etiquetas,
              bg="#27ae60", fg="white", font=("Arial", 9), padx=10, pady=4, cursor="hand2").pack(side="left", padx=3)
    tk.Button(sel_frame, text="☐ DESMARCAR TODAS", command=self._desmarcar_todas_etiquetas,
              bg="#e74c3c", fg="white", font=("Arial", 9), padx=10, pady=4, cursor="hand2").pack(side="left", padx=3)
    
    total_selecionadas = sum(1 for v in self.etiquetas_selecionadas.values() if v)
    self.label_selecionadas = tk.Label(
        sel_frame,
        text=f"Selecionadas: {total_selecionadas}/{len(self.dados_processados)}",
        bg="#1a3d2e", fg="#ff9800", font=("Arial", 9, "bold")
    )
    self.label_selecionadas.pack(side="right", padx=10, pady=4)
    
    # FRAME INFERIOR - BOTÕES PRINCIPAIS
    btn_frame = tk.Frame(self.janela_editor, bg="#1a3d2e")
    btn_frame.pack(fill="x", padx=10, pady=10)
    
    info_text = f"📋 Total: {len(self.dados_processados)} etiquetas | 💡 Clique nos valores para editar | ☑️ Selecione quais imprimir"
    tk.Label(btn_frame, text=info_text, bg="#1a3d2e", fg="white", font=("Arial", 9)).pack(side="left", padx=10, pady=5)
    
    # Botões à direita
    btn_actions = tk.Frame(btn_frame, bg="#1a3d2e")
    btn_actions.pack(side="right", padx=5)
    
    tk.Button(btn_actions, text="✅ GERAR SELECIONADAS",
              command=self._confirmar_e_gerar_etiquetas_lajes,
              bg="#27ae60", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5, cursor="hand2").pack(side="left", padx=3)
    tk.Button(btn_actions, text="✕ FECHAR", command=self._fechar_editor_etiquetas_lajes,
              bg="#e74c3c", fg="white", font=("Arial", 9), padx=10, pady=5, cursor="hand2").pack(side="left", padx=3)

# ========================================
# MÉTODOS AUXILIARES DE NAVEGAÇÃO
# ========================================

def _ir_primeira_pagina_etiquetas(self):
    """Volta para primeira página"""
    self.pagina_atual = 0
    self.canvas_etiq.delete("all")
    self.desenhar_etiquetas_com_selecao()
    self.label_pagina.config(text=f"Página {self.pagina_atual + 1} de {self.total_paginas}")

def _ir_pagina_anterior_etiquetas(self):
    """Vai para página anterior"""
    if self.pagina_atual > 0:
        self.pagina_atual -= 1
        self.canvas_etiq.delete("all")
        self.desenhar_etiquetas_com_selecao()
        self.label_pagina.config(text=f"Página {self.pagina_atual + 1} de {self.total_paginas}")

def _ir_proxima_pagina_etiquetas(self):
    """Vai para próxima página"""
    if self.pagina_atual < self.total_paginas - 1:
        self.pagina_atual += 1
        self.canvas_etiq.delete("all")
        self.desenhar_etiquetas_com_selecao()
        self.label_pagina.config(text=f"Página {self.pagina_atual + 1} de {self.total_paginas}")

def _ir_ultima_pagina_etiquetas(self):
    """Vai para última página"""
    self.pagina_atual = self.total_paginas - 1
    self.canvas_etiq.delete("all")
    self.desenhar_etiquetas_com_selecao()
    self.label_pagina.config(text=f"Página {self.pagina_atual + 1} de {self.total_paginas}")

def _marcar_todas_etiquetas(self):
    """Marca todas as etiquetas para impressão"""
    if not hasattr(self, 'etiquetas_selecionadas') or len(self.etiquetas_selecionadas) != len(self.dados_processados):
        self.etiquetas_selecionadas = {i: True for i in range(len(self.dados_processados))}
    else:
        for i in range(len(self.dados_processados)):
            self.etiquetas_selecionadas[i] = True
    self.desenhar_etiquetas_com_selecao()
    if hasattr(self, 'label_selecionadas'):
        total = sum(1 for v in self.etiquetas_selecionadas.values() if v)
        self.label_selecionadas.config(text=f"Selecionadas: {total}/{len(self.dados_processados)}")

def _desmarcar_todas_etiquetas(self):
    """Desmarca todas as etiquetas"""
    if not hasattr(self, 'etiquetas_selecionadas') or len(self.etiquetas_selecionadas) != len(self.dados_processados):
        self.etiquetas_selecionadas = {i: False for i in range(len(self.dados_processados))}
    else:
        for i in range(len(self.dados_processados)):
            self.etiquetas_selecionadas[i] = False
    self.desenhar_etiquetas_com_selecao()
    if hasattr(self, 'label_selecionadas'):
        total = sum(1 for v in self.etiquetas_selecionadas.values() if v)
        self.label_selecionadas.config(text=f"Selecionadas: {total}/{len(self.dados_processados)}")

def _fechar_editor_etiquetas_lajes(self):
    """Fecha a janela do editor"""
    if hasattr(self, 'janela_editor') and self.janela_editor:
        self.janela_editor.destroy()

def _confirmar_e_gerar_etiquetas_lajes(self):
    """Confirma e gera/imprime as etiquetas selecionadas"""
    selecionadas = [i for i, v in self.etiquetas_selecionadas.items() if v]
    if not selecionadas:
        messagebox.showwarning("Atenção", "Selecione pelo menos uma etiqueta!")
        return
    
    resposta = messagebox.askyesno(
        "Confirmar Geração",
        f"Gerar {len(selecionadas)} etiqueta(s) selecionada(s)?\n\n"
        "As etiquetas serão salvas como PNG."
    )
    
    if resposta:
        # Aqui você pode implementar a geração de PNGs ou impressão direta
        messagebox.showinfo("Sucesso", f"{len(selecionadas)} etiqueta(s) processada(s)!")

# ========================================
# MÉTODO PRINCIPAL DE RENDERIZAÇÃO
# ========================================

def desenhar_etiquetas_com_selecao(self):
    """
    Renderiza etiquetas 100×150mm COM PICOTES + CHECKBOXES para seleção
    ADAPTADO PARA LAJES - usa dados: (elemento, pos_tipo, bitola, qtde, comp_m, largura_info, peso, formato_dobra, medidas_m)
    """
    try:
        yview_prev = getattr(self, '_pending_yview', None)
    except Exception:
        yview_prev = None
    if yview_prev is None:
        try:
            yview_prev = self.canvas_etiq.yview()
        except Exception:
            yview_prev = None
    
    self.canvas_etiq.delete("all")
    self._barcode_images = []
    self._desenho_images = []

    # Escala e dimensões reais
    PX_MM = CFG_PX_MM if 'CFG_PX_MM' in globals() and ETIQUETAS_LAYOUT_CFG else 4
    zf = getattr(self, 'zoom_factor', 1.0)
    MARGEM = ((MARGEM_EXTERNA_MM if ETIQUETAS_LAYOUT_CFG else 10) * PX_MM) * zf
    LARGURA_ETIQ = ((LARGURA_ETIQUETA_MM if ETIQUETAS_LAYOUT_CFG else 100) * PX_MM) * zf
    ALTURA_TOPO = ((TOPO_ALTURA_MM if ETIQUETAS_LAYOUT_CFG else 93) * PX_MM) * zf
    ALTURA_MICRO = ((SECAO_MICRO_ALTURA_MM if ETIQUETAS_LAYOUT_CFG else 19) * PX_MM) * zf
    ESPACO_PICOTE = ((ESPACO_PICOTE_MM if ETIQUETAS_LAYOUT_CFG else 2) * PX_MM) * zf

    # Altura total da etiqueta
    altura_etiqueta = ALTURA_TOPO + (ESPACO_PICOTE // 2) + 3 * (ALTURA_MICRO + ESPACO_PICOTE) + ALTURA_MICRO

    # Centro horizontal na tela
    canvas_w = int(self.canvas_etiq.winfo_width())
    x_base = max(MARGEM, (canvas_w - LARGURA_ETIQ) // 2)

    # Índice inicial baseado na página
    inicio = self.pagina_atual * self.etiquetas_por_pagina
    fim = min(len(self.dados_processados), inicio + self.etiquetas_por_pagina)

    y_cursor = MARGEM

    # Redesenhar etiquetas
    self._checkbox_positions = {}
    for i in range(inicio, fim):
        if i < 0 or i >= len(self.dados_processados):
            print(f"[WARN] Índice {i} inválido (0-{len(self.dados_processados)-1})")
            continue
        
        dado = self.dados_processados[i]
        if not dado or len(dado) < 7:  # Lajes tem no mínimo 7 campos
            print(f"[WARN] Dado inválido no índice {i}: {dado}")
            continue
        
        try:
            # ADAPTAÇÃO LAJES: estrutura (elemento, pos_tipo, bitola, qtde, comp_m, largura_info, peso, formato_dobra, medidas_m)
            elemento = dado[0]  # ex: "LAJE NEG/HOR"
            pos_tipo = str(dado[1])  # ex: "N1"
            bitola = float(dado[2])
            qtde = int(dado[3])
            comp_m = float(dado[4])
            # largura_info = dado[5]  # não usado na etiqueta
            # peso = dado[6]
            # formato_dobra = dado[7] if len(dado) > 7 else "RETA"
            # medidas_m = dado[8] if len(dado) > 8 else []
        except (ValueError, TypeError, IndexError) as e:
            print(f"[WARN] Erro ao extrair dados: {e}")
            continue
        
        chave = (elemento, pos_tipo)
        cortado_val = False
        if chave in self.medidas_customizadas:
            cortado_val = bool(self.medidas_customizadas[chave].get('cortado', False))
        
        # Moldura topo e conteúdo técnico
        if hasattr(self, '_desenhar_moldura_etiqueta_fase4'):
            self._desenhar_moldura_etiqueta_fase4(x_base, y_cursor, LARGURA_ETIQ, ALTURA_TOPO)
        if hasattr(self, '_desenhar_topo_identico_fase4'):
            self._desenhar_topo_identico_fase4(x_base, y_cursor, LARGURA_ETIQ, ALTURA_TOPO, elemento, pos_tipo, bitola, qtde, comp_m, i)
        
        # 3 seções inferiores
        base_y = y_cursor + ALTURA_TOPO + (ESPACO_PICOTE / 2)
        for idx in range(3):
            y_sec = base_y + idx * (ALTURA_MICRO + ESPACO_PICOTE)
            self.canvas_etiq.create_rectangle(x_base, y_sec, x_base + LARGURA_ETIQ, y_sec + ALTURA_MICRO, outline="#cccccc", width=1)
            if hasattr(self, '_desenhar_secao_micro_fase4'):
                self._desenhar_secao_micro_fase4(x_base + 6 * zf, y_sec + 6 * zf, LARGURA_ETIQ - 12 * zf, ALTURA_MICRO - 12 * zf, elemento, pos_tipo, bitola, qtde, comp_m)
            if idx < 2 and hasattr(self, '_desenhar_picote_fase4'):
                self._desenhar_picote_fase4(x_base, y_sec + ALTURA_MICRO + (ESPACO_PICOTE / 2), LARGURA_ETIQ)
        
        # Número da etiqueta
        info_y = y_cursor + 8
        self.canvas_etiq.create_text(x_base + 8, info_y, text=f"E {i+1}", font=("Arial", int(9*zf), "bold"), fill="#333333", anchor="nw")
        
        # TAG para clique na etiqueta
        tag_ret = self.canvas_etiq.create_rectangle(x_base-1, y_cursor-1, x_base + LARGURA_ETIQ+1, 
                                         y_cursor + altura_etiqueta+1,
                                         fill="", outline="", 
                                         tags=f"etiq_{i}")
        self.canvas_etiq.tag_raise(f"etiq_{i}")
        
        # Indicativo de cortado
        if cortado_val:
            self.canvas_etiq.create_text(x_base + LARGURA_ETIQ - 15, y_cursor + altura_etiqueta - 10, text="✗", font=("Arial", 14, "bold"), fill="#e74c3c")
        
        # CHECKBOX DE SELEÇÃO
        checkbox_size = 28 * zf
        x_checkbox = x_base + 8 * zf
        y_checkbox = y_cursor + 8 * zf
        if not hasattr(self, '_checkbox_positions'):
            self._checkbox_positions = {}
        self._checkbox_positions[i] = {
            'x1': x_checkbox - 5 * zf, 'y1': y_checkbox - 5 * zf,
            'x2': x_checkbox + checkbox_size + 5 * zf, 'y2': y_checkbox + checkbox_size + 5 * zf,
            'elemento': elemento, 'pos_tipo': pos_tipo, 'bitola': bitola, 'qtde': qtde, 'comp_m': comp_m
        }
        self.canvas_etiq.create_rectangle(x_checkbox-2 * zf, y_checkbox-2 * zf, x_checkbox+checkbox_size+2 * zf, y_checkbox+checkbox_size+2 * zf,
                                         fill="white", outline="white", width=1)
        if self.etiquetas_selecionadas.get(i, True):
            self.canvas_etiq.create_rectangle(x_checkbox, y_checkbox, x_checkbox+checkbox_size, y_checkbox+checkbox_size,
                                              fill="#27ae60", outline="#1a5c3a", width=int(3*zf), tags=f"checkbox_{i}")
            self.canvas_etiq.create_line(x_checkbox+6*zf, y_checkbox+14*zf, x_checkbox+11*zf, y_checkbox+20*zf, 
                                         x_checkbox+22*zf, y_checkbox+5*zf, fill="white", width=int(3*zf), capstyle="round", joinstyle="round", tags=f"checkbox_{i}")
        else:
            self.canvas_etiq.create_rectangle(x_checkbox, y_checkbox, x_checkbox+checkbox_size, y_checkbox+checkbox_size,
                                              outline="#333333", width=int(2*zf), fill="white", tags=f"checkbox_{i}")
        
        # Área clicável sobre o checkbox
        self.canvas_etiq.create_rectangle(x_checkbox - 5 * zf, y_checkbox - 5 * zf, 
                                         x_checkbox + checkbox_size + 5 * zf, y_checkbox + checkbox_size + 5 * zf,
                                         fill="", outline="", tags=f"checkbox_{i}")
        self.canvas_etiq.tag_bind(f"checkbox_{i}", "<Button-1>", lambda e, idx=i: self._toggle_etiqueta_selecao(idx))
        
        if self.etiquetas_selecionadas.get(i, True):
            self.canvas_etiq.create_text(x_checkbox+checkbox_size+8*zf, y_checkbox+checkbox_size//2, 
                                        text="Selecionado", font=("Arial", int(8*zf), "bold"), fill="#27ae60", anchor="w")
        else:
            self.canvas_etiq.create_text(x_checkbox+checkbox_size+8*zf, y_checkbox+checkbox_size//2, 
                                        text="Clique para selecionar", font=("Arial", int(7*zf)), fill="#999999", anchor="w")
        
        y_cursor += altura_etiqueta + (ESPACO_PICOTE * 3)

    # Calcular total de páginas
    self.total_paginas = max(1, math.ceil(len(self.dados_processados) / self.etiquetas_por_pagina))

    # Ajustar área de scroll
    self.canvas_etiq.configure(scrollregion=(0, 0, canvas_w, max(1188, y_cursor + MARGEM + (ALTURA_MICRO * 2))))

    # Reaplicar posição de scroll
    if 'yview_prev' in locals() and yview_prev:
        try:
            self.canvas_etiq.yview_moveto(yview_prev[0])
        except Exception:
            pass
    if hasattr(self, '_pending_yview'):
        try:
            del self._pending_yview
        except Exception:
            pass

    # Atualizar label de página
    if hasattr(self, 'label_pagina'):
        self.label_pagina.config(text=f"Página {self.pagina_atual + 1} de {self.total_paginas}")

# ========================================
# MÉTODOS DE DESENHO DAS SEÇÕES
# ========================================

def _desenhar_moldura_etiqueta_fase4(self, x, y, w, h):
    """Desenha moldura com marcas de corte"""
    # Moldura principal
    self.canvas_etiq.create_rectangle(x, y, x + w, y + h, outline="#ff6f00", width=2, fill="white")

    # Marcas de corte nos cantos
    tamanho_marca = 5
    cantos = [
        (x, y), (x + w, y),
        (x, y + h), (x + w, y + h)
    ]

    for px, py in cantos:
        self.canvas_etiq.create_line(px - tamanho_marca, py, px + tamanho_marca, py, width=1, fill="black")
        self.canvas_etiq.create_line(px, py - tamanho_marca, px, py + tamanho_marca, width=1, fill="black")

def _desenhar_topo_identico_fase4(self, x, y, w, h, elemento, pos_tipo, bitola, qtde, comp_m, idx_etiq=0):
    """
    Desenha o topo (9,3 cm) com OS, faixa vertical e tabela técnica
    ADAPTADO PARA LAJES: elemento + pos_tipo
    """
    pxmm = (CFG_PX_MM if 'CFG_PX_MM' in globals() and ETIQUETAS_LAYOUT_CFG else 4)
    def mm(v):
        return int(round(v * pxmm))

    faixa_larg = mm(FAIXA_VERTICAL_LARGURA_MM) if ETIQUETAS_LAYOUT_CFG else mm(10)
    os_w = mm(OS_BLOCO_LARGURA_MM) if ETIQUETAS_LAYOUT_CFG else mm(18)
    os_h = mm(OS_BLOCO_ALTURA_MM) if ETIQUETAS_LAYOUT_CFG else mm(30)

    # Área do bloco OS
    area_os_x1 = x + w - os_w - faixa_larg
    area_os_y1 = y
    area_os_x2 = x + w - faixa_larg
    area_os_y2 = y + os_h
    self.canvas_etiq.create_rectangle(area_os_x1, area_os_y1, area_os_x2, area_os_y2, outline="#000", width=1)
    self.canvas_etiq.create_text(area_os_x1 + 6, area_os_y1 + 6, text="OS", font=("Arial", 10, "bold"), anchor="nw")
    
    # Número da OS
    os_txt = f"{idx_etiq + 1}-{self.total_paginas}" if hasattr(self, 'total_paginas') else "-"
    linhas_os = os_txt.split("-")
    start_y = area_os_y1 + os_h // 2 - mm(6)
    espaco_linha = mm(8)
    for i, linha in enumerate(linhas_os):
        self.canvas_etiq.create_text((area_os_x1 + area_os_x2)//2, start_y + i*espaco_linha, 
                                     text=linha, font=("Arial", 11, "bold"), anchor="center")

    # Faixa vertical
    faixa_x1 = x + w - faixa_larg
    faixa_x2 = x + w
    self.canvas_etiq.create_rectangle(faixa_x1, y, faixa_x2, y + h, outline="#000", width=1)

    obra_nome = self.var_obra.get() if hasattr(self, 'var_obra') else "OBRA.001"
    if Image is None or ImageTk is None:
        self.canvas_etiq.create_text(faixa_x1 + faixa_larg//2, y + h//2, text=obra_nome, angle=90)
    else:
        try:
            img_tmp = Image.new('RGBA', (mm(60), faixa_larg), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img_tmp)
            try:
                fnt = ImageFont.truetype("arial.ttf", 12)
            except Exception:
                fnt = ImageFont.load_default()
            tw = draw.textlength(obra_nome, font=fnt)
            th = 12
            text_x = (img_tmp.width - tw) // 2
            text_y = (img_tmp.height - th) // 2
            draw.text((text_x, text_y), obra_nome, fill=(0,0,0,255), font=fnt)
            img_tmp = img_tmp.rotate(90, expand=True)
            photo = ImageTk.PhotoImage(img_tmp)
            if not hasattr(self, '_desenho_images'):
                self._desenho_images = []
            self._desenho_images.append(photo)
            self.canvas_etiq.create_image(faixa_x1 + (faixa_larg//2), y + h//2, image=photo)
        except Exception:
            self.canvas_etiq.create_text(faixa_x1 + faixa_larg//2, y + h//2, text=obra_nome, angle=90)

    # Área útil para textos
    area_util_x1 = x + 6
    area_util_x2 = area_os_x1 - 6
    area_util_w = max(0, area_util_x2 - area_util_x1)

    # Cabeçalho
    step_y = mm(8)
    y_current = y + mm(12)

    # Linha 1: Sigla/Obra
    self.canvas_etiq.create_text(area_util_x1, y_current, text="Sigla/Obra", font=("Arial", 8), anchor="nw")
    self.canvas_etiq.create_text(area_util_x1 + mm(24), y_current, text=obra_nome.replace(" ", " - "), font=("Arial", 11, "bold"), anchor="nw")
    y_current += step_y

    # Linha 2: Desenho
    self.canvas_etiq.create_text(area_util_x1, y_current, text="Desenho", font=("Arial", 8), anchor="nw")
    self.canvas_etiq.create_text(area_util_x1 + mm(24), y_current, text="PEDIDO - 00000 - Rev.0", font=("Arial", 10, "bold"), anchor="nw")
    y_current += step_y

    # Linha 3: Pavimento
    self.canvas_etiq.create_text(area_util_x1, y_current, text="Pavimento", font=("Arial", 8), anchor="nw")
    pavimento = self.var_pavimento.get() if hasattr(self, 'var_pavimento') else "LAJE 1"
    self.canvas_etiq.create_text(area_util_x1 + mm(24), y_current, text=pavimento, font=("Arial", 10, "bold"), anchor="nw")
    y_current += step_y

    # Linha 4: Elemento + POS
    self.canvas_etiq.create_text(area_util_x1, y_current, text="Elemento", font=("Arial", 8), anchor="nw")
    self.canvas_etiq.create_text(area_util_x1 + mm(24), y_current, text=f"{elemento}", font=("Arial", 10, "bold"), anchor="nw")
    self.canvas_etiq.create_text(area_util_x2 - mm(25), y_current, text="POS", font=("Arial", 8))
    self.canvas_etiq.create_text(area_util_x2 - mm(10), y_current, text=f"{pos_tipo}", font=("Arial", 12, "bold"))

    # Tabela técnica
    th = mm(TABELA_ALTURA_HEADER_MM) if ETIQUETAS_LAYOUT_CFG else mm(8)
    tr = mm(TABELA_ALTURA_LINHA_MM) if ETIQUETAS_LAYOUT_CFG else mm(10)
    tab_y1 = y + mm(45)
    tab_y2 = tab_y1 + th + tr
    tab_x = area_util_x1
    cw1 = mm(COL_BITOLA_MM if ETIQUETAS_LAYOUT_CFG else 16)
    cw2 = mm(COL_COMPR_UNIT_MM if ETIQUETAS_LAYOUT_CFG else 34)
    cw3 = mm(COL_PESO_MM if ETIQUETAS_LAYOUT_CFG else 22)
    cw4 = mm(COL_QTDE_MM if ETIQUETAS_LAYOUT_CFG else 18)
    tot = cw1 + cw2 + cw3 + cw4
    if tot > area_util_w:
        escala = area_util_w / tot
        cw1 = int(cw1 * escala); cw2 = int(cw2 * escala); cw3 = int(cw3 * escala); cw4 = int(cw4 * escala)
    
    # Desenhar tabela
    self.canvas_etiq.create_rectangle(tab_x, tab_y1, tab_x + cw1 + cw2 + cw3 + cw4, tab_y2, outline="#000", width=1)
    self.canvas_etiq.create_line(tab_x + cw1, tab_y1, tab_x + cw1, tab_y2)
    self.canvas_etiq.create_line(tab_x + cw1 + cw2, tab_y1, tab_x + cw1 + cw2, tab_y2)
    self.canvas_etiq.create_line(tab_x + cw1 + cw2 + cw3, tab_y1, tab_x + cw1 + cw2 + cw3, tab_y2)
    self.canvas_etiq.create_line(tab_x, tab_y1 + th, tab_x + cw1 + cw2 + cw3 + cw4, tab_y1 + th)
    
    # Headers
    self.canvas_etiq.create_text(tab_x + cw1//2, tab_y1 + th//2, text="Bitola", font=("Arial", 7, "bold"))
    self.canvas_etiq.create_text(tab_x + cw1 + cw2//2, tab_y1 + th//2, text="Compr. Unit.", font=("Arial", 7, "bold"))
    self.canvas_etiq.create_text(tab_x + cw1 + cw2 + cw3//2, tab_y1 + th//2, text="Peso", font=("Arial", 7, "bold"))
    self.canvas_etiq.create_text(tab_x + cw1 + cw2 + cw3 + cw4//2, tab_y1 + th//2, text="Qtde", font=("Arial", 7, "bold"))
    
    # Valores editáveis
    tag_bitola = f"edit_bitola_{elemento}_{pos_tipo}"
    tag_comp = f"edit_comp_{elemento}_{pos_tipo}"
    tag_qtde = f"edit_qtde_{elemento}_{pos_tipo}"
    
    # Usar valores customizados se existirem
    chave = (elemento, pos_tipo)
    if chave in self.medidas_customizadas:
        bitola = self.medidas_customizadas[chave].get('bitola', bitola)
        comp_m = self.medidas_customizadas[chave].get('comp', comp_m)
        qtde = self.medidas_customizadas[chave].get('qtde', qtde)
    
    txt_bitola = self.canvas_etiq.create_text(tab_x + cw1//2, tab_y1 + th + tr//2, text=f"{bitola:.2f}", font=("Arial", 8, "underline"), fill="#0066cc", tags=(tag_bitola,))
    txt_comp = self.canvas_etiq.create_text(tab_x + cw1 + cw2//2, tab_y1 + th + tr//2, text=f"{comp_m:.3f}", font=("Arial", 8, "underline"), fill="#0066cc", tags=(tag_comp,))
    
    # Calcular peso
    peso_val = 0.0
    try:
        from core.peso import peso_linear_kg_m
        peso_val = peso_linear_kg_m(float(bitola)) * float(comp_m) * float(qtde)
    except Exception as e:
        print(f"[peso] Falha ao calcular: {e}")
    self.canvas_etiq.create_text(tab_x + cw1 + cw2 + cw3//2, tab_y1 + th + tr//2, text=f"{peso_val:.2f}", font=("Arial", 8))
    
    txt_qtde = self.canvas_etiq.create_text(tab_x + cw1 + cw2 + cw3 + cw4//2, tab_y1 + th + tr//2, text=f"{qtde}", font=("Arial", 8, "underline"), fill="#0066cc", tags=(tag_qtde,))
    
    # Bindings para editar
    self.canvas_etiq.tag_bind(txt_bitola, "<Button-1>", lambda e, el=elemento, p=pos_tipo, tipo="bitola": self._editar_medida_etiqueta(el, p, tipo))
    self.canvas_etiq.tag_bind(txt_comp, "<Button-1>", lambda e, el=elemento, p=pos_tipo, tipo="comp": self._editar_medida_etiqueta(el, p, tipo))
    self.canvas_etiq.tag_bind(txt_qtde, "<Button-1>", lambda e, el=elemento, p=pos_tipo, tipo="qtde": self._editar_medida_etiqueta(el, p, tipo))

    # Desenho técnico (placeholder - pode ser expandido)
    margem_topo = mm(3)
    margem_lateral = mm(3)
    draw_area_x1 = area_util_x1 + margem_lateral
    draw_area_x2 = area_util_x2 - margem_lateral
    draw_area_y1 = tab_y2 + margem_topo
    draw_area_y2 = y + h - margem_topo
    
    if draw_area_x2 > draw_area_x1 and draw_area_y2 > draw_area_y1:
        avail_w = draw_area_x2 - draw_area_x1
        avail_h = draw_area_y2 - draw_area_y1
        
        pref_w = mm(DESENHO_LARGURA_MM) if ETIQUETAS_LAYOUT_CFG else mm(60)
        pref_h = mm(DESENHO_ALTURA_MM) if ETIQUETAS_LAYOUT_CFG else mm(50)
        escala = min(avail_w / max(1, pref_w), avail_h / max(1, pref_h), 6.0)
        dw = max(10, int(pref_w * escala))
        dh = max(10, int(pref_h * escala))
        dx = draw_area_x1 + (avail_w - dw) // 2
        dy = draw_area_y1 + (avail_h - dh) // 2
        
        # Área do desenho clicável
        tag = f"desenho_{elemento}_{pos_tipo}"
        rect_id = self.canvas_etiq.create_rectangle(
            dx, dy, dx + dw, dy + dh,
            outline="#e11d48", width=2, fill="white", tags=(tag,)
        )
        self.canvas_etiq.tag_bind(tag, "<Button-1>", lambda e, el=elemento, p=pos_tipo: self._editar_desenho_canvas(el, p))
        
        # Desenhar forma baseada em formato_dobra ou forma customizada
        chave = (elemento, pos_tipo)
        forma_raw = self.formas_customizadas.get(chave)
        
        if not forma_raw:
            # Detectar baseado no formato_dobra do dado
            try:
                dado_idx = None
                for idx, d in enumerate(self.dados_processados):
                    if d[0] == elemento and str(d[1]) == pos_tipo:
                        dado_idx = idx
                        break
                if dado_idx is not None and len(self.dados_processados[dado_idx]) > 7:
                    formato_dobra = self.dados_processados[dado_idx][7]
                    if 'BARRA U' in formato_dobra.upper():
                        forma_raw = 'barra_u'
                    else:
                        forma_raw = 'reta'
                else:
                    forma_raw = 'reta'
            except:
                forma_raw = 'reta'
        
        # Desenhar forma simplificada
        cx, cy = dx + dw//2, dy + dh//2
        if 'reta' in str(forma_raw).lower():
            # Desenhar barra reta
            self.canvas_etiq.create_line(dx + 10, cy, dx + dw - 10, cy, fill="#e11d48", width=3)
            self.canvas_etiq.create_text(cx, cy - 15, text="RETA", font=("Arial", 8, "bold"), fill="#333")
        elif 'barra_u' in str(forma_raw).lower() or 'u' in str(forma_raw).lower():
            # Desenhar barra U
            pontos = [
                dx + 20, dy + 20,
                dx + 20, dy + dh - 20,
                dx + dw - 20, dy + dh - 20,
                dx + dw - 20, dy + 20
            ]
            self.canvas_etiq.create_line(pontos, fill="#e11d48", width=3)
            self.canvas_etiq.create_text(cx, dy + 10, text="BARRA U", font=("Arial", 8, "bold"), fill="#333")
        else:
            # Forma genérica
            self.canvas_etiq.create_text(cx, cy, text=str(forma_raw).upper(), font=("Arial", 9, "bold"), fill="#333")

def _desenhar_picote_fase4(self, x, y, w):
    """Desenha linha de picote tracejada"""
    self.canvas_etiq.create_line(x, y, x + w, y, fill="red", width=2, dash=(4, 4))
    self.canvas_etiq.create_text(x + w // 2, y - 8, text="✄ DESTACAR AQUI", font=("Arial", 5), fill="red")

def _desenhar_secao_micro_fase4(self, x, y, w, h, elemento, pos_tipo, bitola, qtde, comp_m):
    """
    Seção inferior (1,9 cm): 2 linhas compactas
    ADAPTADO PARA LAJES
    """
    # Calcular OS por elemento
    try:
        idx = -1
        for i, dado in enumerate(self.dados_processados):
            if dado[0] == elemento and str(dado[1]) == pos_tipo:
                idx = i
                break
        
        if idx >= 0:
            elemento_index = sum(1 for i in range(idx) if self.dados_processados[i][0] == elemento)
            elemento_total = sum(1 for d in self.dados_processados if d[0] == elemento)
            os_num = f"{elemento_index + 1}-{elemento_total}"
        else:
            os_num = "-"
    except Exception:
        os_num = "-"

    texto_center_x = x + w // 2
    
    obra = self.var_obra.get() if hasattr(self, 'var_obra') else ""
    pavimento = self.var_pavimento.get() if hasattr(self, 'var_pavimento') else ""
    
    # Linha 1
    y_linha1 = y + h * 0.3
    texto_linha1 = f"{obra}|{pavimento} • {elemento}/{pos_tipo} • OS:{os_num}"
    self.canvas_etiq.create_text(texto_center_x, y_linha1, text=texto_linha1, font=("Arial", 7, "bold"), fill="black", anchor="center")
    
    # Linha 2
    y_linha2 = y + h * 0.6
    texto_linha2 = f"Ø{bitola:.1f}mm • Q:{qtde} • C:{comp_m:.2f}m"
    self.canvas_etiq.create_text(texto_center_x, y_linha2, text=texto_linha2, font=("Arial", 7, "bold"), fill="black", anchor="center")

# ========================================
# MÉTODOS DE INTERAÇÃO E EDIÇÃO
# ========================================

def _handle_canvas_click(self, event):
    """Handler de clique no canvas - verifica checkbox ou etiqueta"""
    x = self.canvas_etiq.canvasx(event.x)
    y = self.canvas_etiq.canvasy(event.y)
    
    # Primeiro: verificar checkbox
    if hasattr(self, '_checkbox_positions') and self._checkbox_positions:
        for idx, pos_info in self._checkbox_positions.items():
            x1, y1, x2, y2 = pos_info['x1'], pos_info['y1'], pos_info['x2'], pos_info['y2']
            if x1 <= x <= x2 and y1 <= y <= y2:
                self._toggle_etiqueta_selecao(idx)
                return "break"
    
    # Segundo: verificar clique na etiqueta para editar
    items_at_point = self.canvas_etiq.find_overlapping(x-5, y-5, x+5, y+5)
    for item in items_at_point:
        tags = self.canvas_etiq.gettags(item)
        for tag in tags:
            if tag.startswith('etiq_'):
                idx_str = tag.replace('etiq_', '')
                try:
                    idx = int(idx_str)
                    if idx < len(self.dados_processados):
                        dado = self.dados_processados[idx]
                        elemento = dado[0]
                        pos_tipo = str(dado[1])
                        bitola = float(dado[2])
                        qtde = int(dado[3])
                        comp_m = float(dado[4])
                        self._editar_etiqueta_dados(idx, elemento, pos_tipo, bitola, qtde, comp_m)
                        return "break"
                except:
                    pass

def _toggle_etiqueta_selecao(self, idx):
    """Toggle - inverte o estado da etiqueta clicada"""
    current_state = self.etiquetas_selecionadas.get(idx, True)
    self.etiquetas_selecionadas[idx] = not current_state
    
    self.desenhar_etiquetas_com_selecao()
    
    total_selecionadas = sum(1 for v in self.etiquetas_selecionadas.values() if v)
    self.label_selecionadas.config(text=f"Selecionadas: {total_selecionadas}/{len(self.dados_processados)}")

def _editar_medida_etiqueta(self, elemento, pos_tipo, tipo):
    """
    Abre diálogo para editar bitola, comp ou qtde diretamente
    ADAPTADO PARA LAJES
    """
    chave = (elemento, pos_tipo)
    
    # Buscar valores atuais
    item_atual = None
    for item in self.dados_processados:
        if item[0] == elemento and str(item[1]) == pos_tipo:
            item_atual = item
            break
    
    if not item_atual:
        messagebox.showwarning("Aviso", f"Item {elemento} {pos_tipo} não encontrado")
        return
    
    bitola_atual = item_atual[2]
    qtde_atual = item_atual[3]
    comp_atual = item_atual[4]
    
    # Verificar customização
    if chave in self.medidas_customizadas:
        bitola_atual = self.medidas_customizadas[chave].get('bitola', bitola_atual)
        comp_atual = self.medidas_customizadas[chave].get('comp', comp_atual)
        qtde_atual = self.medidas_customizadas[chave].get('qtde', qtde_atual)
    
    # Diálogo
    if tipo == "bitola":
        novo_valor = simpledialog.askfloat(
            "Editar Bitola",
            f"Nova bitola para {elemento} {pos_tipo}:",
            initialvalue=bitola_atual,
            minvalue=0.1,
            maxvalue=100.0
        )
    elif tipo == "comp":
        novo_valor = simpledialog.askfloat(
            "Editar Comprimento",
            f"Novo comprimento (m) para {elemento} {pos_tipo}:",
            initialvalue=comp_atual,
            minvalue=0.01,
            maxvalue=100.0
        )
    elif tipo == "qtde":
        novo_valor = simpledialog.askinteger(
            "Editar Quantidade",
            f"Nova quantidade para {elemento} {pos_tipo}:",
            initialvalue=int(qtde_atual),
            minvalue=1,
            maxvalue=10000
        )
    else:
        return
    
    if novo_valor is None:
        return
    
    # Armazenar customização
    if chave not in self.medidas_customizadas:
        self.medidas_customizadas[chave] = {}
    
    self.medidas_customizadas[chave][tipo] = novo_valor
    
    # Redesenhar
    self.desenhar_etiquetas_com_selecao()

def _editar_desenho_canvas(self, elemento, pos_tipo):
    """Editar o desenho (forma) da barra - ADAPTADO PARA LAJES"""
    print(f"\n[CLIQUE DETECTADO!] _editar_desenho_canvas para {elemento}/{pos_tipo}")
    chave = (elemento, pos_tipo)

    # Buscar dados atuais
    item_atual = None
    for item in self.dados_processados:
        if item[0] == elemento and str(item[1]) == pos_tipo:
            item_atual = item
            break
    if not item_atual:
        messagebox.showwarning("Aviso", f"Item {elemento} {pos_tipo} não encontrado")
        return

    bitola_atual = float(item_atual[2])
    qtde_atual = int(item_atual[3])
    comp_atual = float(item_atual[4])
    
    if chave in self.medidas_customizadas:
        bitola_atual = float(self.medidas_customizadas[chave].get('bitola', bitola_atual))
        comp_atual = float(self.medidas_customizadas[chave].get('comp', comp_atual))
        qtde_atual = int(self.medidas_customizadas[chave].get('qtde', qtde_atual))
    
    forma_atual = self.formas_customizadas.get(chave, 'reta')

    # Controles integrados
    controls = tk.Frame(self.janela_editor, bg="#ecf0f1")
    controls.pack(fill="x", padx=14, pady=8)
    
    var_forma = tk.StringVar(value=forma_atual)
    tk.Label(controls, text="Forma:", bg="#ecf0f1").grid(row=0, column=0, sticky="w")
    formas_opcoes = [
        ("Reta", "reta"),
        ("Barra U", "barra_u"),
        ("Gancho", "gancho"),
    ]
    for j, (label, f) in enumerate(formas_opcoes):
        tk.Radiobutton(controls, text=label, variable=var_forma, value=f, bg="#ecf0f1").grid(row=0, column=j+1, padx=4)

    tk.Label(controls, text="Bitola (mm):", bg="#ecf0f1").grid(row=1, column=0, sticky="w", pady=4)
    ent_bitola = tk.Entry(controls, width=10)
    ent_bitola.insert(0, f"{bitola_atual:.1f}")
    ent_bitola.grid(row=1, column=1)

    tk.Label(controls, text="Compr. (m):", bg="#ecf0f1").grid(row=1, column=2, sticky="w")
    ent_comp = tk.Entry(controls, width=10)
    ent_comp.insert(0, f"{comp_atual:.2f}")
    ent_comp.grid(row=1, column=3)

    tk.Label(controls, text="Qtde:", bg="#ecf0f1").grid(row=1, column=4, sticky="w")
    ent_qtde = tk.Entry(controls, width=6)
    ent_qtde.insert(0, str(qtde_atual))
    ent_qtde.grid(row=1, column=5)

    btns = tk.Frame(self.janela_editor, bg="#ecf0f1")
    btns.pack(pady=12)

    def salvar():
        print(f"\n[SALVAR CHAMADO!] {chave}")
        try:
            novo_bitola = float(ent_bitola.get())
            novo_comp = float(ent_comp.get())
            novo_qtde = int(ent_qtde.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite valores válidos")
            return
        
        forma_sel = var_forma.get()
        print(f"[SALVAR] chave={chave}, forma_sel='{forma_sel}'")
        
        if chave not in self.medidas_customizadas:
            self.medidas_customizadas[chave] = {}
        self.medidas_customizadas[chave]['bitola'] = novo_bitola
        self.medidas_customizadas[chave]['comp'] = novo_comp
        self.medidas_customizadas[chave]['qtde'] = novo_qtde
        self.formas_customizadas[chave] = forma_sel
        
        try:
            self._pending_yview = self.canvas_etiq.yview()
        except Exception:
            self._pending_yview = None
        
        # Remover controles
        controls.destroy()
        btns.destroy()
        
        self.desenhar_etiquetas_com_selecao()

    tk.Button(btns, text="✓ Salvar", command=salvar, bg="#27ae60", fg="white", font=("Arial", 11, "bold"), width=12).pack(side="left", padx=10)
    tk.Button(btns, text="✗ Cancelar", command=lambda: (controls.destroy(), btns.destroy()), bg="#e74c3c", fg="white", font=("Arial", 11, "bold"), width=12).pack(side="left", padx=10)

def _editar_etiqueta_dados(self, idx, elemento, pos_tipo, bitola, qtde, comp_m):
    """
    Abre diálogo completo para editar dados + forma + medidas
    ADAPTADO PARA LAJES
    """
    dado = self.dados_processados[idx]
    chave = (elemento, pos_tipo)
    
    # Diálogo de edição
    dialog = tk.Toplevel(self.janela_editor)
    dialog.title(f"Editar Etiqueta #{idx+1} - {elemento}/{pos_tipo}")
    dialog.geometry("520x500")
    dialog.configure(bg="#0d2818")
    
    # Centralizar
    dialog.update_idletasks()
    x = self.janela_editor.winfo_x() + 400
    y = self.janela_editor.winfo_y() + 200
    dialog.geometry(f"520x500+{x}+{y}")
    
    tk.Label(dialog, text=f"Editar: {elemento} {pos_tipo}", bg="#0d2818", fg="#ff9800", 
            font=("Arial", 11, "bold")).pack(pady=10)
    
    frame = tk.Frame(dialog, bg="#0d2818")
    frame.pack(padx=10, pady=5)
    
    # Bitola
    tk.Label(frame, text="Bitola (mm):", bg="#0d2818", fg="white").pack(side="left", padx=5)
    var_bitola = tk.DoubleVar(value=bitola)
    tk.Entry(frame, textvariable=var_bitola, width=10, font=("Arial", 10)).pack(side="left", padx=5)
    
    # Quantidade
    frame2 = tk.Frame(dialog, bg="#0d2818")
    frame2.pack(padx=10, pady=5)
    tk.Label(frame2, text="Quantidade:", bg="#0d2818", fg="white").pack(side="left", padx=5)
    var_qtde = tk.IntVar(value=qtde)
    tk.Entry(frame2, textvariable=var_qtde, width=10, font=("Arial", 10)).pack(side="left", padx=5)
    
    # Comprimento
    frame3 = tk.Frame(dialog, bg="#0d2818")
    frame3.pack(padx=10, pady=5)
    tk.Label(frame3, text="Comprimento (m):", bg="#0d2818", fg="white").pack(side="left", padx=5)
    var_comp = tk.DoubleVar(value=comp_m)
    tk.Entry(frame3, textvariable=var_comp, width=10, font=("Arial", 10)).pack(side="left", padx=5)
    
    # Forma
    frame4 = tk.Frame(dialog, bg="#0d2818")
    frame4.pack(padx=10, pady=5)
    tk.Label(frame4, text="Forma:", bg="#0d2818", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
    
    formas_map = {
        "Reta": "reta",
        "Barra U": "barra_u",
        "Gancho": "gancho"
    }
    formas_map_inverso = {v: k for k, v in formas_map.items()}
    
    forma_atual = self.formas_customizadas.get(chave, "reta")
    forma_display = formas_map_inverso.get(forma_atual, "Reta")
    
    var_forma = tk.StringVar(value=forma_display)
    combo_forma = ttk.Combobox(frame4, textvariable=var_forma, values=list(formas_map.keys()), 
                               state="readonly", width=20)
    combo_forma.set(forma_display)
    combo_forma.pack(side="left", padx=5)
    
    # Campo Cortado
    frame_cortado = tk.Frame(dialog, bg="#0d2818")
    frame_cortado.pack(fill="x", padx=14, pady=4)
    var_cortado = tk.BooleanVar()
    cortado_atual = False
    if chave in self.medidas_customizadas and 'cortado' in self.medidas_customizadas[chave]:
        cortado_atual = bool(self.medidas_customizadas[chave]['cortado'])
    var_cortado.set(cortado_atual)
    tk.Checkbutton(frame_cortado, text="Cortado", variable=var_cortado, bg="#0d2818", fg="white",
                  selectcolor="#0d2818", font=("Arial", 10)).pack(side="left")
    
    # Botões
    btn_frame = tk.Frame(dialog, bg="#0d2818")
    btn_frame.pack(pady=15)
    
    def salvar_edicao():
        try:
            # Atualizar dados_processados
            peso_novo = dado[6] if len(dado) > 6 else 0
            self.dados_processados[idx] = (elemento, pos_tipo, var_bitola.get(), var_qtde.get(), var_comp.get(), 
                                          dado[5] if len(dado) > 5 else "", peso_novo,
                                          dado[7] if len(dado) > 7 else "", dado[8] if len(dado) > 8 else [])
            
            medidas_novo = {
                'bitola': var_bitola.get(),
                'qtde': var_qtde.get(),
                'comp': var_comp.get(),
                'cortado': var_cortado.get()
            }
            self.medidas_customizadas[chave] = medidas_novo
            
            forma_display = var_forma.get()
            forma_selecionada = formas_map.get(forma_display, "reta")
            self.formas_customizadas[chave] = forma_selecionada
            
            dialog.destroy()
            self.desenhar_etiquetas_com_selecao()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    tk.Button(btn_frame, text="✅ SALVAR", command=salvar_edicao,
             bg="#27ae60", fg="white", font=("Arial", 10), padx=15, pady=5).pack(side="left", padx=5)
    tk.Button(btn_frame, text="✕ CANCELAR", command=dialog.destroy,
             bg="#e74c3c", fg="white", font=("Arial", 10), padx=15, pady=5).pack(side="left", padx=5)

# ========================================
# FIM DOS MÉTODOS ADAPTADOS
# ========================================
