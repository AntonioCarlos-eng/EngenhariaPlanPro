# lajes_app_completo.py - SISTEMA DE LAJES UNIFICADO

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import os
import sys
import math
import json
import re
try:
    from PIL import Image, ImageTk
    PIL_DISPONIVEL = True
except Exception:
    Image = None
    ImageTk = None
    PIL_DISPONIVEL = False
from typing import Dict, Any, List, Tuple, Optional

# Importa o motor real do core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.lajes_motor import processar_lajes, analisar_barra_geometricamente, BITOLAS_VALIDAS

# Etiquetas no mesmo padrão de vigas/pilares (opcional)
try:
    from core.etiquetas_generator import GeradorEtiquetasDinamico
    ETIQUETAS_GERADOR_DISPONIVEL = True
except Exception:
    GeradorEtiquetasDinamico = None
    ETIQUETAS_GERADOR_DISPONIVEL = False

# Constantes para os nomes dos arquivos de persistência
ESTADO_FILEPATH = "lajes_checklist_state.json"
PLANILHAMENTO_FILEPATH = "lajes_planilhamento_editado.json"

# --- CLASSE ANALISADOR GEOMÉTRICO ---

class AnalisadorGeometricoLajes:
    """Análise geométrica para lajes (compatível com vigas e pilares)."""
    
    @staticmethod
    def identificar_tipo_laje(pos: str, bitola: float, comp_m: float, formato_dobra: str = None) -> str:
        """Identifica o tipo de barra de laje."""
        if formato_dobra:
            return formato_dobra
        
        # Fallback baseado em posição
        pos_upper = pos.upper()
        if 'P/' in pos_upper or 'POS' in pos_upper:
            return "RETA (01) - POSITIVA"
        elif 'N/' in pos_upper or 'NEG' in pos_upper:
            return "BARRA U (11)"
        
        return "RETA (01)"

# --- CLASSE PRINCIPAL DO APLICATIVO ---

class LajesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("EngenhariaPlanPro - LAJES")
        self.geometry("1200x700")
        self.configure(bg="#0d2818")
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 600
        y = (self.winfo_screenheight() // 2) - 350
        self.geometry(f"1200x700+{x}+{y}")
        
        self.arquivos_selecionados = []
        self.dados_processados: List[Tuple[str, str, float, float, float, float, float, str, List[float]]] = [] 
        self.lajes_ativas = set()  
        self.total_kg = 0.0
        self.total_pecas = 0
        self.checkboxes_conf: Dict[Tuple[str, str], Dict[str, tk.BooleanVar]] = {} 
        self.estado_salvo_checklist: Dict[str, Dict[str, bool]] = {} 
        
        self.janela_etiq = None
        self.canvas_etiq = None
        self.indice_etiqueta_pagina = 0 
        self.pecas_por_pagina = 6 
        self.dados_etiquetas_filtrados = [] 

        self.var_obra = tk.StringVar(value="OBRA 001")
        self.var_pavimento = tk.StringVar(value="LAJE 1")

        # 1. Inicialização: Começa VAZIO (sem Mock)
        self.dados_processados, self.total_kg, self.total_pecas = [], 0.0, 0
        
        # 2. Carrega persistência (se houver)
        self.carregar_planilhamento()
        self.carregar_estado_persistencia()
        
        # 3. Garante que as lajes ativas são as do dataset carregado
        elementos_iniciais = set(dado[0] for dado in self.dados_processados)
        if not self.lajes_ativas and elementos_iniciais:
             self.lajes_ativas = elementos_iniciais
        
        self._criar_interface()
        self.recarregar_treeview()


    # --- PERSISTÊNCIA GERAL ---
    def salvar_estado_persistencia(self):
        estado = {
            "obra": self.var_obra.get(),
            "pavimento": self.var_pavimento.get(),
            "lajes_ativas": list(self.lajes_ativas),
            "checklist_status": {}
        }
        if self.checkboxes_conf:
            for (elemento, pos), vars_dict in self.checkboxes_conf.items():
                chave = f"{elemento}-{pos}"
                estado["checklist_status"][chave] = { status: var.get() for status, var in vars_dict.items() }

        try:
            with open(ESTADO_FILEPATH, 'w', encoding='utf-8') as f:
                json.dump(estado, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Erro de Persistência", f"Não foi possível salvar o estado: {e}")
            return False

    def carregar_estado_persistencia(self):
        try:
            with open(ESTADO_FILEPATH, 'r', encoding='utf-8') as f:
                estado = json.load(f)
                self.var_obra.set(estado.get("obra", "OBRA 001"))
                self.var_pavimento.set(estado.get("pavimento", "LAJE 1"))
                lajes = set(estado.get("lajes_ativas", []))
                if lajes: self.lajes_ativas = lajes
                self.estado_salvo_checklist = estado.get("checklist_status", {})
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Aviso: Não foi possível carregar o estado salvo: {e}")

    def salvar_planilhamento(self):
        if not self.dados_processados:
            messagebox.showwarning("Atenção", "Nenhum dado para salvar.")
            return

        dados_serializaveis = [list(dado) for dado in self.dados_processados]

        try:
            with open(PLANILHAMENTO_FILEPATH, 'w', encoding='utf-8') as f:
                json.dump(dados_serializaveis, f, indent=4)
            self.salvar_estado_persistencia()
            messagebox.showinfo("Sucesso", "Planilhamento editado e estado salvos com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro de Salvamento", f"Não foi possível salvar o planilhamento: {e}")

    def carregar_planilhamento(self):
        try:
            with open(PLANILHAMENTO_FILEPATH, 'r', encoding='utf-8') as f:
                dados_serializaveis = json.load(f)
                dados_carregados = []
                for dado_list in dados_serializaveis:
                    dado = (
                        dado_list[0], dado_list[1], float(dado_list[2]), 
                        float(dado_list[3]), float(dado_list[4]), 
                        float(dado_list[5]), float(dado_list[6]), 
                        dado_list[7], [float(m) for m in dado_list[8]]
                    )
                    dados_carregados.append(dado)
                
                if dados_carregados:
                    self.dados_processados = dados_carregados
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Aviso: Erro ao carregar planilhamento salvo. Iniciando vazio. {e}")


    # --- CÁLCULOS E AUXILIARES ---

    def _calcular_comp_corte_com_forma(self, forma: str, medidas_m: List[float], bitola_mm: float) -> float:
        comp_segmentos = 0
        num_dobras = 0
        
        if forma.startswith("RETA") or forma.startswith("REFORÇO") or forma.startswith("MALHA"):
            num_dobras = 0
            comp_segmentos = medidas_m[0] if medidas_m else 0.0
        elif forma.startswith("DOBRA L") or forma.startswith("BARRA L"):
            num_dobras = 1
            comp_segmentos = sum(medidas_m[:2])
        elif forma.startswith("BARRA U"):
            num_dobras = 2
            comp_segmentos = sum(medidas_m[:3])
        elif forma.startswith("ESTRIBO") and len(medidas_m) >= 2:
            num_dobras = 4
            A = medidas_m[0]
            B = medidas_m[1]
            comp_segmentos = 2 * A + 2 * B
        
        correcao = (bitola_mm / 1000.0) * 0.5 * num_dobras
        comp_final = comp_segmentos - correcao
        return max(0.01, comp_final)

    def _atualizar_dados_globais(self, elemento_original: str, pos_original: str, novos_dados: Dict[str, Any]):
        for i, dado in enumerate(self.dados_processados):
            elemento, pos, bitola, qtde_area, comp_m, largura_m, peso_kg, formato_dobra, medidas_m = dado
            
            if elemento == elemento_original and pos == pos_original:
                nova_qtde_area = novos_dados.get('qtde_area', qtde_area)
                novo_comp_m = novos_dados.get('comp_m', comp_m)
                novo_largura_m = 0.0
                novo_formato = novos_dados.get('formato_dobra', formato_dobra)
                novas_medidas = novos_dados.get('medidas_m', medidas_m)
                
                if novo_formato.endswith("(TELA)"):
                    novo_comp_m = novas_medidas[0] if novas_medidas else novo_comp_m
                    novo_largura_m = novas_medidas[1] if len(novas_medidas) > 1 else novo_largura_m
                    novo_peso_kg = _calcular_peso(bitola, (novo_comp_m * novo_largura_m), 1) * 3 
                else:
                    if novas_medidas:
                        novo_comp_m = self._calcular_comp_corte_com_forma(novo_formato, novas_medidas, bitola)
                    qtde_int = int(round(nova_qtde_area)) if isinstance(nova_qtde_area, float) else nova_qtde_area
                    novo_peso_kg = _calcular_peso(bitola, novo_comp_m, qtde_int)
                    
                novo_dado = (
                    elemento, pos, bitola, nova_qtde_area, 
                    round(novo_comp_m, 2), round(novo_largura_m, 2), 
                    round(novo_peso_kg, 2), novo_formato, novas_medidas
                )
                self.dados_processados[i] = novo_dado
                break

        self.recarregar_treeview()
        if self.janela_etiq and self.janela_etiq.winfo_exists():
            self.dados_etiquetas_filtrados, _, _ = self.aplicar_filtro_producao()
            if self.dados_etiquetas_filtrados:
                 self.desenhar_pagina_etiquetas_lajes(self.indice_etiqueta_pagina)


    # --- INTERFACE E CONTROLES ---

    def _criar_interface(self):
        # Container principal
        main_container = tk.Frame(self, bg="#0d2818")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        header = tk.Frame(main_container, bg="#0d2818")
        header.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            header,
            text="🏗️ PROCESSAMENTO DE LAJES",
            font=("Arial", 20, "bold"),
            bg="#0d2818",
            fg="#ff9800"
        ).pack()
        
        # Frame de controles (Botões)
        control_frame = tk.Frame(main_container, bg="#1a3d2e")
        control_frame.pack(fill="x", pady=5)
        
        # Linha 1 - Dados do projeto
        row1 = tk.Frame(control_frame, bg="#1a3d2e")
        row1.pack(fill="x", padx=10, pady=10)
        
        tk.Label(row1, text="Obra:", bg="#1a3d2e", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Entry(row1, textvariable=self.var_obra, width=25, font=("Arial", 10)).pack(side="left", padx=5)
        
        tk.Label(row1, text="Laje/Pavimento:", bg="#1a3d2e", fg="white", font=("Arial", 10)).pack(side="left", padx=20)
        tk.Entry(row1, textvariable=self.var_pavimento, width=20, font=("Arial", 10)).pack(side="left", padx=5)

        tk.Button(
            row1,
            text="💾 Salvar Planilha",
            command=self.salvar_planilhamento,
            bg="#2e7d32", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5, cursor="hand2"
        ).pack(side="right", padx=5)
        
        # Linha 2 - Botões principais
        row2 = tk.Frame(control_frame, bg="#1a3d2e")
        row2.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Button(
            row2, text="📁 Selecionar Arquivos", command=self.selecionar_arquivos,
            bg="#ff6f00", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5, cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            row2, text="⚙️ PROCESSAR", command=lambda: self.processar(inicial=False),
            bg="#ff8f00", fg="white", font=("Arial", 11, "bold"), padx=20, pady=5, cursor="hand2"
        ).pack(side="left", padx=5)

        tk.Button(
            row2, text="📐 Gerenciar Produção", command=self.gerenciar_producao,
            bg="#5e35b1", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5, cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            row2, text="📄 Gerar Romaneio", command=self.gerar_romaneio,
            bg="#1976d2", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5, cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            row2, text="📋 Check List", command=self.gerar_romaneio_conferencia,
            bg="#00acc1", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5, cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            row2, text="🏷️ Etiquetas", command=self.imprimir_etiquetas,
            bg="#9c27b0", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5, cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            row2, text="📊 Exportar Excel", command=self.exportar_excel,
            bg="#4caf50", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5, cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            row2, text="🔄 Limpar Tudo", command=self.limpar,
            bg="#757575", fg="white", font=("Arial", 10), padx=15, pady=5, cursor="hand2"
        ).pack(side="left", padx=5)
        
        # Frame da tabela
        table_frame = tk.Frame(main_container, bg="#0d2818")
        table_frame.pack(fill="both", expand=True, pady=10)
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e")
        style.configure("Treeview.Heading", background="#ff6f00", foreground="white", font=("Arial", 10, "bold"))
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=("elemento", "pos", "bitola", "qtd_area", "comp_m", "largura_m", "peso", "formato", "medidas"),
            show="headings",
        )
        
        # Configurar colunas visíveis
        self.tree.heading("elemento", text="ELEMENTO")
        self.tree.heading("pos", text="TIPO/POS")
        self.tree.heading("bitola", text="Ø (mm)")
        self.tree.heading("qtd_area", text="QTD (pçs)")
        self.tree.heading("comp_m", text="COMP. (m)")
        self.tree.heading("largura_m", text="LARG. (m)")
        self.tree.heading("peso", text="PESO (kg)")
        
        self.tree.column("elemento", width=150, anchor="center")
        self.tree.column("pos", width=100, anchor="center")
        self.tree.column("bitola", width=80, anchor="center")
        self.tree.column("qtd_area", width=120, anchor="center")
        self.tree.column("comp_m", width=100, anchor="center")
        self.tree.column("largura_m", width=100, anchor="center")
        self.tree.column("peso", width=100, anchor="center")

        # Esconder colunas auxiliares
        self.tree.column("formato", width=0, stretch=tk.NO)
        self.tree.column("medidas", width=0, stretch=tk.NO)
        
        self.tree.pack(fill="both", expand=True)
        
        # Status bar
        self.status_frame = tk.Frame(main_container, bg="#1a3d2e", relief="sunken", bd=1)
        self.status_frame.pack(fill="x", pady=(5, 0))
        
        self.status_label = tk.Label(
            self.status_frame, text="✅ Pronto. Selecione os arquivos DXF/DWG.", bg="#1a3d2e", fg="white", font=("Arial", 10), anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        self.info_label = tk.Label(
            self.status_frame, text="", bg="#1a3d2e", fg="#ff9800", font=("Arial", 10, "bold"), anchor="e"
        )
        self.info_label.pack(side="right", padx=10, pady=5)

    def selecionar_arquivos(self):
        arquivos = filedialog.askopenfilenames(
            title="Selecionar arquivos DXF/DWG de LAJES",
            filetypes=[("Arquivos CAD", "*.dxf *.dwg"), ("DXF", "*.dxf"), ("DWG", "*.dwg"), ("Todos", "*.*")]
        )
        if arquivos:
            self.arquivos_selecionados = list(arquivos)
            self.status_label.config(text=f"📁 {len(arquivos)} arquivo(s) selecionado(s)")
            nomes = [os.path.basename(f) for f in arquivos]
            if len(nomes) > 3: texto = f"{', '.join(nomes[:3])}, ..."
            else: texto = ', '.join(nomes)
            self.info_label.config(text=texto)

    def recarregar_treeview(self):
        dados_filtrados, total_kg, total_pecas = self.aplicar_filtro_producao()

        for item in self.tree.get_children(): self.tree.delete(item)
        
        for dado in dados_filtrados:
            elemento, pos, bitola, qtd_area, comp_m, largura_m, peso_kg, formato, medidas = dado
            
            # Formatação - quantidade apenas número (sem "pçs")
            qtd_area_fmt = f"{int(round(qtd_area))}"
            
            # largura_m pode ser string (VARIÁVEL/NORMAL) ou float
            if isinstance(largura_m, str):
                largura_fmt = largura_m
            else:
                largura_fmt = f"{largura_m:.2f}"
            
            dado_formatado = (
                elemento, pos, f"{bitola:.1f}", qtd_area_fmt, f"{comp_m:.2f}", 
                largura_fmt, f"{peso_kg:.2f}", formato, str([round(m, 2) for m in medidas])
            )
            self.tree.insert("", "end", values=dado_formatado)
        
        # O total_kg e total_pecas na barra de status são os totais filtrados
        self.info_label.config(text=f"Total Filtrado: {total_pecas} barras | {total_kg:.2f} kg")

    
    def processar(self, inicial=False):
        arquivos_para_processar = self.arquivos_selecionados
        
        if not arquivos_para_processar and not inicial:
            messagebox.showwarning("Atenção", "Por favor, selecione os arquivos DXF/DWG primeiro!")
            return
        
        if not arquivos_para_processar and inicial:
            # Não faz nada, a inicialização é vazia
            return

        try:
            self.status_label.config(text="⏳ Processando arquivos com extração por coordenadas...")
            self.update()
            
            # Usa o motor real do core (extração por coordenadas Y-grouping)
            dados_completos, total_kg, total_pecas = processar_lajes(arquivos_para_processar)
            
            if dados_completos:
                # SUCESSO na leitura real
                self.dados_processados = dados_completos
                self.total_kg = total_kg
                self.total_pecas = total_pecas
                self.status_label.config(text=f"✅ Processamento concluído! {len(dados_completos)} posições extraídas.")
                print(f"✅ Sucesso: {len(dados_completos)} posições | {total_pecas} barras | {total_kg:.2f} kg")
                
            else:
                # FALHA na leitura real
                messagebox.showwarning(
                    "Falha na Leitura", 
                    "A extração do arquivo DXF retornou dados vazios.\n\n"
                    "Possíveis causas:\n"
                    "- Arquivo sem textos de tabela de armaduras\n"
                    "- Formato de texto não reconhecido\n"
                    "- Dados fragmentados fora do padrão esperado\n\n"
                    "Verifique o arquivo e tente novamente."
                )
                self.dados_processados, self.total_kg, self.total_pecas = [], 0.0, 0
                self.status_label.config(text="⚠️ Nenhum dado extraído do DXF.")

            # Atualiza o estado das lajes ativas com base nos novos dados
            elementos_atuais = set(dado[0] for dado in self.dados_processados)
            self.lajes_ativas = elementos_atuais # Ativa todos os novos elementos
            
            self.recarregar_treeview()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro fatal ao processar:\n{str(e)}")
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            self.dados_processados, self.total_kg, self.total_pecas = [], 0.0, 0
            self.status_label.config(text="❌ Erro fatal no processamento.")
            self.recarregar_treeview()

    def aplicar_filtro_producao(self) -> Tuple[List[Any], float, int]:
        if not self.dados_processados: return [], 0.0, 0
        
        elementos_processados = set(dado[0] for dado in self.dados_processados)
        if not self.lajes_ativas:
            self.lajes_ativas = elementos_processados

        dados_filtrados = [dado for dado in self.dados_processados if dado[0] in self.lajes_ativas]
        total_kg_filtrado = sum(dado[6] for dado in dados_filtrados)
        total_pecas_filtrado = int(round(sum(dado[3] for dado in dados_filtrados))) 
        
        return dados_filtrados, total_kg_filtrado, total_pecas_filtrado

    
    def gerenciar_producao(self):
        """Abre uma nova janela para gerenciar o filtro de lajes ativas."""
        
        elementos_unicos = sorted(list(set(dado[0] for dado in self.dados_processados)))
        
        if not elementos_unicos:
            messagebox.showwarning("Atenção", "Nenhum dado de laje carregado para gerenciar. Por favor, processe um projeto ou carregue o Mock.")
            return

        janela_gerencia = tk.Toplevel(self)
        janela_gerencia.title("📐 Gerenciar Produção: Seleção de Lajes")
        janela_gerencia.geometry("500x500")
        janela_gerencia.configure(bg="#1a3d2e")
        janela_gerencia.transient(self)
        
        frame_header = tk.Frame(janela_gerencia, bg="#0d2818", padx=10, pady=5)
        frame_header.pack(fill="x")
        tk.Label(frame_header, text="SELEÇÃO DE ELEMENTOS", bg="#0d2818", fg="#ff9800", font=("Arial", 12, "bold")).pack()
        
        # Frame de Rolagem
        canvas_scroll = tk.Canvas(janela_gerencia, bg="#1a3d2e", highlightthickness=0)
        canvas_scroll.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(janela_gerencia, orient="vertical", command=canvas_scroll.yview)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        
        frame_content = tk.Frame(canvas_scroll, bg="#1a3d2e")
        canvas_scroll.create_window((0, 0), window=frame_content, anchor="nw", width=450)

        # Variáveis de controle
        self.vars_selecao: Dict[str, tk.BooleanVar] = {}
        
        def toggle_all():
            current_state = not all(v.get() for v in self.vars_selecao.values())
            for var in self.vars_selecao.values():
                var.set(current_state)

        # Configuração dos Checkboxes
        for i, elemento in enumerate(elementos_unicos):
            var = tk.BooleanVar(value=elemento in self.lajes_ativas)
            self.vars_selecao[elemento] = var
            
            cb = tk.Checkbutton(
                frame_content,
                text=elemento,
                variable=var,
                bg="#1a3d2e",
                fg="white",
                selectcolor="#333333",
                font=("Arial", 10),
                anchor="w",
                width=40
            )
            cb.grid(row=i, column=0, sticky="ew", pady=2, padx=10)

        # Função de Aplicação
        def aplicar_selecao():
            lajes_selecionadas = {e for e, v in self.vars_selecao.items() if v.get()}
            
            if not lajes_selecionadas:
                messagebox.showwarning("Filtro Vazio", "Nenhuma laje selecionada. O Romaneio e Etiquetas ficarão vazios.")
            
            self.lajes_ativas = lajes_selecionadas
            self.salvar_estado_persistencia()
            self.recarregar_treeview()
            janela_gerencia.destroy()
            self.status_label.config(text=f"✅ Filtro de Produção aplicado: {len(lajes_selecionadas)} Elemento(s) ativo(s).")
        
        # Botões de Ação
        frame_botoes = tk.Frame(janela_gerencia, bg="#1a3d2e", pady=10)
        frame_botoes.pack(fill="x", padx=10)
        
        tk.Button(
            frame_botoes,
            text="Aplicar Filtro",
            command=aplicar_selecao,
            bg="#2e7d32", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5, cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            frame_botoes,
            text="Selecionar Todos / Nenhum",
            command=toggle_all,
            bg="#ff6f00", fg="white", font=("Arial", 10), padx=15, pady=5, cursor="hand2"
        ).pack(side="left", padx=10)
        
        tk.Button(
            frame_botoes,
            text="Cancelar",
            command=janela_gerencia.destroy,
            bg="#757575", fg="white", font=("Arial", 10), padx=15, pady=5, cursor="hand2"
        ).pack(side="right", padx=5)


        frame_content.update_idletasks()
        canvas_scroll.config(scrollregion=canvas_scroll.bbox("all"))

        # Rebinding para fechar a janela ao clicar fora
        janela_gerencia.bind('<Configure>', lambda e: canvas_scroll.config(scrollregion=canvas_scroll.bbox("all")))


    def gerar_romaneio(self):
        dados_filtrados, total_kg, total_pecas = self.aplicar_filtro_producao()

        if not dados_filtrados:
            messagebox.showwarning("Atenção", "Nenhum Elemento de Laje selecionado ou processado!")
            return
        
        janela = tk.Toplevel(self)
        janela.title("Romaneio de LAJES - Múltiplas Visualizações")
        janela.geometry("1000x700")
        janela.configure(bg="#0d2818")
        
        btn_frame = tk.Frame(janela, bg="#1a3d2e")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.aba_ativa = None
        self.texto_ativo = None
        
        def salvar_aba_ativa():
            if self.texto_ativo:
                self.salvar_txt(self.texto_ativo.get("1.0", "end-1c"))
        
        tk.Button(btn_frame, text="💾 Salvar TXT", command=salvar_aba_ativa, bg="#2e7d32", fg="white", font=("Arial", 10, "bold"), padx=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🖨️ Imprimir", command=lambda: messagebox.showinfo("Aviso", "Função Imprimir ainda não implementada."), bg="#6a1b9a", fg="white", font=("Arial", 10, "bold"), padx=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📊 Exportar Tudo Excel", command=self.exportar_excel, bg="#ff6f00", fg="white", font=("Arial", 10, "bold"), padx=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="❌ Fechar", command=janela.destroy, bg="#757575", fg="white", font=("Arial", 10), padx=10).pack(side="right", padx=5)
        
        notebook = ttk.Notebook(janela)
        notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        def gerar_conteudo_formatado(dados, titulo, agrupamento_chave=None):
            conteudo = []
            conteudo.append("=" * 80)
            conteudo.append(f"                {titulo}")
            conteudo.append("=" * 80)
            conteudo.append(f"Obra:      {self.var_obra.get()}")
            conteudo.append(f"Laje:      {self.var_pavimento.get()}")
            conteudo.append(f"Lajes Ativas: {', '.join(sorted(list(self.lajes_ativas)) or ['TODAS'])}")
            conteudo.append(f"Data:      {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            conteudo.append("=" * 80)
            conteudo.append("")

            if not dados:
                 conteudo.append("Nenhum dado encontrado.")
                 conteudo.append("=" * 80)
                 return "\n".join(conteudo)
            
            # (elemento, pos_ou_tipo, bitola, qtde_ou_area, comp_m, largura_m, peso_kg, formato_dobra, medidas_m)
            
            if agrupamento_chave == 'GERAL':
                elemento_atual = None
                for dado in dados:
                    elemento, pos, bitola, qtd_area, comp_m, _, peso_kg, formato_dobra, _ = dado
                    if elemento != elemento_atual:
                        elemento_atual = elemento
                        conteudo.append("")
                        conteudo.append(f">>> {elemento_atual}")
                        conteudo.append("-" * 60)
                    
                    qtd_fmt = f"Qtd: {int(round(qtd_area)):<6}"
                    comp_fmt = f"Comp: {comp_m:.2f} m"

                    conteudo.append(
                        f"    {pos:<12} Ø{bitola:<6.1f} {qtd_fmt:<18} "
                        f"{comp_fmt:<18} Peso: {peso_kg:<8.2f}kg | Forma: {formato_dobra}"
                    )

            elif agrupamento_chave == 'POSICAO':
                posicoes_agrupadas = {}
                for dado in dados:
                    posicao = dado[1] # pos_ou_tipo
                    if posicao not in posicoes_agrupadas:
                        posicoes_agrupadas[posicao] = []
                    posicoes_agrupadas[posicao].append(dado)
                
                for posicao in sorted(posicoes_agrupadas.keys()):
                    conteudo.append("")
                    conteudo.append(f"╔{'═' * 78}╗")
                    conteudo.append(f"║ POSIÇÃO: {posicao:<69} ║")
                    conteudo.append(f"╚{'═' * 78}╝")
                    
                    subtotal_peso = 0.0
                    subtotal_barras = 0
                    
                    for dado in posicoes_agrupadas[posicao]:
                        elemento, _, bitola, qtd_area, comp_m, _, peso_kg, formato_dobra, _ = dado
                        qt = int(round(qtd_area))
                        conteudo.append(
                            f"      {elemento:<10} Ø{bitola:<6.1f} Qtd: {qt:<4} Comp: {comp_m:<6.2f}m  "
                            f"Peso: {peso_kg:<8.2f}kg | Forma: {formato_dobra}"
                        )
                        subtotal_peso += peso_kg
                        subtotal_barras += qtd_area

                    conteudo.append("  " + "-" * 60)
                    conteudo.append(f"  Subtotal {posicao}: Barras: {int(round(subtotal_barras))} | Peso: {subtotal_peso:.2f} kg")

            elif agrupamento_chave == 'BITOLA':
                bitolas_agrupadas = {}
                for dado in dados:
                    bitola = dado[2]
                    if bitola not in bitolas_agrupadas:
                        bitolas_agrupadas[bitola] = []
                    bitolas_agrupadas[bitola].append(dado)
                
                for bitola in sorted(bitolas_agrupadas.keys(), reverse=True):
                    conteudo.append("")
                    conteudo.append(f"╔{'═' * 78}╗")
                    conteudo.append(f"║ BITOLA: Ø {bitola:.1f} mm{' ' * (66 - len(f'{bitola:.1f}'))} ║")
                    conteudo.append(f"╚{'═' * 78}╝")

                    subtotal_peso = 0.0
                    subtotal_barras = 0
                    
                    for dado in bitolas_agrupadas[bitola]:
                        elemento, pos, _, qtd_area, comp_m, _, peso_kg, formato_dobra, _ = dado
                        qt = int(round(qtd_area))
                        conteudo.append(
                            f"      {elemento}/{pos:<10} Qtd: {qt:<4} Comp: {comp_m:<6.2f}m  "
                            f"Peso: {peso_kg:<8.2f}kg | Forma: {formato_dobra}"
                        )
                        subtotal_peso += peso_kg
                        subtotal_barras += qtd_area

                    conteudo.append("  " + "-" * 60)
                    conteudo.append(f"  Subtotal Ø {bitola:.1f}mm: Barras: {int(round(subtotal_barras))} | Peso: {subtotal_peso:.2f} kg")
                    percentual = (subtotal_peso / total_kg) * 100 if total_kg > 0 else 0
                    conteudo.append(f"    Percentual do total: {percentual:.1f}%")
            
            # Rodapé final
            conteudo.append("")
            conteudo.append("=" * 80)
            conteudo.append(f"TOTAL GERAL DE PRODUÇÃO: {total_pecas} barras | {total_kg:.2f} kg")
            conteudo.append("=" * 80)
            
            return "\n".join(conteudo)

        # ========== ABA 1: ROMANEIO GERAL ==========
        frame_geral = tk.Frame(notebook, bg="#1e1e1e")
        notebook.add(frame_geral, text="📋 Romaneio Geral")
        texto_geral = ScrolledText(frame_geral, bg="#1e1e1e", fg="#ff9800", font=("Courier New", 10), wrap="none")
        texto_geral.pack(fill="both", expand=True)
        conteudo_geral = gerar_conteudo_formatado(dados_filtrados, "ROMANEIO DE LAJES - GERAL", 'GERAL')
        texto_geral.insert("1.0", conteudo_geral)

        # ========== ABA 2: POR POSIÇÃO ==========
        frame_posicao = tk.Frame(notebook, bg="#1e1e1e")
        notebook.add(frame_posicao, text="📌 Por Posição/Tipo")
        texto_posicao = ScrolledText(frame_posicao, bg="#1e1e1e", fg="#1976d2", font=("Courier New", 10), wrap="none")
        texto_posicao.pack(fill="both", expand=True)
        conteudo_posicao = gerar_conteudo_formatado(dados_filtrados, "ROMANEIO DE LAJES - POR POSIÇÃO/TIPO", 'POSICAO')
        texto_posicao.insert("1.0", conteudo_posicao)

        # ========== ABA 3: POR BITOLA ==========
        frame_bitola = tk.Frame(notebook, bg="#1e1e1e")
        notebook.add(frame_bitola, text="📏 Por Bitola")
        texto_bitola = ScrolledText(frame_bitola, bg="#1e1e1e", fg="#4caf50", font=("Courier New", 10), wrap="none")
        texto_bitola.pack(fill="both", expand=True)
        conteudo_bitola = gerar_conteudo_formatado(dados_filtrados, "ROMANEIO DE LAJES - POR BITOLA", 'BITOLA')
        texto_bitola.insert("1.0", conteudo_bitola)

        def on_tab_changed(event):
            selected_tab = notebook.index(notebook.select())
            textos = [texto_geral, texto_posicao, texto_bitola]
            if selected_tab < len(textos):
                self.texto_ativo = textos[selected_tab]
        
        notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
        self.texto_ativo = texto_geral

    def gerar_romaneio_conferencia(self):
        messagebox.showinfo("Aviso", "Funcionalidade de Check List para Lajes ainda não implementada.")
        pass

    # --- ETIQUETAS E DESENHO ---
    def navegar_proximo(self):
        total_paginas = math.ceil(len(self.dados_etiquetas_filtrados) / self.pecas_por_pagina)
        self.indice_etiqueta_pagina = (self.indice_etiqueta_pagina + 1) % total_paginas
        self.desenhar_pagina_etiquetas_lajes(self.indice_etiqueta_pagina)

    def navegar_anterior(self):
        total_paginas = math.ceil(len(self.dados_etiquetas_filtrados) / self.pecas_por_pagina)
        self.indice_etiqueta_pagina = (self.indice_etiqueta_pagina - 1 + total_paginas) % total_paginas
        self.desenhar_pagina_etiquetas_lajes(self.indice_etiqueta_pagina)

    def desenhar_esquema_geometria(self, canvas: tk.Canvas, forma: str, medidas_m: List[float], x_base: int, y_base: int):
        canvas.delete("desenho") 
        x, y = x_base, y_base
        escala = 10 

        medidas_cm = [m * 100 for m in medidas_m]
        
        if forma.endswith("(TELA)"):
             pass
        else:
            def draw_line(x1, y1, x2, y2, tag):
                canvas.create_line(x1, y1, x2, y2, width=3, fill="black", tags=("desenho", tag))
            
            if forma.startswith("RETA"):
                if medidas_cm: draw_line(x, y, x + medidas_cm[0] * escala, y, "reta")
            elif forma.startswith("DOBRA L") or forma.startswith("BARRA L"):
                if len(medidas_cm) >= 2:
                    A_pix, B_pix = medidas_cm[0] * escala, medidas_cm[1] * escala
                    draw_line(x, y, x + A_pix, y, "l_a")
                    draw_line(x + A_pix, y, x + A_pix, y - B_pix, "l_b")
            elif forma.startswith("BARRA U"):
                if len(medidas_cm) >= 3:
                    A_pix, B_pix, C_pix = medidas_cm[0] * escala, medidas_cm[1] * escala, medidas_cm[2] * escala
                    draw_line(x, y, x, y + A_pix, "u_a")
                    draw_line(x, y + A_pix, x + B_pix, y + A_pix, "u_b")
                    draw_line(x + B_pix, y + A_pix, x + B_pix, y + A_pix - C_pix, "u_c")
            
        canvas.create_text(x_base + 100, y_base - 70, text="Esquema de Geometria (cm)", font=("Arial", 9, "bold"), fill="#333", tags="desenho")


    def desenhar_etiqueta_card(self, frame_pai: tk.Frame, dado: Tuple[str, str, float, float, float, float, float, str, List[float]], indice_global: int):
        elemento, pos, bitola, qtd_area, comp_m, largura_m, peso_kg, formato_dobra, medidas_m = dado
        data_lancamento = datetime.now().strftime('%d/%m/%Y')
        
        card = tk.Frame(frame_pai, width=420, height=300, bg="white", bd=2, relief="groove")
        card.grid_propagate(False)
        
        header_context = tk.Frame(card, bg="#f0f0f0", padx=5, pady=2)
        header_context.pack(fill="x")
        
        tk.Label(header_context, text=f"OBRA: {self.var_obra.get()}", font=("Arial", 7, "bold"), bg="#f0f0f0", fg="#003366").grid(row=0, column=0, sticky="w")
        tk.Label(header_context, text=f"LAJE/PAV: {self.var_pavimento.get()}", font=("Arial", 7, "bold"), bg="#f0f0f0", fg="#003366").grid(row=0, column=1, sticky="w", padx=10)
        tk.Label(header_context, text=f"LANÇAMENTO: {data_lancamento}", font=("Arial", 7), bg="#f0f0f0", fg="#555").grid(row=0, column=2, sticky="e", padx=5)
        header_context.grid_columnconfigure(2, weight=1)

        header_title = tk.Frame(card, bg="#003366")
        header_title.pack(fill="x", ipady=5)
        
        tk.Label(header_title, text=f"PEÇA #{indice_global+1} | {elemento}", font=("Arial", 11, "bold"), bg="#003366", fg="white").pack(side="left", padx=5)
        tk.Label(header_title, text=f"Ø {bitola:.1f} MM", font=("Arial", 11, "bold"), bg="#003366", fg="#ffcc00").pack(side="right", padx=5)

        detail_frame = tk.Frame(card, bg="white", padx=5, pady=5)
        detail_frame.pack(fill="x")
        
        if formato_dobra.endswith("(TELA)"):
            qtde_info = f"ÁREA: {qtd_area:.2f} m²"
            if isinstance(largura_m, str):
                comp_info = f"DIMENSÕES: {comp_m:.2f} m ({largura_m})"
            else:
                comp_info = f"DIMENSÕES: {comp_m:.2f} x {largura_m:.2f} m"
        else:
            qtde_info = f"QTD: {int(round(qtd_area))} pçs"
            if isinstance(largura_m, str):
                comp_info = f"COMP. CORTE: {comp_m:.2f} m ({largura_m})"
            else:
                comp_info = f"COMP. CORTE: {comp_m:.2f} m"
        
        tk.Label(detail_frame, text=qtde_info, font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5)
        tk.Label(detail_frame, text=comp_info, font=("Arial", 10, "bold"), fg="#1976d2").grid(row=1, column=0, sticky="w", padx=5)
        tk.Label(detail_frame, text=f"FORMA: {formato_dobra}", font=("Arial", 10), fg="#333").grid(row=2, column=0, sticky="w", padx=5)
        
        draw_canvas = tk.Canvas(card, bg="#f5f5f5", width=380, height=150, bd=1, relief="sunken")
        draw_canvas.pack(padx=5, pady=5)
        
        self.desenhar_esquema_geometria(draw_canvas, formato_dobra, medidas_m, x_base=100, y_base=100)

        btn_edit = tk.Button(
            card, text="✏️ Editar Dados", command=lambda i=indice_global: self.abrir_edicao_avancada(i),
            bg="#ff5722", fg="white", font=("Arial", 9, "bold"), pady=2, cursor="hand2"
        )
        btn_edit.pack(fill="x", padx=5, pady=(0, 5))
        
        return card

    def desenhar_pagina_etiquetas_lajes(self, pagina_indice: int):
        if not self.dados_etiquetas_filtrados: return
        self.indice_etiqueta_pagina = pagina_indice
        start_index = pagina_indice * self.pecas_por_pagina
        end_index = min(start_index + self.pecas_por_pagina, len(self.dados_etiquetas_filtrados))
        pecas_na_pagina = self.dados_etiquetas_filtrados[start_index:end_index]
        
        for widget in self.frame_grid.winfo_children(): widget.destroy()

        total_pecas_filtradas = len(self.dados_etiquetas_filtrados)
        total_paginas = math.ceil(total_pecas_filtradas / self.pecas_por_pagina)
        self.contagem_label.config(text=f"Página {pagina_indice + 1} de {total_paginas} ({start_index + 1} a {end_index} de {total_pecas_filtradas})")

        # Se houver PNGs gerados, mostrar preview no padrão das vigas/pilares
        if PIL_DISPONIVEL and hasattr(self, 'caminhos_etiquetas_geradas') and self.caminhos_etiquetas_geradas:
            self._etiqueta_images = []
            for i in range(start_index, end_index):
                row = (i - start_index) // 2
                col = (i - start_index) % 2
                if i >= len(self.caminhos_etiquetas_geradas):
                    continue
                caminho_png = self.caminhos_etiquetas_geradas[i]
                try:
                    img = Image.open(caminho_png)
                    new_w = 420
                    new_h = int(round(new_w * (img.height / img.width)))
                    img = img.resize((new_w, new_h))
                    img_tk = ImageTk.PhotoImage(img)
                    lbl = tk.Label(self.frame_grid, image=img_tk, bg="#ffffff")
                    lbl.image = img_tk
                    self._etiqueta_images.append(img_tk)
                    lbl.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                except Exception:
                    card = self.desenhar_etiqueta_card(self.frame_grid, self.dados_etiquetas_filtrados[i], indice_global=i)
                    card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        else:
            for i, dado in enumerate(pecas_na_pagina):
                row = i // 2
                col = i % 2
                card = self.desenhar_etiqueta_card(self.frame_grid, dado, indice_global=(start_index + i))
                card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        self.frame_grid.grid_columnconfigure(0, weight=1)
        self.frame_grid.grid_columnconfigure(1, weight=1)
        self.janela_etiq.update_idletasks()


    def abrir_edicao_avancada(self, indice_global: int):
        if not self.dados_etiquetas_filtrados:
            messagebox.showwarning("Atenção", "Nenhuma peça filtrada para edição.")
            return

        messagebox.showinfo("Aviso", "Edição Avançada aberta para demonstração. Funcionalidade completa de edição está ativa.")
        # Lógica completa de edição seria implementada aqui
        # janela_edit.destroy()

    def gerar_romaneio(self):
        """Gera romaneio com 4 abas: Geral, Por Tipo, Por Bitola e Resumo Executivo."""
        dados_filtrados, total_kg, total_pecas = self.aplicar_filtro_producao()
        
        if not dados_filtrados:
            messagebox.showwarning("Atenção", "Nenhum Elemento de Laje selecionado ou processado!")
            return

        # Criar janela
        janela_romaneio = tk.Toplevel(self)
        janela_romaneio.title("Romaneio de Lajes - EngenhariaPlanPro")
        janela_romaneio.geometry("1000x700")
        janela_romaneio.configure(bg="#1e1e1e")

        # Botões superiores
        frame_btns = tk.Frame(janela_romaneio, bg="#2d2d2d")
        frame_btns.pack(fill="x", pady=10, padx=10)

        tk.Button(
            frame_btns,
            text="💾 Salvar TXT",
            command=lambda: self.salvar_txt(texto_geral.get("1.0", "end-1c")),
            bg="#4caf50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side="left", padx=5)

        tk.Button(
            frame_btns,
            text="📋 Copiar Geral",
            command=lambda: self.copiar_para_clipboard(texto_geral.get("1.0", "end-1c")),
            bg="#2196f3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side="left", padx=5)

        # Notebook com 4 abas
        notebook = ttk.Notebook(janela_romaneio)
        notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ========== ABA 1: ROMANEIO GERAL ==========
        frame_geral = tk.Frame(notebook, bg="#1e1e1e")
        notebook.add(frame_geral, text="📋 Romaneio Geral")

        texto_geral = ScrolledText(
            frame_geral,
            bg="#1e1e1e",
            fg="#ff9800",
            font=("Courier New", 10),
            wrap="none"
        )
        texto_geral.pack(fill="both", expand=True)

        # Gerar conteúdo do romaneio geral
        conteudo_geral = []
        conteudo_geral.append("=" * 80)
        conteudo_geral.append("                    ROMANEIO DE LAJES - GERAL")
        conteudo_geral.append("=" * 80)
        conteudo_geral.append(f"Obra:      {self.var_obra.get()}")
        conteudo_geral.append(f"Pavimento: {self.var_pavimento.get()}")
        conteudo_geral.append(f"Data:      {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        conteudo_geral.append("=" * 80)
        conteudo_geral.append("")

        laje_atual = None
        for dado in dados_filtrados:
            if dado[0] != laje_atual:
                laje_atual = dado[0]
                conteudo_geral.append("")
                conteudo_geral.append(f">>> {laje_atual}")
                conteudo_geral.append("-" * 60)

            conteudo_geral.append(
                f"    {dado[1]:<10} Ø{dado[2]:<6.1f} Qtd: {int(dado[3]):<4} "
                f"Comp: {dado[4]:<6.2f}m  Peso: {dado[6]:<8.2f}kg  {dado[7]}"
            )

        conteudo_geral.append("")
        conteudo_geral.append("=" * 80)
        conteudo_geral.append(f"TOTAL GERAL: {total_pecas} barras | {total_kg:.2f} kg")
        conteudo_geral.append("=" * 80)

        texto_geral.insert("1.0", "\n".join(conteudo_geral))

        # ========== ABA 2: POR TIPO DE BARRA ==========
        frame_tipo = tk.Frame(notebook, bg="#1e1e1e")
        notebook.add(frame_tipo, text="🔧 Por Tipo")

        texto_tipo = ScrolledText(
            frame_tipo,
            bg="#1e1e1e",
            fg="#00bcd4",
            font=("Courier New", 10),
            wrap="none"
        )
        texto_tipo.pack(fill="both", expand=True)

        # Separar por tipo
        tipos_agrupados = {}
        for dado in dados_filtrados:
            pos = dado[1]
            bitola = dado[2]
            comp = dado[4]
            formato = dado[7]
            tipo = AnalisadorGeometricoLajes.identificar_tipo_laje(pos, bitola, comp, formato)

            if tipo not in tipos_agrupados:
                tipos_agrupados[tipo] = []
            tipos_agrupados[tipo].append(dado)

        conteudo_tipo = []
        conteudo_tipo.append("=" * 80)
        conteudo_tipo.append("                ROMANEIO DE LAJES - POR TIPO DE BARRA")
        conteudo_tipo.append("=" * 80)
        conteudo_tipo.append(f"Obra:      {self.var_obra.get()}")
        conteudo_tipo.append(f"Pavimento: {self.var_pavimento.get()}")
        conteudo_tipo.append(f"Data:      {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        conteudo_tipo.append("=" * 80)

        for tipo in sorted(tipos_agrupados.keys()):
            conteudo_tipo.append("")
            conteudo_tipo.append(f"╔{'═' * 78}╗")
            conteudo_tipo.append(f"║ TIPO: {tipo:<70} ║")
            conteudo_tipo.append(f"╚{'═' * 78}╝")
            conteudo_tipo.append("")

            laje_atual = None
            subtotal_tipo = 0.0
            subtotal_barras = 0

            for dado in tipos_agrupados[tipo]:
                if dado[0] != laje_atual:
                    laje_atual = dado[0]
                    conteudo_tipo.append(f"  ▶ {laje_atual}")
                    conteudo_tipo.append("  " + "-" * 60)

                conteudo_tipo.append(
                    f"      {dado[1]:<10} Ø{dado[2]:<6.1f} Qtd: {int(dado[3]):<4} "
                    f"Comp: {dado[4]:<6.2f}m  Peso: {dado[6]:<8.2f}kg"
                )
                subtotal_tipo += dado[6]
                subtotal_barras += int(dado[3])

            conteudo_tipo.append("  " + "-" * 60)
            conteudo_tipo.append(f"  Subtotal {tipo}:")
            conteudo_tipo.append(f"    Barras: {subtotal_barras} | Peso: {subtotal_tipo:.2f} kg")
            percent = (subtotal_tipo / total_kg * 100) if total_kg > 0 else 0
            conteudo_tipo.append(f"    Percentual: {percent:.1f}%")

        conteudo_tipo.append("")
        conteudo_tipo.append("=" * 80)
        conteudo_tipo.append(f"TOTAL GERAL: {total_pecas} barras | {total_kg:.2f} kg")
        conteudo_tipo.append("=" * 80)

        texto_tipo.insert("1.0", "\n".join(conteudo_tipo))

        # ========== ABA 3: POR BITOLA ==========
        frame_bitola = tk.Frame(notebook, bg="#1e1e1e")
        notebook.add(frame_bitola, text="📏 Por Bitola")

        texto_bitola = ScrolledText(
            frame_bitola,
            bg="#1e1e1e",
            fg="#4caf50",
            font=("Courier New", 10),
            wrap="none"
        )
        texto_bitola.pack(fill="both", expand=True)

        # Agrupar por bitola
        bitolas_agrupadas = {}
        for dado in dados_filtrados:
            bitola = dado[2]
            if bitola not in bitolas_agrupadas:
                bitolas_agrupadas[bitola] = []
            bitolas_agrupadas[bitola].append(dado)

        conteudo_bitola = []
        conteudo_bitola.append("=" * 80)
        conteudo_bitola.append("                  ROMANEIO DE LAJES - POR BITOLA")
        conteudo_bitola.append("=" * 80)
        conteudo_bitola.append(f"Obra:      {self.var_obra.get()}")
        conteudo_bitola.append(f"Pavimento: {self.var_pavimento.get()}")
        conteudo_bitola.append(f"Data:      {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        conteudo_bitola.append("=" * 80)

        for bitola in sorted(bitolas_agrupadas.keys()):
            conteudo_bitola.append("")
            conteudo_bitola.append(f"╔{'═' * 78}╗")
            conteudo_bitola.append(f"║ BITOLA: Ø {bitola:.1f} mm{' ' * (66 - len(f'{bitola:.1f}'))} ║")
            conteudo_bitola.append(f"╚{'═' * 78}╝")
            conteudo_bitola.append("")

            laje_atual = None
            subtotal_bitola = 0.0
            subtotal_barras = 0

            for dado in bitolas_agrupadas[bitola]:
                if dado[0] != laje_atual:
                    laje_atual = dado[0]
                    conteudo_bitola.append(f"  ▶ {laje_atual}")
                    conteudo_bitola.append("  " + "-" * 60)

                conteudo_bitola.append(
                    f"      {dado[1]:<10} Qtd: {int(dado[3]):<4} "
                    f"Comp: {dado[4]:<6.2f}m  Peso: {dado[6]:<8.2f}kg  {dado[7]}"
                )
                subtotal_bitola += dado[6]
                subtotal_barras += int(dado[3])

            conteudo_bitola.append("  " + "-" * 60)
            conteudo_bitola.append(f"  Subtotal Ø{bitola:.1f}mm:")
            conteudo_bitola.append(f"    Barras: {subtotal_barras} | Peso: {subtotal_bitola:.2f} kg")
            percent = (subtotal_bitola / total_kg * 100) if total_kg > 0 else 0
            conteudo_bitola.append(f"    Percentual: {percent:.1f}%")

        conteudo_bitola.append("")
        conteudo_bitola.append("=" * 80)
        conteudo_bitola.append(f"TOTAL GERAL: {total_pecas} barras | {total_kg:.2f} kg")
        conteudo_bitola.append("=" * 80)

        texto_bitola.insert("1.0", "\n".join(conteudo_bitola))

        # ========== ABA 4: RESUMO EXECUTIVO ==========
        frame_resumo = tk.Frame(notebook, bg="#1e1e1e")
        notebook.add(frame_resumo, text="📊 Resumo Executivo")

        texto_resumo = ScrolledText(
            frame_resumo,
            bg="#1e1e1e",
            fg="#ffc107",
            font=("Courier New", 10),
            wrap="none"
        )
        texto_resumo.pack(fill="both", expand=True)

        conteudo_resumo = []
        conteudo_resumo.append("=" * 80)
        conteudo_resumo.append("             RESUMO EXECUTIVO - LAJES")
        conteudo_resumo.append("=" * 80)
        conteudo_resumo.append(f"Obra:      {self.var_obra.get()}")
        conteudo_resumo.append(f"Pavimento: {self.var_pavimento.get()}")
        conteudo_resumo.append(f"Data:      {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        conteudo_resumo.append("=" * 80)
        conteudo_resumo.append("")

        # Resumo por bitola
        conteudo_resumo.append("DISTRIBUIÇÃO POR BITOLA:")
        conteudo_resumo.append("-" * 80)
        for bitola in sorted(bitolas_agrupadas.keys()):
            peso_bitola = sum(d[6] for d in bitolas_agrupadas[bitola])
            qtd_bitola = sum(int(d[3]) for d in bitolas_agrupadas[bitola])
            percent = (peso_bitola / total_kg * 100) if total_kg > 0 else 0
            conteudo_resumo.append(
                f"  Ø {bitola:>5.1f} mm: {qtd_bitola:>4} barras | {peso_bitola:>8.2f} kg | {percent:>5.1f}%"
            )

        conteudo_resumo.append("")
        conteudo_resumo.append("DISTRIBUIÇÃO POR TIPO:")
        conteudo_resumo.append("-" * 80)
        for tipo in sorted(tipos_agrupados.keys()):
            peso_tipo = sum(d[6] for d in tipos_agrupados[tipo])
            qtd_tipo = sum(int(d[3]) for d in tipos_agrupados[tipo])
            percent = (peso_tipo / total_kg * 100) if total_kg > 0 else 0
            conteudo_resumo.append(
                f"  {tipo:<25}: {qtd_tipo:>4} barras | {peso_tipo:>8.2f} kg | {percent:>5.1f}%"
            )

        conteudo_resumo.append("")
        conteudo_resumo.append("=" * 80)
        conteudo_resumo.append(f"TOTAL GERAL: {total_pecas} barras | {total_kg:.2f} kg")
        conteudo_resumo.append("=" * 80)

        texto_resumo.insert("1.0", "\n".join(conteudo_resumo))

        janela_romaneio.transient(self)

    def copiar_para_clipboard(self, texto):
        """Copia texto para a área de transferência."""
        self.clipboard_clear()
        self.clipboard_append(texto)
        messagebox.showinfo("Sucesso", "Conteúdo copiado para área de transferência!")

    # --- MÉTODOS AUXILIARES DE DESENHO DE ETIQUETAS ---

    def _desenhar_moldura_etiqueta(self, x, y, w, h):
        """Desenha moldura com marcas de corte."""
        self.canvas_etiq.create_rectangle(x, y, x + w, y + h, outline="#ff6f00", width=2, fill="white")
        tamanho_marca = 5
        cantos = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
        for px, py in cantos:
            self.canvas_etiq.create_line(px - tamanho_marca, py, px + tamanho_marca, py, width=1, fill="black")
            self.canvas_etiq.create_line(px, py - tamanho_marca, px, py + tamanho_marca, width=1, fill="black")

    def _desenhar_topo_etiqueta(self, x, y, w, h, elemento, pos_tipo, bitola, qtde, comp_m, largura_m=""):
        """Desenha o topo (93mm) com informações técnicas."""
        pxmm = 4
        def mm(v):
            return int(round(v * pxmm))

        faixa_larg = mm(10)
        os_w = mm(18)
        os_h = mm(30)

        # Área OS
        area_os_x1 = x + w - os_w - faixa_larg
        area_os_y1 = y
        area_os_x2 = x + w - faixa_larg
        area_os_y2 = y + os_h
        self.canvas_etiq.create_rectangle(area_os_x1, area_os_y1, area_os_x2, area_os_y2, outline="#000", width=1)
        self.canvas_etiq.create_text(area_os_x1 + 6, area_os_y1 + 6, text="OS", font=("Arial", 10, "bold"), anchor="nw")
        
        os_txt = f"{self.pagina_atual + 1}-{self.total_paginas}" if hasattr(self, 'total_paginas') else "-"
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
                from PIL import ImageDraw, ImageFont
                img_tmp = Image.new('RGBA', (mm(60), faixa_larg), (255, 255, 255, 0))
                draw = ImageDraw.Draw(img_tmp)
                try:
                    fnt = ImageFont.truetype("arial.ttf", 12)
                except Exception:
                    fnt = ImageFont.load_default()
                tw, th = draw.textsize(obra_nome, font=fnt)
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

        # Área útil
        area_util_x1 = x + 6
        area_util_x2 = area_os_x1 - 6
        area_util_w = max(0, area_util_x2 - area_util_x1)

        def _text_width(text, font):
            try:
                return draw.textlength(text, font=font)
            except Exception:
                return draw.textsize(text, font=font)[0]

        def _truncate_pil(text, font, max_width):
            if _text_width(text, font) <= max_width:
                return text
            ell = "..."
            max_w = max_width - _text_width(ell, font)
            if max_w <= 0:
                return ell
            while text and _text_width(text, font) > max_w:
                text = text[:-1]
            return text + ell

        def _draw_right(x_right, y, text, font, fill):
            w = _text_width(text, font)
            draw.text((x_right - w, y), text, font=font, fill=fill)

        def _truncate_text(text, max_width, font):
            try:
                import tkinter.font as tkfont
                f = tkfont.Font(font=font)
                if f.measure(text) <= max_width:
                    return text
                ell = "..."
                max_w = max_width - f.measure(ell)
                if max_w <= 0:
                    return ell
                while text and f.measure(text) > max_w:
                    text = text[:-1]
                return text + ell
            except Exception:
                return text

        step_y = mm(8)
        y_current = y + mm(12)

        # Cabeçalho
        self.canvas_etiq.create_text(area_util_x1, y_current, text="Sigla/Obra", font=("Arial", 8), anchor="nw")
        self.canvas_etiq.create_text(area_util_x1 + mm(24), y_current, text=obra_nome.replace(" ", " - "), font=("Arial", 11, "bold"), anchor="nw")
        y_current += step_y

        self.canvas_etiq.create_text(area_util_x1, y_current, text="Desenho", font=("Arial", 8), anchor="nw")
        tipo_exib = self._obter_tipo_formato(largura_m)
        self.canvas_etiq.create_text(area_util_x1 + mm(24), y_current, text=tipo_exib, font=("Arial", 10, "bold"), anchor="nw", fill="#e11d48")
        y_current += step_y

        self.canvas_etiq.create_text(area_util_x1, y_current, text="Pavimento", font=("Arial", 8), anchor="nw")
        pavimento = self.var_pavimento.get() if hasattr(self, 'var_pavimento') else "LAJE 1"
        self.canvas_etiq.create_text(area_util_x1 + mm(24), y_current, text=pavimento, font=("Arial", 10, "bold"), anchor="nw")
        y_current += step_y

        self.canvas_etiq.create_text(area_util_x1, y_current, text="Elemento", font=("Arial", 8), anchor="nw")
        pos_block_w = mm(24)
        elem_x = area_util_x1 + mm(24)
        elem_max_w = max(0, (area_util_x2 - pos_block_w - mm(4)) - elem_x)
        elemento_txt = _truncate_text(f"{elemento}", elem_max_w, ("Arial", 10, "bold"))
        self.canvas_etiq.create_text(elem_x, y_current, text=elemento_txt, font=("Arial", 10, "bold"), anchor="nw")
        self.canvas_etiq.create_text(area_util_x2 - mm(18), y_current, text="POS", font=("Arial", 8), anchor="e")
        self.canvas_etiq.create_text(area_util_x2 - mm(2), y_current, text=f"{pos_tipo}", font=("Arial", 12, "bold"), anchor="e")

        # Tabela técnica
        th = mm(8)
        tr = mm(10)
        tab_y1 = y + mm(45)
        tab_y2 = tab_y1 + th + tr
        tab_x = area_util_x1
        cw1 = mm(16)
        cw2 = mm(34)
        cw3 = mm(22)
        cw4 = mm(18)
        tot = cw1 + cw2 + cw3 + cw4
        if tot > area_util_w:
            escala = area_util_w / tot
            cw1 = int(cw1 * escala); cw2 = int(cw2 * escala); cw3 = int(cw3 * escala); cw4 = int(cw4 * escala)
        
        self.canvas_etiq.create_rectangle(tab_x, tab_y1, tab_x + cw1 + cw2 + cw3 + cw4, tab_y2, outline="#000", width=1)
        self.canvas_etiq.create_line(tab_x + cw1, tab_y1, tab_x + cw1, tab_y2)
        self.canvas_etiq.create_line(tab_x + cw1 + cw2, tab_y1, tab_x + cw1 + cw2, tab_y2)
        self.canvas_etiq.create_line(tab_x + cw1 + cw2 + cw3, tab_y1, tab_x + cw1 + cw2 + cw3, tab_y2)
        self.canvas_etiq.create_line(tab_x, tab_y1 + th, tab_x + cw1 + cw2 + cw3 + cw4, tab_y1 + th)
        
        self.canvas_etiq.create_text(tab_x + cw1//2, tab_y1 + th//2, text="Bitola", font=("Arial", 7, "bold"))
        self.canvas_etiq.create_text(tab_x + cw1 + cw2//2, tab_y1 + th//2, text="Compr. Unit.", font=("Arial", 7, "bold"))
        self.canvas_etiq.create_text(tab_x + cw1 + cw2 + cw3//2, tab_y1 + th//2, text="Peso", font=("Arial", 7, "bold"))
        self.canvas_etiq.create_text(tab_x + cw1 + cw2 + cw3 + cw4//2, tab_y1 + th//2, text="Qtde", font=("Arial", 7, "bold"))
        
        # Valores
        chave = (elemento, pos_tipo)
        if hasattr(self, 'medidas_customizadas') and chave in self.medidas_customizadas:
            bitola = self.medidas_customizadas[chave].get('bitola', bitola)
            comp_m = self.medidas_customizadas[chave].get('comp', comp_m)
            qtde = self.medidas_customizadas[chave].get('qtde', qtde)
        
        self.canvas_etiq.create_text(tab_x + cw1//2, tab_y1 + th + tr//2, text=f"{bitola:.2f}", font=("Arial", 8))
        self.canvas_etiq.create_text(tab_x + cw1 + cw2//2, tab_y1 + th + tr//2, text=f"{comp_m:.3f}", font=("Arial", 8))
        
        peso_val = 0.0
        try:
            from core.peso import peso_linear_kg_m
            peso_val = peso_linear_kg_m(float(bitola)) * float(comp_m) * float(qtde)
        except Exception as e:
            print(f"[peso] Falha ao calcular: {e}")
        self.canvas_etiq.create_text(tab_x + cw1 + cw2 + cw3//2, tab_y1 + th + tr//2, text=f"{peso_val:.2f}", font=("Arial", 8))
        self.canvas_etiq.create_text(tab_x + cw1 + cw2 + cw3 + cw4//2, tab_y1 + th + tr//2, text=f"{qtde}", font=("Arial", 8))

        # Desenho técnico (editável)
        margem_topo = mm(3)
        margem_lateral = mm(3)
        draw_area_x1 = area_util_x1 + margem_lateral
        draw_area_x2 = area_util_x2 - margem_lateral
        draw_area_y1 = tab_y2 + margem_topo
        draw_area_y2 = y + h - margem_topo

        if draw_area_x2 > draw_area_x1 and draw_area_y2 > draw_area_y1:
            draw_w = draw_area_x2 - draw_area_x1
            draw_h = draw_area_y2 - draw_area_y1

            chave = (elemento, pos_tipo)
            forma = None
            if hasattr(self, 'formas_customizadas') and chave in self.formas_customizadas:
                forma = self.formas_customizadas.get(chave)
            if not forma:
                forma = self._obter_forma_laje(elemento)

            medidas = self.medidas_customizadas.get(chave, {}) if hasattr(self, 'medidas_customizadas') else {}
            tag = self._sanitize_tag(f"desenho_{elemento}_{pos_tipo}")
            self._desenhar_forma_canvas(draw_area_x1, draw_area_y1, draw_w, draw_h, forma, medidas, comp_m, tag=tag)
            self.canvas_etiq.tag_bind(tag, "<Button-1>", lambda e, el=elemento, p=pos_tipo: self._editar_desenho_canvas(el, p))

    def _sanitize_tag(self, value: str) -> str:
        return re.sub(r"[^A-Za-z0-9_]+", "_", str(value))

    def _obter_forma_laje(self, elemento):
        elemento_upper = str(elemento).upper()
        if "NEG" in elemento_upper:
            return "dobra_dupla"
        return "reta"

    def _desenhar_forma_canvas(self, x, y, w, h, forma, medidas, comp_m, tag=None):
        zf = getattr(self, 'zoom_factor', 1.0)
        cx = x + w / 2
        cy = y + h / 2
        tag = tag or ""

        # Área de clique
        self.canvas_etiq.create_rectangle(x, y, x + w, y + h, outline="#e11d48", width=2, fill="white", tags=(tag,))

        corpo_cm = float(medidas.get('medida_corpo', comp_m * 100.0 if comp_m else 0))

        if forma == "dobra_dupla":
            # U com duas dobras (altura proporcional às medidas)
            left = x + w * 0.2
            right = x + w * 0.8
            bottom = y + h * 0.8
            leg_max_h = h * 0.55

            dobra_esq = float(medidas.get('medida_dobra', 25))
            dobra_dir = float(medidas.get('medida_dobra_2', 25))
            max_dobra = max(dobra_esq, dobra_dir, 1.0)
            leg_esq_h = leg_max_h * (dobra_esq / max_dobra)
            leg_dir_h = leg_max_h * (dobra_dir / max_dobra)

            top_esq = bottom - leg_esq_h
            top_dir = bottom - leg_dir_h

            self.canvas_etiq.create_line(left, bottom, right, bottom, width=int(3*zf), fill="#000", tags=(tag,))
            self.canvas_etiq.create_line(left, bottom, left, top_esq, width=int(3*zf), fill="#000", tags=(tag,))
            self.canvas_etiq.create_line(right, bottom, right, top_dir, width=int(3*zf), fill="#000", tags=(tag,))

            self.canvas_etiq.create_text(left - 8*zf, (top_esq + bottom) / 2, text=f"{dobra_esq:.0f}cm", font=("Arial", int(8*zf)), anchor="e", tags=(tag,))
            self.canvas_etiq.create_text(right + 8*zf, (top_dir + bottom) / 2, text=f"{dobra_dir:.0f}cm", font=("Arial", int(8*zf)), anchor="w", tags=(tag,))
            if corpo_cm > 0:
                self.canvas_etiq.create_text(cx, bottom + 10*zf, text=f"{corpo_cm:.0f}cm", font=("Arial", int(8*zf)), anchor="n", tags=(tag,))
        else:
            # Reta
            self.canvas_etiq.create_line(x + w * 0.15, cy, x + w * 0.85, cy, width=int(3*zf), fill="#000", tags=(tag,))
            if corpo_cm > 0:
                self.canvas_etiq.create_text(cx, cy - 10*zf, text=f"{corpo_cm:.0f}cm", font=("Arial", int(8*zf)), tags=(tag,))

    def _obter_tipo_formato(self, largura_m):
        """Determina se é NORMAL ou VARIÁVEL baseado na largura_m (que é string se variável)."""
        # Se largura_m é string, significa que a largura é VARIÁVEL (está escrita como texto)
        if isinstance(largura_m, str):
            return str(largura_m).upper()  # Retorna "VARIÁVEL", "NORMAL", ou o texto da coluna largura
        # Se for número, é NORMAL
        return "NORMAL"

    def _desenhar_secao_micro(self, x, y, w, h, elemento, pos_tipo, bitola, qtde, comp_m, largura_m=""):
        """Desenha seção micro (picote) com informação de NORMAL/VARIÁVEL."""
        obra_nome = self.var_obra.get() if hasattr(self, 'var_obra') else "OBRA 001"
        
        tipo_exib = self._obter_tipo_formato(largura_m)
        
        self.canvas_etiq.create_text(
            x + w//2, y + h//2,
            text=f"{obra_nome} | {elemento} | {pos_tipo} | ø{bitola:.1f} | {qtde}x{comp_m:.2f}m | {tipo_exib}",
            font=("Arial", 8, "bold"), fill="#000"
        )

    def _desenhar_picote(self, x, y, w):
        """Desenha linha tracejada de picote."""
        dash = (4, 4)
        self.canvas_etiq.create_line(x, y, x + w, y, dash=dash, fill="#999")

    def _editar_etiqueta_dados(self, idx, elemento, pos_tipo, bitola, qtde, comp_m):
        """Abre diálogo para editar dados da etiqueta."""
        chave = (elemento, pos_tipo)
        
        dialog = tk.Toplevel(self.janela_editor)
        dialog.title(f"Editar Etiqueta #{idx+1} - {elemento}/{pos_tipo}")
        dialog.geometry("520x400")
        dialog.configure(bg="#0d2818")
        
        dialog.update_idletasks()
        x = self.janela_editor.winfo_x() + 400
        y = self.janela_editor.winfo_y() + 200
        dialog.geometry(f"520x400+{x}+{y}")
        
        tk.Label(dialog, text=f"Editar: {elemento} {pos_tipo}", bg="#0d2818", fg="#ff9800", 
                font=("Arial", 11, "bold")).pack(pady=10)
        
        frame = tk.Frame(dialog, bg="#0d2818")
        frame.pack(padx=10, pady=5)
        
        tk.Label(frame, text="Bitola (mm):", bg="#0d2818", fg="white").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        var_bitola = tk.DoubleVar(value=bitola)
        tk.Entry(frame, textvariable=var_bitola, width=10, font=("Arial", 10)).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame, text="Comprimento (m):", bg="#0d2818", fg="white").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        var_comp = tk.DoubleVar(value=comp_m)
        tk.Entry(frame, textvariable=var_comp, width=10, font=("Arial", 10)).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame, text="Quantidade:", bg="#0d2818", fg="white").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        var_qtde = tk.IntVar(value=qtde)
        tk.Entry(frame, textvariable=var_qtde, width=10, font=("Arial", 10)).grid(row=2, column=1, padx=5, pady=5)
        
        def salvar():
            if not hasattr(self, 'medidas_customizadas'):
                self.medidas_customizadas = {}
            prev = self.medidas_customizadas.get(chave, {})
            self.medidas_customizadas[chave] = {
                **prev,
                'bitola': var_bitola.get(),
                'comp': var_comp.get(),
                'qtde': var_qtde.get()
            }
            self.desenhar_etiquetas_com_selecao()
            dialog.destroy()
        
        tk.Button(frame, text="✏️ Editar dobras/corpo", command=lambda: self._editar_desenho_canvas(elemento, pos_tipo),
              bg="#3498db", fg="white", font=("Arial", 10, "bold"), padx=12, pady=5).grid(row=3, column=0, columnspan=2, pady=8)
        tk.Button(frame, text="💾 Salvar", command=salvar, bg="#27ae60", fg="white", 
              font=("Arial", 10, "bold"), padx=15, pady=5).grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="❌ Cancelar", command=dialog.destroy, bg="#e74c3c", fg="white", 
              font=("Arial", 10), padx=15, pady=5).grid(row=5, column=0, columnspan=2)

    def _editar_desenho_canvas(self, elemento, pos_tipo):
        """Editar medidas do desenho (reta/dobra dupla)."""
        chave = (elemento, pos_tipo)
        forma = None
        if hasattr(self, 'formas_customizadas') and chave in self.formas_customizadas:
            forma = self.formas_customizadas.get(chave)
        if not forma:
            forma = self._obter_forma_laje(elemento)

        dialog = tk.Toplevel(self.janela_editor)
        dialog.title(f"Desenho - {elemento}/{pos_tipo}")
        dialog.geometry("420x260")
        dialog.configure(bg="#0d2818")

        dialog.update_idletasks()
        x = self.janela_editor.winfo_x() + 420
        y = self.janela_editor.winfo_y() + 220
        dialog.geometry(f"420x260+{x}+{y}")

        tk.Label(dialog, text=f"Desenho: {elemento} {pos_tipo}", bg="#0d2818", fg="#ff9800",
                 font=("Arial", 11, "bold")).pack(pady=10)

        frame = tk.Frame(dialog, bg="#0d2818")
        frame.pack(padx=10, pady=5, fill="x")

        medidas = self.medidas_customizadas.get(chave, {}) if hasattr(self, 'medidas_customizadas') else {}
        comp_atual = float(medidas.get('comp', 0)) if 'comp' in medidas else None
        if comp_atual is None or comp_atual == 0:
            try:
                for item in self.dados_etiquetas_filtrados:
                    if item[0] == elemento and item[1] == pos_tipo:
                        comp_atual = float(item[4])
                        break
            except Exception:
                comp_atual = 0.0
        corpo_atual = float(medidas.get('medida_corpo', comp_atual * 100.0 if comp_atual else 0))

        if forma == "dobra_dupla":
            tk.Label(frame, text="Dobra esquerda (cm):", bg="#0d2818", fg="white").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            var_dobra_esq = tk.DoubleVar(value=float(medidas.get('medida_dobra', 25)))
            tk.Entry(frame, textvariable=var_dobra_esq, width=10).grid(row=0, column=1, padx=5, pady=5)

            tk.Label(frame, text="Dobra direita (cm):", bg="#0d2818", fg="white").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            var_dobra_dir = tk.DoubleVar(value=float(medidas.get('medida_dobra_2', 25)))
            tk.Entry(frame, textvariable=var_dobra_dir, width=10).grid(row=1, column=1, padx=5, pady=5)

            tk.Label(frame, text="Corpo (cm):", bg="#0d2818", fg="white").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            var_corpo = tk.DoubleVar(value=corpo_atual)
            tk.Entry(frame, textvariable=var_corpo, width=10).grid(row=2, column=1, padx=5, pady=5)
        else:
            tk.Label(frame, text="Comprimento (m):", bg="#0d2818", fg="white").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            var_comp = tk.DoubleVar(value=float(comp_atual) if comp_atual else 0.0)
            tk.Entry(frame, textvariable=var_comp, width=10).grid(row=0, column=1, padx=5, pady=5)

            tk.Label(frame, text="Corpo (cm):", bg="#0d2818", fg="white").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            var_corpo = tk.DoubleVar(value=corpo_atual)
            tk.Entry(frame, textvariable=var_corpo, width=10).grid(row=1, column=1, padx=5, pady=5)

        def salvar():
            if not hasattr(self, 'medidas_customizadas'):
                self.medidas_customizadas = {}
            if forma == "dobra_dupla":
                self.medidas_customizadas[chave] = {
                    **self.medidas_customizadas.get(chave, {}),
                    'medida_dobra': var_dobra_esq.get(),
                    'medida_dobra_2': var_dobra_dir.get(),
                    'medida_corpo': var_corpo.get()
                }
            else:
                self.medidas_customizadas[chave] = {
                    **self.medidas_customizadas.get(chave, {}),
                    'comp': var_comp.get(),
                    'medida_corpo': var_corpo.get()
                }
            self.desenhar_etiquetas_com_selecao()
            dialog.destroy()

        tk.Button(frame, text="💾 Salvar", command=salvar, bg="#27ae60", fg="white",
                  font=("Arial", 10, "bold"), padx=15, pady=5).grid(row=3, column=0, columnspan=2, pady=15)
        tk.Button(frame, text="❌ Cancelar", command=dialog.destroy, bg="#e74c3c", fg="white",
                  font=("Arial", 10), padx=15, pady=5).grid(row=4, column=0, columnspan=2)

    def _gerar_png_etiqueta_editor(self, idx, elemento, pos_tipo, bitola, qtde, comp_m, pasta_destino, largura_m="", formato_dobra=""):
        """Gera PNG com o mesmo layout do editor (100x150mm, 3 picotes)."""
        from PIL import Image, ImageDraw, ImageFont
        import os

        PX_MM = 11.811  # 300 DPI

        def mm(v):
            return int(round(v * PX_MM))

        largura = mm(100)
        altura = mm(150)
        altura_topo = mm(93)
        altura_picote = mm(18)
        espaco_picote = mm(1)

        img = Image.new("RGB", (largura, altura), "white")
        draw = ImageDraw.Draw(img)

        def _text_width(text, font):
            try:
                return draw.textlength(text, font=font)
            except Exception:
                return draw.textsize(text, font=font)[0]

        def _truncate_pil(text, font, max_width):
            if _text_width(text, font) <= max_width:
                return text
            ell = "..."
            max_w = max_width - _text_width(ell, font)
            if max_w <= 0:
                return ell
            while text and _text_width(text, font) > max_w:
                text = text[:-1]
            return text + ell

        def _draw_right(x_right, y, text, font, fill):
            w = _text_width(text, font)
            draw.text((x_right - w, y), text, font=font, fill=fill)

        try:
            font_small = ImageFont.truetype("arial.ttf", 32)
            font_tiny = ImageFont.truetype("arial.ttf", 28)
            font_bold = ImageFont.truetype("arialbd.ttf", 36)
            font_pos = ImageFont.truetype("arialbd.ttf", 42)
            font_picote = ImageFont.truetype("arialbd.ttf", 38)  # Fonte grande para picotes
        except Exception:
            font_small = ImageFont.load_default()
            font_tiny = font_small
            font_bold = font_small
            font_pos = font_small
            font_picote = font_small

        # Moldura topo
        draw.rectangle([(0, 0), (largura, altura_topo)], outline="#666666", width=3)

        # Bloco OS
        faixa_larg = mm(10)
        os_w = mm(18)
        os_h = mm(30)
        area_os_x1 = largura - os_w - faixa_larg
        area_os_y1 = 0
        area_os_x2 = largura - faixa_larg
        area_os_y2 = os_h
        draw.rectangle([(area_os_x1, area_os_y1), (area_os_x2, area_os_y2)], outline="#000000", width=2)
        draw.text((area_os_x1 + mm(2), area_os_y1 + mm(2)), "OS", font=font_small, fill="#000000")

        os_txt = f"{self.pagina_atual + 1}-{self.total_paginas}" if hasattr(self, 'total_paginas') else "-"
        linhas_os = os_txt.split("-")
        start_y = area_os_y1 + os_h // 2 - mm(3)
        espaco_linha = mm(4)
        for i, linha in enumerate(linhas_os):
            draw.text(((area_os_x1 + area_os_x2) // 2, start_y + i * espaco_linha), linha, font=font_bold, fill="#000000", anchor="mm")

        # Faixa vertical com obra
        faixa_x1 = largura - faixa_larg
        faixa_x2 = largura
        draw.rectangle([(faixa_x1, 0), (faixa_x2, altura_topo)], outline="#000000", width=2)
        obra_nome = self.var_obra.get() if hasattr(self, 'var_obra') else "OBRA.001"
        try:
            img_tmp = Image.new('RGBA', (mm(60), faixa_larg), (255, 255, 255, 0))
            dtmp = ImageDraw.Draw(img_tmp)
            try:
                fnt = ImageFont.truetype("arial.ttf", 28)
            except Exception:
                fnt = ImageFont.load_default()
            tw, th = dtmp.textsize(obra_nome, font=fnt)
            text_x = (img_tmp.width - tw) // 2
            text_y = (img_tmp.height - th) // 2
            dtmp.text((text_x, text_y), obra_nome, fill=(0, 0, 0, 255), font=fnt)
            img_tmp = img_tmp.rotate(90, expand=True)
            img.paste(img_tmp, (faixa_x1 + (faixa_larg - img_tmp.width) // 2, (altura_topo - img_tmp.height) // 2), img_tmp)
        except Exception:
            pass

        # Área útil
        area_util_x1 = mm(12)  # Margem esquerda maior
        area_util_x2 = area_os_x1 - mm(8)  # Margem direita maior
        area_util_w = max(0, area_util_x2 - area_util_x1)

        step_y = mm(8)
        y_current = mm(12)

        pavimento = self.var_pavimento.get() if hasattr(self, 'var_pavimento') else "LAJE 1"

        draw.text((area_util_x1, y_current), "Sigla/Obra", font=font_bold, fill="#000000")
        draw.text((area_util_x1 + mm(28), y_current), obra_nome.replace(" ", " - "), font=font_bold, fill="#000000")
        y_current += step_y

        draw.text((area_util_x1, y_current), "Desenho", font=font_bold, fill="#000000")
        tipo_exib = self._obter_tipo_formato(largura_m)
        draw.text((area_util_x1 + mm(28), y_current), tipo_exib, font=font_bold, fill="#e11d48")
        y_current += step_y

        draw.text((area_util_x1, y_current), "Pavimento", font=font_bold, fill="#000000")
        draw.text((area_util_x1 + mm(28), y_current), pavimento, font=font_bold, fill="#000000")
        y_current += step_y

        draw.text((area_util_x1, y_current), "Elemento", font=font_bold, fill="#000000")
        pos_block_w = mm(26)
        elem_x = area_util_x1 + mm(28)
        elem_max_w = max(0, (area_util_x2 - pos_block_w - mm(4)) - elem_x)
        elemento_txt = _truncate_pil(f"{elemento}", font_bold, elem_max_w)
        draw.text((elem_x, y_current), elemento_txt, font=font_bold, fill="#000000")
        _draw_right(area_util_x2 - mm(10), y_current, "POS", font=font_bold, fill="#000000")
        _draw_right(area_util_x2 - mm(2), y_current, f"{pos_tipo}", font=font_pos, fill="#000000")
        

        # Tabela técnica
        th = mm(8)
        tr = mm(10)
        tab_y1 = mm(45)
        tab_y2 = tab_y1 + th + tr
        tab_x = area_util_x1
        cw1 = mm(16)
        cw2 = mm(34)
        cw3 = mm(22)
        cw4 = mm(18)
        tot = cw1 + cw2 + cw3 + cw4
        if tot > area_util_w and area_util_w > 0:
            escala = area_util_w / tot
            cw1 = int(cw1 * escala); cw2 = int(cw2 * escala); cw3 = int(cw3 * escala); cw4 = int(cw4 * escala)

        draw.rectangle([(tab_x, tab_y1), (tab_x + cw1 + cw2 + cw3 + cw4, tab_y2)], outline="#000000", width=2)
        draw.line([(tab_x + cw1, tab_y1), (tab_x + cw1, tab_y2)], fill="#000000", width=2)
        draw.line([(tab_x + cw1 + cw2, tab_y1), (tab_x + cw1 + cw2, tab_y2)], fill="#000000", width=2)
        draw.line([(tab_x + cw1 + cw2 + cw3, tab_y1), (tab_x + cw1 + cw2 + cw3, tab_y2)], fill="#000000", width=2)
        draw.line([(tab_x, tab_y1 + th), (tab_x + cw1 + cw2 + cw3 + cw4, tab_y1 + th)], fill="#000000", width=2)

        draw.text((tab_x + cw1 // 2, tab_y1 + th // 2), "Bitola", font=font_bold, fill="#000000", anchor="mm")
        draw.text((tab_x + cw1 + cw2 // 2, tab_y1 + th // 2), "Compr. Unit.", font=font_bold, fill="#000000", anchor="mm")
        draw.text((tab_x + cw1 + cw2 + cw3 // 2, tab_y1 + th // 2), "Peso", font=font_bold, fill="#000000", anchor="mm")
        draw.text((tab_x + cw1 + cw2 + cw3 + cw4 // 2, tab_y1 + th // 2), "Qtde", font=font_bold, fill="#000000", anchor="mm")

        chave = (elemento, pos_tipo)
        if hasattr(self, 'medidas_customizadas') and chave in self.medidas_customizadas:
            bitola = self.medidas_customizadas[chave].get('bitola', bitola)
            comp_m = self.medidas_customizadas[chave].get('comp', comp_m)
            qtde = self.medidas_customizadas[chave].get('qtde', qtde)

        peso_val = 0.0
        try:
            from core.peso import peso_linear_kg_m
            peso_val = peso_linear_kg_m(float(bitola)) * float(comp_m) * float(qtde)
        except Exception:
            pass

        draw.text((tab_x + cw1 // 2, tab_y1 + th + tr // 2), f"{bitola:.2f}", font=font_small, fill="#000000", anchor="mm")
        draw.text((tab_x + cw1 + cw2 // 2, tab_y1 + th + tr // 2), f"{comp_m:.3f}", font=font_small, fill="#000000", anchor="mm")
        draw.text((tab_x + cw1 + cw2 + cw3 // 2, tab_y1 + th + tr // 2), f"{peso_val:.2f}", font=font_small, fill="#000000", anchor="mm")
        draw.text((tab_x + cw1 + cw2 + cw3 + cw4 // 2, tab_y1 + th + tr // 2), f"{qtde}", font=font_small, fill="#000000", anchor="mm")

        # Desenho técnico (reta x dobra dupla)
        draw_area_x1 = area_util_x1 + mm(3)
        draw_area_x2 = area_util_x2 - mm(3)
        draw_area_y1 = tab_y2 + mm(3)
        draw_area_y2 = altura_topo - mm(3)
        if draw_area_x2 > draw_area_x1 and draw_area_y2 > draw_area_y1:
            draw.rectangle([(draw_area_x1, draw_area_y1), (draw_area_x2, draw_area_y2)], outline="#e11d48", width=3)

            chave = (elemento, pos_tipo)
            forma = None
            if hasattr(self, 'formas_customizadas') and chave in self.formas_customizadas:
                forma = self.formas_customizadas.get(chave)
            if not forma:
                forma = self._obter_forma_laje(elemento)

            medidas = self.medidas_customizadas.get(chave, {}) if hasattr(self, 'medidas_customizadas') else {}

            cx = (draw_area_x1 + draw_area_x2) // 2
            cy = (draw_area_y1 + draw_area_y2) // 2

            corpo_cm = float(medidas.get('medida_corpo', comp_m * 100.0 if comp_m else 0))

            if forma == "dobra_dupla":
                left = draw_area_x1 + (draw_area_x2 - draw_area_x1) * 0.2
                right = draw_area_x1 + (draw_area_x2 - draw_area_x1) * 0.8
                bottom = draw_area_y1 + (draw_area_y2 - draw_area_y1) * 0.8
                leg_max_h = (draw_area_y2 - draw_area_y1) * 0.55

                dobra_esq = float(medidas.get('medida_dobra', 25))
                dobra_dir = float(medidas.get('medida_dobra_2', 25))
                max_dobra = max(dobra_esq, dobra_dir, 1.0)
                leg_esq_h = leg_max_h * (dobra_esq / max_dobra)
                leg_dir_h = leg_max_h * (dobra_dir / max_dobra)

                top_esq = bottom - leg_esq_h
                top_dir = bottom - leg_dir_h

                draw.line([(left, bottom), (right, bottom)], fill="#000000", width=6)
                draw.line([(left, bottom), (left, top_esq)], fill="#000000", width=6)
                draw.line([(right, bottom), (right, top_dir)], fill="#000000", width=6)

                draw.text((left - mm(3), (top_esq + bottom) / 2), f"{dobra_esq:.0f}cm", font=font_tiny, fill="#000000", anchor="rm")
                draw.text((right + mm(3), (top_dir + bottom) / 2), f"{dobra_dir:.0f}cm", font=font_tiny, fill="#000000", anchor="lm")
                if corpo_cm > 0:
                    draw.text((cx, bottom + mm(3)), f"{corpo_cm:.0f}cm", font=font_tiny, fill="#000000", anchor="mm")
            else:
                draw.line([(draw_area_x1 + (draw_area_x2 - draw_area_x1) * 0.15, cy),
                           (draw_area_x1 + (draw_area_x2 - draw_area_x1) * 0.85, cy)], fill="#000000", width=6)
                if corpo_cm > 0:
                    draw.text((cx, cy - mm(3)), f"{corpo_cm:.0f}cm", font=font_tiny, fill="#000000", anchor="mm")

        # Picotes
        total_picotes_h = (3 * altura_picote) + (2 * espaco_picote)
        y_picote_base = altura_topo + max(0, (altura - altura_topo - total_picotes_h) // 2) + (espaco_picote // 2) + mm(4)
        obra_nome = self.var_obra.get() if hasattr(self, 'var_obra') else "OBRA 001"
        picote_x1 = mm(2)
        picote_x2 = largura
        
        # Determinar tipo NORMAL ou VARIÁVEL
        tipo_exib = self._obter_tipo_formato(formato_dobra)
        
        for i in range(3):
            y_picote = y_picote_base + i * (altura_picote + espaco_picote)
            draw.rectangle([(picote_x1, y_picote), (picote_x2, y_picote + altura_picote)], outline="#000000", width=3)  # Bordas mais escuras
            draw.rectangle([(picote_x1, y_picote), (picote_x2, y_picote + altura_picote)], fill="#f0f0f0")  # Fundo cinza claro
            texto = f"{obra_nome} | {elemento} | {pos_tipo} | ø{bitola:.1f} | {qtde}x{comp_m:.2f}m | {tipo_exib}"
            draw.text(((picote_x1 + picote_x2) // 2, y_picote + altura_picote // 2), texto, font=font_picote, fill="#000000", anchor="mm")
            if i < 2:
                y_linha = y_picote + altura_picote + espaco_picote // 2
                for x in range(0, largura, 12):
                    draw.line([(x, y_linha), (x + 6, y_linha)], fill="#000000", width=2)

        nome_arquivo = re.sub(r'[\\/:*?"<>|]', '-', f"{elemento}_{pos_tipo}_Ø{bitola}_Q{qtde}.png")
        caminho_final = os.path.join(pasta_destino, nome_arquivo)
        img.save(caminho_final, dpi=(300, 300))
        return caminho_final

    def gerar_etiquetas(self):
        self.dados_etiquetas_filtrados, total_kg, total_pecas = self.aplicar_filtro_producao()

        if not self.dados_etiquetas_filtrados:
            messagebox.showwarning("Atenção", "Nenhum Elemento de Laje selecionado ou processado!")
            return

        if self.janela_etiq and self.janela_etiq.winfo_exists(): self.janela_etiq.destroy()

        # Preparar gerador de etiquetas no padrão de vigas/pilares
        if ETIQUETAS_GERADOR_DISPONIVEL:
            try:
                arquivos_dxf = []
                if hasattr(self, 'arquivos_processados') and self.arquivos_processados:
                    arquivos_dxf = list(self.arquivos_processados)
                elif hasattr(self, 'arquivos_selecionados') and self.arquivos_selecionados:
                    arquivos_dxf = list(self.arquivos_selecionados)

                dados_etq = []
                for dado in self.dados_etiquetas_filtrados:
                    elemento, pos, bitola, qtd_area, comp_m, _, peso_kg, _, _ = dado
                    dados_etq.append((elemento, pos, bitola, int(round(qtd_area)), comp_m, float(peso_kg)))

                self.gerador_etiquetas_dinamico = GeradorEtiquetasDinamico(
                    arquivos_dxf=arquivos_dxf,
                    pasta_etiquetas=r"c:\EngenhariaPlanPro\etiquetas",
                    obra=self.var_obra.get(),
                    pavimento=self.var_pavimento.get(),
                    dados_override=dados_etq
                )
                # Gerar PNGs para preview no padrão vigas/pilares
                self.caminhos_etiquetas_geradas = self.gerador_etiquetas_dinamico.gerar_e_salvar_etiquetas_png(
                    dpi_x=300, dpi_y=300
                )
            except Exception as e:
                print(f"[WARN] Falha ao preparar etiquetas padrão: {e}")

        self.janela_etiq = tk.Toplevel(self)
        self.janela_etiq.title("Etiquetas de Corte e Dobra - LAJES")
        self.janela_etiq.geometry("950x750")
        self.janela_etiq.configure(bg="#f5f5f5")
        
        control_frame = tk.Frame(self.janela_etiq, bg="#e0e0e0")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(control_frame, text="Total de Barras Filtradas:", bg="#e0e0e0").pack(side="left", padx=10)
        tk.Label(control_frame, text=f"{total_pecas}", bg="#e0e0e0", font=("Arial", 10, "bold")).pack(side="left")
        
        self.contagem_label = tk.Label(control_frame, text="", bg="#e0e0e0", font=("Arial", 10, "bold"), fg="#1976d2")
        self.contagem_label.pack(side="right", padx=10)
        
        tk.Button(control_frame, text="◀ Página Anterior", command=self.navegar_anterior, padx=10).pack(side="right", padx=5)
        tk.Button(control_frame, text="Próxima Página ▶", command=self.navegar_proximo, padx=10).pack(side="right", padx=5)
        
        tk.Button(
            control_frame, text="🖨️ Imprimir Etiquetas",
            command=self._gerar_etiquetas_png_padrao,
            bg="#9c27b0", fg="white", font=("Arial", 10, "bold"), padx=10, pady=2
        ).pack(side="right", padx=20)

        self.frame_grid = tk.Frame(self.janela_etiq, bg="#cccccc")
        self.frame_grid.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.indice_etiqueta_pagina = 0
        self.desenhar_pagina_etiquetas_lajes(self.indice_etiqueta_pagina)
        self.janela_etiq.transient(self)

    # --- EDITOR DE ETIQUETAS (PADRÃO VIGAS/PILARES) ---
    def imprimir_etiquetas(self):
        """Abre editor visual de etiquetas no padrão vigas/pilares - RENDERIZAÇÃO DIRETA NO CANVAS."""
        self.dados_etiquetas_filtrados, total_kg, total_pecas = self.aplicar_filtro_producao()
        
        if not self.dados_etiquetas_filtrados:
            messagebox.showwarning("Atenção", "Nenhum Elemento de Laje selecionado ou processado!")
            return
        
        # Inicializar variáveis
        if not hasattr(self, 'pagina_atual'):
            self.pagina_atual = 0
        if not hasattr(self, 'etiquetas_por_pagina'):
            self.etiquetas_por_pagina = 6
        if not hasattr(self, 'etiquetas_selecionadas'):
            self.etiquetas_selecionadas = {i: True for i in range(len(self.dados_etiquetas_filtrados))}
        if not hasattr(self, 'medidas_customizadas'):
            self.medidas_customizadas = {}
        if not hasattr(self, 'formas_customizadas'):
            self.formas_customizadas = {}
        
        self.total_paginas = max(1, math.ceil(len(self.dados_etiquetas_filtrados) / self.etiquetas_por_pagina))
        
        # Janela do editor
        if hasattr(self, 'janela_editor') and self.janela_editor and self.janela_editor.winfo_exists():
            self.janela_editor.destroy()
        
        self.janela_editor = tk.Toplevel(self)
        self.janela_editor.title("✏️ EDITOR DE ETIQUETAS - LAJES")
        self.janela_editor.configure(bg="#0d2818")
        
        self.janela_editor.update_idletasks()
        screen_w = self.janela_editor.winfo_screenwidth()
        screen_h = self.janela_editor.winfo_screenheight()
        win_w = min(1200, screen_w - 40)
        win_h = min(900, screen_h - 80)
        x = max(0, (screen_w // 2) - (win_w // 2))
        y = max(0, (screen_h // 2) - (win_h // 2))
        self.janela_editor.geometry(f"{win_w}x{win_h}+{x}+{y}")
        
        if not hasattr(self, 'zoom_factor'):
            if screen_h < 900 or screen_w < 1200:
                self.zoom_factor = 0.85
            else:
                self.zoom_factor = 1.0
        
        # Título
        titulo_frame = tk.Frame(self.janela_editor, bg="#ff6f00")
        titulo_frame.pack(fill="x")
        tk.Label(titulo_frame, text="✏️ EDITOR DE ETIQUETAS - EDITE, SELECIONE E IMPRIMA",
                 bg="#ff6f00", fg="white", font=("Arial", 12, "bold"), pady=8).pack()
        
        # Canvas com scroll
        canvas_frame = tk.Frame(self.janela_editor, bg="#0d2818")
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(canvas_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas_etiq = tk.Canvas(canvas_frame, bg="white", yscrollcommand=scrollbar.set, highlightthickness=0)
        self.canvas_etiq.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.canvas_etiq.yview)
        
        def _on_mousewheel(event):
            try:
                self.canvas_etiq.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass
        self.canvas_etiq.bind("<MouseWheel>", _on_mousewheel)
        self.canvas_etiq.bind("<Button-1>", self._handle_canvas_click)
        
        # Renderizar etiquetas
        try:
            self.desenhar_etiquetas_com_selecao()
        except Exception as e:
            self.canvas_etiq.create_text(600, 450, text=f"⚠️ Erro ao renderizar preview\n{str(e)}", 
                                          font=("Arial", 12), fill="red")
            print(f"[ERRO] Erro ao renderizar: {e}")
        
        # Navegação
        nav_frame = tk.Frame(self.janela_editor, bg="#34495e")
        nav_frame.pack(fill="x", padx=10, pady=5)
        
        self.label_pagina = tk.Label(nav_frame, text=f"Página {self.pagina_atual + 1} de {self.total_paginas}",
                                      bg="#34495e", fg="white", font=("Arial", 10, "bold"))
        self.label_pagina.pack(side="left", padx=10, pady=5)
        
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

        # Seleção
        sel_frame = tk.Frame(self.janela_editor, bg="#1a3d2e")
        sel_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(sel_frame, text="🔘 Seleção:", bg="#1a3d2e", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(sel_frame, text="☑️ MARCAR TODAS", command=self._marcar_todas_etiquetas,
              bg="#27ae60", fg="white", font=("Arial", 9, "bold"), padx=10, pady=4, cursor="hand2").pack(side="left", padx=3)
        tk.Button(sel_frame, text="☐ DESMARCAR TODAS", command=self._desmarcar_todas_etiquetas,
              bg="#e74c3c", fg="white", font=("Arial", 9, "bold"), padx=10, pady=4, cursor="hand2").pack(side="left", padx=3)

        total_selecionadas = sum(1 for v in self.etiquetas_selecionadas.values() if v)
        self.label_selecionadas = tk.Label(sel_frame, text=f"Selecionadas: {total_selecionadas}/{len(self.dados_etiquetas_filtrados)}",
                            bg="#1a3d2e", fg="#ff9800", font=("Arial", 9, "bold"))
        self.label_selecionadas.pack(side="right", padx=10, pady=4)

        btn_frame = tk.Frame(self.janela_editor, bg="#1a3d2e")
        btn_frame.pack(fill="x", padx=10, pady=10)
        info_text = f"📋 Total: {len(self.dados_etiquetas_filtrados)} etiquetas | 💡 Clique nos valores para editar | ☑️ Selecione quais imprimir"
        tk.Label(btn_frame, text=info_text, bg="#1a3d2e", fg="white", font=("Arial", 9)).pack(side="left", padx=10, pady=5)
        btn_actions = tk.Frame(btn_frame, bg="#1a3d2e")
        btn_actions.pack(side="right", padx=5)
        tk.Button(btn_actions, text="✅ IMPRIMIR SELECIONADAS", command=self._imprimir_etiquetas_selecionadas,
                  bg="#27ae60", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5, cursor="hand2").pack(side="left", padx=3)
        tk.Button(btn_actions, text="✕ FECHAR", command=self.janela_editor.destroy,
                  bg="#e74c3c", fg="white", font=("Arial", 9), padx=10, pady=5, cursor="hand2").pack(side="left", padx=3)

    def desenhar_etiquetas_com_selecao(self):
        """Renderiza etiquetas 100×150mm COM PICOTES + CHECKBOXES para seleção (padrão vigas_app)."""
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

        # Escala e dimensões
        PX_MM = 4
        zf = getattr(self, 'zoom_factor', 1.0)
        MARGEM = (10 * PX_MM) * zf
        LARGURA_ETIQ = (100 * PX_MM) * zf
        ALTURA_TOPO = (93 * PX_MM) * zf
        ALTURA_MICRO = (18 * PX_MM) * zf
        ESPACO_PICOTE = (1 * PX_MM) * zf

        total_picotes_h = (3 * ALTURA_MICRO) + (2 * ESPACO_PICOTE)
        ALTURA_ETIQ = (150 * PX_MM) * zf
        altura_etiqueta = ALTURA_ETIQ

        canvas_w = int(self.canvas_etiq.winfo_width())
        x_base = max(MARGEM, (canvas_w - LARGURA_ETIQ) // 2)

        inicio = self.pagina_atual * self.etiquetas_por_pagina
        fim = min(len(self.dados_etiquetas_filtrados), inicio + self.etiquetas_por_pagina)

        y_cursor = MARGEM

        self._checkbox_positions = {}
        for i in range(inicio, fim):
            if i < 0 or i >= len(self.dados_etiquetas_filtrados):
                continue
            dado = self.dados_etiquetas_filtrados[i]
            if not dado or len(dado) < 6:
                continue
            try:
                elemento, pos_tipo, bitola, qtde, comp_m, largura_m = dado[0], dado[1], float(dado[2]), int(dado[3]), float(dado[4]), dado[5]
            except (ValueError, TypeError, IndexError) as e:
                print(f"[WARN] Erro ao extrair dados: {e}")
                continue
            
            chave = (elemento, pos_tipo)
            
            # Moldura e conteúdo
            self._desenhar_moldura_etiqueta(x_base, y_cursor, LARGURA_ETIQ, ALTURA_TOPO)
            self._desenhar_topo_etiqueta(x_base, y_cursor, LARGURA_ETIQ, ALTURA_TOPO, elemento, pos_tipo, bitola, qtde, comp_m, largura_m)
            
            # 3 seções inferiores
            extra_gap = max(0, (ALTURA_ETIQ - ALTURA_TOPO - total_picotes_h) / 2)
            base_y = y_cursor + ALTURA_TOPO + (ESPACO_PICOTE / 2) + extra_gap + (2 * PX_MM * zf)
            picote_margin = 8 * zf
            for idx in range(3):
                y_sec = base_y + idx * (ALTURA_MICRO + ESPACO_PICOTE)
                self.canvas_etiq.create_rectangle(x_base + picote_margin, y_sec, x_base + LARGURA_ETIQ, y_sec + ALTURA_MICRO, outline="#cccccc", width=1)
                self._desenhar_secao_micro(x_base + picote_margin + 6 * zf, y_sec + 6 * zf, LARGURA_ETIQ - picote_margin - 12 * zf, ALTURA_MICRO - 12 * zf, elemento, pos_tipo, bitola, qtde, comp_m, largura_m)
                if idx < 2:
                    self._desenhar_picote(x_base, y_sec + ALTURA_MICRO + (ESPACO_PICOTE / 2), LARGURA_ETIQ)
            
            # Identificação
            info_y = y_cursor + 8
            self.canvas_etiq.create_text(x_base + 8, info_y, text=f"E {i+1}", font=("Arial", int(9*zf), "bold"), fill="#333333", anchor="nw")
            
            # TAG para clique
            tag_ret = self.canvas_etiq.create_rectangle(x_base-1, y_cursor-1, x_base + LARGURA_ETIQ+1, 
                                             y_cursor + altura_etiqueta+1, fill="", outline="", tags=f"etiq_{i}")
            self.canvas_etiq.tag_raise(f"etiq_{i}")
            
            # CHECKBOX DE SELEÇÃO
            checkbox_size = 28 * zf
            x_checkbox = x_base + 8 * zf
            y_checkbox = y_cursor + 8 * zf
            self._checkbox_positions[i] = {
                'x1': x_checkbox - 5 * zf, 'y1': y_checkbox - 5 * zf,
                'x2': x_checkbox + checkbox_size + 5 * zf, 'y2': y_checkbox + checkbox_size + 5 * zf,
                'elemento': elemento, 'pos': pos_tipo, 'bitola': bitola, 'qtde': qtde, 'comp': comp_m
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
            
            self.canvas_etiq.create_rectangle(x_checkbox - 5 * zf, y_checkbox - 5 * zf, 
                                             x_checkbox + checkbox_size + 5 * zf, y_checkbox + checkbox_size + 5 * zf,
                                             fill="", outline="", tags=f"checkbox_{i}")
            
            if self.etiquetas_selecionadas.get(i, True):
                self.canvas_etiq.create_text(x_checkbox+checkbox_size+8*zf, y_checkbox+checkbox_size//2, 
                                            text="Selecionado", font=("Arial", int(8*zf), "bold"), fill="#27ae60", anchor="w")
            else:
                self.canvas_etiq.create_text(x_checkbox+checkbox_size+8*zf, y_checkbox+checkbox_size//2, 
                                            text="Clique para selecionar", font=("Arial", int(7*zf)), fill="#999999", anchor="w")
            y_cursor += altura_etiqueta + (ESPACO_PICOTE * 3)

        self.total_paginas = max(1, math.ceil(len(self.dados_etiquetas_filtrados) / self.etiquetas_por_pagina))
        self.canvas_etiq.configure(scrollregion=(0, 0, canvas_w, max(1188, y_cursor + MARGEM + (ALTURA_MICRO * 2))))

        if yview_prev:
            try:
                self.canvas_etiq.yview_moveto(yview_prev[0])
            except Exception:
                pass

        if hasattr(self, 'label_pagina'):
            self.label_pagina.config(text=f"Página {self.pagina_atual + 1} de {self.total_paginas}")

    def _toggle_etiqueta_selecao(self, idx):
        """Toggle do estado da etiqueta clicada."""
        current_state = self.etiquetas_selecionadas.get(idx, True)
        self.etiquetas_selecionadas[idx] = not current_state
        self.desenhar_etiquetas_com_selecao()
        total_selecionadas = sum(1 for v in self.etiquetas_selecionadas.values() if v)
        self.label_selecionadas.config(text=f"Selecionadas: {total_selecionadas}/{len(self.dados_etiquetas_filtrados)}")

    def _handle_canvas_click(self, event):
        """Handler de clique no canvas - verifica se clicou em checkbox ou etiqueta."""
        x = self.canvas_etiq.canvasx(event.x)
        y = self.canvas_etiq.canvasy(event.y)
        
        # Verificar checkbox primeiro
        if hasattr(self, '_checkbox_positions') and self._checkbox_positions:
            for idx, pos_info in self._checkbox_positions.items():
                x1, y1, x2, y2 = pos_info['x1'], pos_info['y1'], pos_info['x2'], pos_info['y2']
                if x1 <= x <= x2 and y1 <= y <= y2:
                    self._toggle_etiqueta_selecao(idx)
                    return "break"
        
        # Verificar clique na etiqueta para editar
        items_at_point = self.canvas_etiq.find_overlapping(x-5, y-5, x+5, y+5)
        for item in items_at_point:
            tags = self.canvas_etiq.gettags(item)
            for tag in tags:
                if tag.startswith('etiq_'):
                    idx_str = tag.replace('etiq_', '')
                    try:
                        idx = int(idx_str)
                        if idx < len(self.dados_etiquetas_filtrados):
                            dado = self.dados_etiquetas_filtrados[idx]
                            self._editar_etiqueta_dados(idx, dado[0], dado[1], float(dado[2]), int(dado[3]), float(dado[4]))
                            return "break"
                    except:
                        pass

    def _marcar_todas_etiquetas(self):
        self.etiquetas_selecionadas = {i: True for i in range(len(self.dados_etiquetas_filtrados))}
        self.desenhar_etiquetas_com_selecao()

    def _desmarcar_todas_etiquetas(self):
        self.etiquetas_selecionadas = {i: False for i in range(len(self.dados_etiquetas_filtrados))}
        self.desenhar_etiquetas_com_selecao()

    def _ir_primeira_pagina_etiquetas(self):
        self.pagina_atual = 0
        self.desenhar_etiquetas_com_selecao()

    def _ir_pagina_anterior_etiquetas(self):
        if self.pagina_atual > 0:
            self.pagina_atual -= 1
        self.desenhar_etiquetas_com_selecao()

    def _ir_proxima_pagina_etiquetas(self):
        if self.pagina_atual < self.total_paginas - 1:
            self.pagina_atual += 1
        self.desenhar_etiquetas_com_selecao()

    def _ir_ultima_pagina_etiquetas(self):
        self.pagina_atual = self.total_paginas - 1
        self.desenhar_etiquetas_com_selecao()

    def _imprimir_etiquetas_selecionadas(self):
        """Gera PNGs das etiquetas selecionadas e abre HTML para impressão (padrão vigas_app)."""
        selecionadas = [i for i, sel in self.etiquetas_selecionadas.items() if sel]
        if not selecionadas:
            messagebox.showwarning("Atenção", "Nenhuma etiqueta selecionada!")
            return

        try:
            def _to_float(val, default=0.0):
                try:
                    if isinstance(val, str):
                        v = val.replace("ø", "").replace("Ø", "")
                        v = v.replace("mm", "").replace(" ", "")
                        v = v.replace(",", ".")
                        return float(v)
                    return float(val)
                except Exception:
                    return float(default)

            if not ETIQUETAS_GERADOR_DISPONIVEL:
                messagebox.showwarning("Atenção", "Gerador de etiquetas não disponível.")
                return

            arquivos_dxf = []
            if hasattr(self, 'arquivos_processados') and self.arquivos_processados:
                arquivos_dxf = list(self.arquivos_processados)
            elif hasattr(self, 'arquivos_selecionados') and self.arquivos_selecionados:
                arquivos_dxf = list(self.arquivos_selecionados)

            dados_sel = []
            for idx in selecionadas:
                dado = self.dados_etiquetas_filtrados[idx]
                elemento, pos, bitola, qtd_area, comp_m, _, peso_kg, _, _ = dado
                bitola_f = _to_float(bitola)
                comp_m_f = _to_float(comp_m)
                qtde_i = int(round(_to_float(qtd_area)))
                peso_f = _to_float(peso_kg)
                dados_sel.append((elemento, pos, bitola_f, qtde_i, comp_m_f, peso_f))

            # Gerar PNGs no layout do editor
            import tempfile
            pasta_temp = os.path.join(tempfile.gettempdir(), "etiquetas_lajes_editor")
            os.makedirs(pasta_temp, exist_ok=True)

            caminhos = []
            for idx, dado in zip(selecionadas, dados_sel):
                elemento, pos, bitola, qtde, comp_m, largura_m = dado[0], dado[1], dado[2], dado[3], dado[4], dado[5] if len(dado) > 5 else ""
                caminhos.append(self._gerar_png_etiqueta_editor(idx, elemento, pos, bitola, qtde, comp_m, pasta_temp, largura_m))

            # Gerar HTML com imagens base64 (igual padrão vigas)
            import base64
            import tempfile
            import webbrowser

            imagens_base64 = []
            for caminho in caminhos:
                try:
                    with open(caminho, 'rb') as f:
                        imagens_base64.append(base64.b64encode(f.read()).decode('utf-8'))
                except Exception as e:
                    print(f"[WARN] Erro ao ler {caminho}: {e}")

            if not imagens_base64:
                messagebox.showerror("Erro", "Não foi possível processar as imagens para impressão.")
                return

            html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Impressão de Etiquetas - Lajes</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; font-weight: bold; }}
        .toolbar {{ position: sticky; top: 0; background: #ffffff; padding: 10px; border-bottom: 1px solid #ddd; display: flex; gap: 10px; z-index: 10; }}
        .btn {{ background: #27ae60; color: white; border: none; padding: 8px 14px; border-radius: 4px; font-weight: bold; cursor: pointer; }}
        .page {{ display: grid; gap: 20px; }}
        .etiqueta {{ background: white; padding: 10px; border: 2px solid #333; width: 100mm; height: 150mm; }}
        img {{ width: 100mm; height: 150mm; object-fit: contain; display: block; margin: 0 auto; image-rendering: auto; }}
        @media print {{
            @page {{ size: 100mm 150mm; margin: 0; }}
            html, body {{ width: 100%; height: 100%; }}
            body {{ background: white; padding: 0; margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .toolbar {{ display: none; }}
            .page {{ gap: 0; }}
            .etiqueta {{ border: none; padding: 0; width: 100mm; height: 150mm; page-break-inside: avoid; page-break-after: always; }}
            img {{ width: 100mm; height: 150mm; }}
        }}
    </style>
</head>
<body>
    <div class="toolbar">
        <button class="btn" onclick="window.print()">Imprimir</button>
    </div>
    <div class="page">
        {''.join([f'<div class="etiqueta"><img src="data:image/png;base64,{img}" /></div>' for img in imagens_base64])}
    </div>
</body>
</html>
"""

            html_temp = tempfile.mktemp(suffix="_etiquetas_lajes.html")
            with open(html_temp, 'w', encoding='utf-8') as f:
                f.write(html_content)
            try:
                webbrowser.open('file://' + html_temp)
            except Exception:
                try:
                    os.startfile(html_temp)
                except Exception:
                    pass
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Falha ao imprimir etiquetas:\n{e}")

    def _gerar_etiquetas_png_padrao(self):
        if not ETIQUETAS_GERADOR_DISPONIVEL or not hasattr(self, 'gerador_etiquetas_dinamico'):
            messagebox.showwarning("Atenção", "Gerador de etiquetas padrão não disponível.")
            return

        try:
            caminhos = self.gerador_etiquetas_dinamico.gerar_e_salvar_etiquetas_png(dpi_x=300, dpi_y=300)
            messagebox.showinfo(
                "Etiquetas geradas",
                f"{len(caminhos)} etiquetas PNG geradas em:\n{self.gerador_etiquetas_dinamico.pasta_etiquetas}"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar etiquetas padrão:\n{e}")


    # --- FUNÇÕES AUXILIARES (Salvar/Limpar/Exportar) ---
    
    def exportar_excel(self):
        dados_filtrados, total_kg, total_pecas = self.aplicar_filtro_producao()
        if not dados_filtrados:
            messagebox.showwarning("Atenção", "Nenhum Elemento de Laje selecionado ou processado!")
            return
        messagebox.showinfo("Aviso", f"Exportação para Excel iniciada com dados de {len(dados_filtrados)} itens. (Total kg: {total_kg:.2f})")
        
    def limpar(self):
        if not messagebox.askyesno("Confirmação", "Você tem certeza que deseja LIMPAR TODOS OS DADOS (Planilhamento, Filtros e Checklist)? Esta ação é irreversível!"): return

        self.arquivos_selecionados = []
        self.dados_processados, self.total_kg, self.total_pecas = [], 0.0, 0 # Limpa TUDO
        self.lajes_ativas = set() 
        self.checkboxes_conf.clear()
        self.estado_salvo_checklist.clear() 
        self.var_obra.set("OBRA 001")
        self.var_pavimento.set("LAJE 1")
        
        try:
            if os.path.exists(ESTADO_FILEPATH): os.remove(ESTADO_FILEPATH)
            if os.path.exists(PLANILHAMENTO_FILEPATH): os.remove(PLANILHAMENTO_FILEPATH)
        except: pass
            
        self.recarregar_treeview()
        self.status_label.config(text="✅ Pronto. Tabela limpa.")
        self.info_label.config(text="")
        messagebox.showinfo("Limpeza", "TODOS os dados de processamento, filtros e estado foram limpos.")

    def salvar_txt(self, conteudo):
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt")],
            initialfile=f"romaneio_lajes_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        )
        if arquivo:
            with open(arquivo, "w", encoding="utf-8") as f:
                f.write(conteudo)
            messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")

# Executar aplicação
if __name__ == "__main__":
    app = LajesApp()
    app.mainloop()