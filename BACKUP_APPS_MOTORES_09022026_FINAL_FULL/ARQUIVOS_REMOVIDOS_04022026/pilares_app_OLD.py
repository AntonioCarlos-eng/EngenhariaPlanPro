# pilares_app.py - SISTEMA COMPLETO DE PILARES COM FILTRO DE PRODUÇÃO E PERSISTÊNCIA
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import os
import sys
import math
import json
import csv
from typing import Dict, Any, List, Tuple

# Constantes para os nomes dos arquivos de persistência
ESTADO_FILEPATH = "pilares_checklist_state.json"
PLANILHAMENTO_FILEPATH = "pilares_planilhamento_editado.json"

# Adicionar o diretório ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importação do motor de pilares
try:
    from core.pilares_motor import processar_pilares, analisar_pilar_geometricamente, _calcular_peso
except ImportError:
    messagebox.showerror("Erro de Importação", "Não foi possível carregar o arquivo 'core/pilares_motor.py'.")
    sys.exit(1) # Sai se o motor não puder ser importado

class PilaresApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("EngenhariaPlanPro - PILARES")
        self.geometry("1200x700")
        self.configure(bg="#0d2818")
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 600
        y = (self.winfo_screenheight() // 2) - 350
        self.geometry(f"1200x700+{x}+{y}")
        
        self.arquivos_selecionados = []
        # Estrutura de dados processados:
        # (pilar, pos, bitola, qtde, comp_m, peso_kg, formato_dobra, medidas_m)
        self.dados_processados: List[Tuple[str, str, float, int, float, float, str, List[float]]] = [] 
        self.pilares_ativos = set()  
        self.total_kg = 0.0
        self.total_barras = 0
        self.checkboxes_conf: Dict[Tuple[str, str], Dict[str, tk.BooleanVar]] = {} 
        self.estado_salvo_checklist: Dict[str, Dict[str, bool]] = {} # Estado carregado do JSON
        
        # Variáveis de controle de etiqueta
        self.janela_etiq = None
        self.canvas_etiq = None
        self.indice_etiqueta_pagina = 0 
        self.pecas_por_pagina = 6 
        self.dados_etiquetas_filtrados = [] 

        # Variáveis de Cabeçalho
        self.var_obra = tk.StringVar(value="OBRA 001")
        self.var_pavimento = tk.StringVar(value="TÉRREO")

        self.carregar_planilhamento() # Tenta carregar dados editados
        self.carregar_estado_persistencia() # Tenta carregar filtros e checklist
        
        self._criar_interface()

    # --- PERSISTÊNCIA GERAL ---

    def salvar_estado_persistencia(self):
        """Salva o estado atual (pilares ativos, obra/pavimento e checklist) em JSON."""
        estado = {
            "obra": self.var_obra.get(),
            "pavimento": self.var_pavimento.get(),
            "pilares_ativos": list(self.pilares_ativos),
            "checklist_status": {}
        }
        
        # Coletar estado do checklist se a janela estiver aberta e populada
        if self.checkboxes_conf:
            for (pilar, pos), vars_dict in self.checkboxes_conf.items():
                chave = f"{pilar}-{pos}"
                estado["checklist_status"][chave] = {
                    status: var.get() for status, var in vars_dict.items()
                }

        try:
            with open(ESTADO_FILEPATH, 'w', encoding='utf-8') as f:
                json.dump(estado, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Erro de Persistência", f"Não foi possível salvar o estado: {e}")
            return False

    def carregar_estado_persistencia(self):
        """Carrega o estado do último uso (filtros e checklist)."""
        try:
            with open(ESTADO_FILEPATH, 'r', encoding='utf-8') as f:
                estado = json.load(f)
                
                # Carrega Cabeçalho
                self.var_obra.set(estado.get("obra", "OBRA 001"))
                self.var_pavimento.set(estado.get("pavimento", "TÉRREO"))

                # Carrega Pilares Ativos
                pilares = set(estado.get("pilares_ativos", []))
                if pilares:
                    self.pilares_ativos = pilares

                # Carrega Estado do Checklist (para inicializar variáveis depois)
                self.estado_salvo_checklist = estado.get("checklist_status", {})

        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Aviso: Não foi possível carregar o estado salvo: {e}")

    # --- SALVAMENTO E CARREGAMENTO DO PLANILHAMENTO EDITADO ---
    
    def salvar_planilhamento(self):
        """Salva a lista completa de dados (self.dados_processados) em JSON."""
        if not self.dados_processados:
            messagebox.showwarning("Atenção", "Nenhum dado para salvar.")
            return

        # Para salvar a tupla, precisamos convertê-la para lista, que é serializável em JSON
        dados_serializaveis = [list(dado) for dado in self.dados_processados]

        try:
            with open(PLANILHAMENTO_FILEPATH, 'w', encoding='utf-8') as f:
                json.dump(dados_serializaveis, f, indent=4)
            
            # Salva também o estado atual do filtro/cabeçalho
            self.salvar_estado_persistencia()
            
            messagebox.showinfo("Sucesso", "Planilhamento editado e estado salvos com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro de Salvamento", f"Não foi possível salvar o planilhamento: {e}")

    def carregar_planilhamento(self):
        """Carrega a lista completa de dados de um JSON previamente editado."""
        try:
            with open(PLANILHAMENTO_FILEPATH, 'r', encoding='utf-8') as f:
                dados_serializaveis = json.load(f)
                
                # Converte de volta para tupla e float/int
                dados_carregados = []
                for dado_list in dados_serializaveis:
                    # Garante que os tipos estão corretos (importante após a serialização/desserialização)
                    dado = (
                        dado_list[0], # pilar (str)
                        dado_list[1], # pos (str)
                        float(dado_list[2]), # bitola (float)
                        int(dado_list[3]),   # qtde (int)
                        float(dado_list[4]), # comp_m (float)
                        float(dado_list[5]), # peso_kg (float)
                        dado_list[6], # formato_dobra (str)
                        [float(m) for m in dado_list[7]] # medidas_m (List[float])
                    )
                    dados_carregados.append(dado)
                
                if dados_carregados:
                    self.dados_processados = dados_carregados
                    self.recarregar_treeview() # Atualiza a Treeview após o carregamento
                    messagebox.showinfo("Carregamento", f"Planilhamento editado carregado com {len(self.dados_processados)} peças.")
                
        except FileNotFoundError:
            pass # Ignora se o arquivo não existir
        except Exception as e:
            messagebox.showwarning("Aviso", f"Erro ao carregar planilhamento salvo. Iniciando vazio. {e}")


    # --- CÁLCULOS E AUXILIARES ---

    def _calcular_comp_corte_com_forma(self, forma: str, medidas_m: List[float], bitola_mm: float) -> float:
        """
        Recalcula o comprimento de corte a partir da soma dos segmentos em metros.
        Adiciona o fator de correção de dobramento (redução).
        """
        comp_segmentos = 0
        num_dobras = 0
        
        if forma.startswith("RETA") or forma.startswith("REFORÇO"):
            num_dobras = 0
            comp_segmentos = medidas_m[0] if medidas_m else 0.0

        elif forma.startswith("DOBRA L") or forma.startswith("BARRA L"):
            num_dobras = 1
            comp_segmentos = sum(medidas_m[:2])

        elif forma.startswith("BARRA U"):
            num_dobras = 2
            comp_segmentos = sum(medidas_m[:3])

        elif forma.startswith("ESTRIBO"):
            num_dobras = 4 # 4 cantos
            if len(medidas_m) >= 2:
                 A = medidas_m[0]
                 B = medidas_m[1]
                 comp_segmentos = 2 * A + 2 * B # CORREÇÃO: 4 lados
            else:
                 comp_segmentos = sum(medidas_m) # Fallback

        elif forma.startswith("GRAMPO"):
            num_dobras = 4 # 2 cantos + 2 dobras internas
            comp_segmentos = sum(medidas_m)
        
        # Correção simplificada: subtrai um diâmetro (aproximadamente) por dobra.
        correcao = (bitola_mm / 1000.0) * 0.5 * num_dobras
        
        comp_final = comp_segmentos - correcao
        return max(0.01, comp_final) # Mínimo de 1cm

    def _atualizar_dados_globais(self, pilar_original: str, pos_original: str, novos_dados: Dict[str, Any]):
        """Atualiza a lista principal de dados (self.dados_processados) após a edição."""
        
        for i, dado in enumerate(self.dados_processados):
            pilar, pos, bitola, qtde, comp_m, peso_kg, formato_dobra, medidas_m = dado
            
            if pilar == pilar_original and pos == pos_original:
                
                # Extrair novos valores
                nova_qtde = novos_dados.get('qtde', qtde)
                novo_formato = novos_dados.get('formato_dobra', formato_dobra)
                novas_medidas = novos_dados.get('medidas_m', medidas_m)
                
                # Recalcular Comprimento e Peso
                novo_comp_m = self._calcular_comp_corte_com_forma(novo_formato, novas_medidas, bitola)
                novo_peso_kg = _calcular_peso(bitola, novo_comp_m, nova_qtde)
                
                # Recriar a tupla de dados atualizada
                novo_dado = (
                    pilar, 
                    pos, 
                    bitola, 
                    nova_qtde, 
                    round(novo_comp_m, 2), 
                    round(novo_peso_kg, 2), 
                    novo_formato, 
                    novas_medidas
                )
                self.dados_processados[i] = novo_dado
                break

        # Re-processar/Recarregar a Treeview e o Romaneio se necessário
        self.recarregar_treeview()
        # Se as etiquetas estiverem abertas, recalcular o filtro e redesenhar
        if self.janela_etiq and self.janela_etiq.winfo_exists():
            self.dados_etiquetas_filtrados, _, _ = self.aplicar_filtro_producao()
            if self.dados_etiquetas_filtrados:
                 # Chama a função de redesenho para a página atual
                 self.desenhar_pagina_etiquetas_pilares(self.indice_etiqueta_pagina)


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
            text="🏗️ PROCESSAMENTO DE PILARES",
            font=("Arial", 20, "bold"),
            bg="#0d2818",
            fg="#ff9800"
        ).pack()
        
        # Frame de controles
        control_frame = tk.Frame(main_container, bg="#1a3d2e")
        control_frame.pack(fill="x", pady=5)
        
        # Linha 1 - Dados do projeto
        row1 = tk.Frame(control_frame, bg="#1a3d2e")
        row1.pack(fill="x", padx=10, pady=10)
        
        tk.Label(row1, text="Obra:", bg="#1a3d2e", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        # Entry para Obra
        tk.Entry(row1, textvariable=self.var_obra, width=25, font=("Arial", 10)).pack(side="left", padx=5)
        
        tk.Label(row1, text="Pavimento:", bg="#1a3d2e", fg="white", font=("Arial", 10)).pack(side="left", padx=20)
        # Entry para Pavimento
        tk.Entry(row1, textvariable=self.var_pavimento, width=20, font=("Arial", 10)).pack(side="left", padx=5)

        # Botão SALVAR PLANILHAMENTO (Novo)
        tk.Button(
            row1,
            text="💾 Salvar Planilha",
            command=self.salvar_planilhamento,
            bg="#2e7d32",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side="right", padx=5)
        
        # Linha 2 - Botões principais
        row2 = tk.Frame(control_frame, bg="#1a3d2e")
        row2.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Button(
            row2,
            text="📁 Selecionar Arquivos",
            command=self.selecionar_arquivos,
            bg="#ff6f00",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            row2,
            text="⚙️ PROCESSAR V1",
            command=self.processar,
            bg="#ff8f00",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side="left", padx=5)

        tk.Button(
            row2,
            text="⚙️ PROCESSAR V2",
            command=self.processar_v2,
            bg="#ff6f00",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side="left", padx=5)

        tk.Button(
            row2,
            text="📐 Gerenciar Produção",
            command=self.gerenciar_producao,
            bg="#5e35b1",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            row2,
            text="📄 Gerar Romaneio",
            command=self.gerar_romaneio,
            bg="#1976d2",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            row2,
            text="📋 Check List",
            command=self.gerar_romaneio_conferencia,
            bg="#00acc1",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            row2,
            text="🏷️ Etiquetas",
            command=self.gerar_etiquetas,
            bg="#9c27b0",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            row2,
            text="📊 Exportar Excel",
            command=self.exportar_excel,
            bg="#4caf50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            row2,
            text="🔄 Limpar Tudo",
            command=self.limpar,
            bg="#757575",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        # Frame da tabela
        table_frame = tk.Frame(main_container, bg="#0d2818")
        table_frame.pack(fill="both", expand=True, pady=10)
        
        # Criar Treeview com scrollbars
        tree_scroll_y = ttk.Scrollbar(table_frame)
        tree_scroll_y.pack(side="right", fill="y")
        
        tree_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e")
        style.configure("Treeview.Heading", background="#ff6f00", foreground="white", font=("Arial", 10, "bold"))
        
        # Colunas expandidas para incluir FORMATO e MEDIDAS (invisíveis na Treeview principal)
        self.tree = ttk.Treeview(
            table_frame,
            columns=("pilar", "pos", "bitola", "qtde", "comp", "peso", "formato", "medidas"),
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        
        # Configurar colunas visíveis
        self.tree.heading("pilar", text="PILAR")
        self.tree.heading("pos", text="POSIÇÃO")
        self.tree.heading("bitola", text="BITOLA (mm)")
        self.tree.heading("qtde", text="QUANTIDADE")
        self.tree.heading("comp", text="COMP. (m)")
        self.tree.heading("peso", text="PESO (kg)")
        
        self.tree.column("pilar", width=150, anchor="center")
        self.tree.column("pos", width=100, anchor="center")
        self.tree.column("bitola", width=100, anchor="center")
        self.tree.column("qtde", width=100, anchor="center")
        self.tree.column("comp", width=100, anchor="center")
        self.tree.column("peso", width=100, anchor="center")

        # Esconder colunas auxiliares de geometria
        self.tree.column("formato", width=0, stretch=tk.NO)
        self.tree.column("medidas", width=0, stretch=tk.NO)
        
        self.tree.pack(fill="both", expand=True)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Status bar
        self.status_frame = tk.Frame(main_container, bg="#1a3d2e", relief="sunken", bd=1)
        self.status_frame.pack(fill="x", pady=(5, 0))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="✅ Pronto para processar",
            bg="#1a3d2e",
            fg="white",
            font=("Arial", 10),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        self.info_label = tk.Label(
            self.status_frame,
            text="",
            bg="#1a3d2e",
            fg="#ff9800",
            font=("Arial", 10, "bold"),
            anchor="e"
        )
        self.info_label.pack(side="right", padx=10, pady=5)
    
    def selecionar_arquivos(self):
        """Seleciona arquivos DXF/DWG"""
        arquivos = filedialog.askopenfilenames(
            title="Selecionar arquivos DXF/DWG de PILARES",
            filetypes=[
                ("Arquivos CAD", "*.dxf *.dwg"),
                ("DXF", "*.dxf"),
                ("DWG", "*.dwg"),
                ("Todos", "*.*")
            ]
        )
        
        if arquivos:
            self.arquivos_selecionados = list(arquivos)
            self.status_label.config(text=f"📁 {len(arquivos)} arquivo(s) selecionado(s)")
            
            nomes = [os.path.basename(f) for f in arquivos]
            if len(nomes) > 3:
                texto = f"{', '.join(nomes[:3])}, ..."
            else:
                texto = ', '.join(nomes)
            self.info_label.config(text=texto)

    def recarregar_treeview(self):
        """Recarrega a Treeview com os dados atuais de self.dados_processados."""
        if not hasattr(self, 'dados_processados') or not self.dados_processados:
            self.total_kg = 0.0
            self.total_barras = 0
            return
        
        try:
            total_kg = sum(dado[5] if len(dado) > 5 else 0.0 for dado in self.dados_processados)
            total_barras = sum(dado[3] if len(dado) > 3 else 0 for dado in self.dados_processados)
        except (TypeError, ValueError, IndexError):
            total_kg = 0.0
            total_barras = 0

        # Limpar treeview
        if hasattr(self, 'tree'):
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Preencher dados com validação
            for dado in self.dados_processados:
                try:
                    if len(dado) >= 8:
                        pilar, pos, bitola, qtde, comp_m, peso_kg, formato, medidas = dado[:8]
                        
                        dado_formatado = (
                            pilar, pos, f"{float(bitola):.1f}", qtde, f"{float(comp_m):.2f}", 
                            f"{float(peso_kg):.2f}", formato, str([round(float(m), 2) for m in medidas])
                        )
                        self.tree.insert("", "end", values=dado_formatado)
                except (ValueError, IndexError, TypeError) as e:
                    print(f"[WARN] Erro ao inserir linha na treeview: {e}")
                    continue
        
        self.total_kg = total_kg
        self.total_barras = total_barras

        # Atualizar label com verificação defensiva
        if hasattr(self, 'info_label'):
            self.info_label.config(text=f"Total: {self.total_barras} barras | {self.total_kg:.2f} kg (Projeto Total)")

    
    def processar(self):
        """Processa os arquivos selecionados - Versão 1 (original)"""
        if not self.arquivos_selecionados:
            messagebox.showwarning("Atenção", "Por favor, selecione os arquivos DXF/DWG primeiro!")
            return
        
        try:
            self.status_label.config(text="⏳ Processando arquivos (V1)...")
            self.update()
            
            # Chama o motor de pilares
            dados_completos, total_kg, total_barras = processar_pilares(self.arquivos_selecionados)
            
            self.dados_processados = dados_completos
            self.total_kg = total_kg
            self.total_barras = total_barras
            
            self.recarregar_treeview()
            
            self.status_label.config(text=f"✅ Processamento V1 concluído")

            # Inicializa ou mantém a seleção de pilares para produção
            pilares_atuais = set(dado[0] for dado in self.dados_processados)
            if not self.pilares_ativos.intersection(pilares_atuais):
                 self.pilares_ativos = pilares_atuais # Se não houver sobreposição, carrega tudo

            if len(self.dados_processados) == 0:
                messagebox.showinfo("Informação", "Nenhum pilar foi encontrado nos arquivos.\n\nVerifique o formato ou a integração do motor.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar (V1):\n{str(e)}")
            self.status_label.config(text="❌ Erro no processamento V1")

    def processar_v2(self):
        """Processa os arquivos selecionados - Versão 2 (motor DXF 2.0 avançado)"""
        if not self.arquivos_selecionados:
            messagebox.showwarning("Atenção", "Por favor, selecione os arquivos DXF/DWG primeiro!")
            return
        
        try:
            # Tentar usar motor v2 se disponível
            from core.pilares_motor_v2 import processar_pilares as motor_v2
        except ImportError:
            # Fallback para motor v1 se v2 não existe
            motor_v2 = None
        
        try:
            self.status_label.config(text="⏳ Processando arquivos (V2 avançado)...")
            self.update()
            
            # Se motor_v2 disponível, usar; senão usar v1
            if motor_v2 is not None:
                dados_completos, total_kg, total_barras = motor_v2(self.arquivos_selecionados)
            else:
                # Fallback para processar_pilares v1
                dados_completos, total_kg, total_barras = processar_pilares(self.arquivos_selecionados)
            
            self.dados_processados = dados_completos
            self.total_kg = total_kg
            self.total_barras = total_barras
            self.arquivos_processados = list(self.arquivos_selecionados)
            
            self.recarregar_treeview()
            
            self.status_label.config(text=f"✅ Processamento V2 concluído")

            # Inicializa ou mantém a seleção de pilares
            pilares_atuais = set(dado[0] for dado in self.dados_processados)
            if not self.pilares_ativos.intersection(pilares_atuais):
                 self.pilares_ativos = pilares_atuais
            
            if len(self.dados_processados) == 0:
                messagebox.showinfo("Informação", "Nenhum pilar foi encontrado nos arquivos.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar (V2):\n{str(e)}")
            self.status_label.config(text="❌ Erro no processamento V2")

    def aplicar_filtro_producao(self) -> Tuple[List[Tuple[str, str, float, int, float, float, str, List[float]]], float, int]:
        """Filtra os dados processados com base nos pilares ativos para geração de relatórios."""
        if not self.dados_processados:
            return [], 0.0, 0
        
        if not self.pilares_ativos:
            return [], 0.0, 0

        # Filtro: (pilar, pos, bitola, qtde, comp_m, peso_kg, formato_dobra, medidas_m)
        dados_filtrados = [dado for dado in self.dados_processados if dado[0] in self.pilares_ativos]
        
        total_kg_filtrado = sum(dado[5] for dado in dados_filtrados)
        total_barras_filtrado = sum(dado[3] for dado in dados_filtrados)
        
        return dados_filtrados, total_kg_filtrado, total_barras_filtrado

    def gerenciar_producao(self):
        """Abre a janela para o usuário selecionar quais pilares produzir."""
        if not self.dados_processados:
            messagebox.showwarning("Atenção", "Processe os arquivos primeiro para identificar os Pilares disponíveis!")
            return

        pilares_unicos = sorted(list(set(dado[0] for dado in self.dados_processados)))
        
        if not pilares_unicos:
            messagebox.showinfo("Informação", "Nenhum Pilar foi encontrado para gerenciar.")
            return

        janela_filtro = tk.Toplevel(self)
        janela_filtro.title("📐 Gerenciar Produção - Seleção de Pilares")
        janela_filtro.geometry("450x550")
        janela_filtro.configure(bg="#0d2818")

        tk.Label(
            janela_filtro, 
            text="Selecione os Pilares para a Próxima Remessa:",
            bg="#0d2818", 
            fg="#ff9800", 
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        # Frame com scrollbar
        frame_scroll = tk.Frame(janela_filtro, bg="#1e1e1e")
        frame_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(frame_scroll, bg="#1e1e1e", borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        scrollable_frame = tk.Frame(canvas, bg="#1e1e1e")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)

        # Variáveis de controle
        checkbox_vars = {}
        
        def toggle_all(master_var):
            state = master_var.get()
            for pilar in pilares_unicos:
                checkbox_vars[pilar].set(state)

        # Checkbox Marcar/Desmarcar Todos
        master_var = tk.BooleanVar(value=all(p in self.pilares_ativos for p in pilares_unicos))
        master_check = tk.Checkbutton(
            scrollable_frame,
            text="Selecionar Todos",
            variable=master_var,
            command=lambda: toggle_all(master_var),
            bg="#1e1e1e",
            fg="#4caf50",
            selectcolor="#1e1e1e",
            font=("Arial", 10, "bold"),
            padx=5,
            pady=5
        )
        master_check.pack(fill="x", pady=(0, 10))

        # Checkboxes para cada pilar
        for pilar in pilares_unicos:
            is_selected = pilar in self.pilares_ativos
            var = tk.BooleanVar(value=is_selected)
            checkbox_vars[pilar] = var
            
            check = tk.Checkbutton(
                scrollable_frame,
                text=pilar,
                variable=var,
                bg="#1e1e1e",
                fg="white",
                selectcolor="#1e1e1e",
                font=("Arial", 10),
                anchor="w",
                padx=5,
                pady=2
            )
            check.pack(fill="x")
        
        # Frame de botões Salvar/Cancelar
        btn_frame = tk.Frame(janela_filtro, bg="#0d2818")
        btn_frame.pack(fill="x", pady=10)

        def salvar_selecao():
            self.pilares_ativos.clear()
            for pilar, var in checkbox_vars.items():
                if var.get():
                    self.pilares_ativos.add(pilar)
            
            # Salvar estado de persistência
            self.salvar_estado_persistencia()
            
            janela_filtro.destroy()
            messagebox.showinfo("Sucesso", f"Produção definida para {len(self.pilares_ativos)} Pilar(es).")
            # Atualiza o info_label principal
            dados_filtrados, total_kg_f, total_barras_f = self.aplicar_filtro_producao()
            self.info_label.config(text=f"Total: {self.total_barras} barras | {self.total_kg:.2f} kg (Filtro: {len(self.pilares_ativos)} ativos)")

        tk.Button(
            btn_frame,
            text="✅ Salvar Seleção",
            command=salvar_selecao,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        ).pack(side="left", padx=10)

        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=janela_filtro.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        ).pack(side="right", padx=10)
    
    def gerar_romaneio(self):
        """Gera romaneio detalhado FILTRADO."""
        dados_filtrados, total_kg, total_barras = self.aplicar_filtro_producao()

        if not dados_filtrados:
            messagebox.showwarning("Atenção", "Nenhum Pilar selecionado ou processado!")
            return
        
        # Restante da lógica de Romaneio... (mantida)

        janela = tk.Toplevel(self)
        janela.title("Romaneio de PILARES - Múltiplas Visualizações")
        janela.geometry("1000x700")
        janela.configure(bg="#0d2818")
        
        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - 500
        y = (janela.winfo_screenheight() // 2) - 350
        janela.geometry(f"1000x700+{x}+{y}")
        
        # Frame superior com botões
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
        
        # Notebook para abas
        notebook = ttk.Notebook(janela)
        notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=[20, 10])
        
        # Função interna para gerar o conteúdo formatado
        def gerar_conteudo_formatado(dados, titulo, cor, agrupamento_chave=None):
            conteudo = []
            conteudo.append("=" * 80)
            conteudo.append(f"                {titulo}")
            conteudo.append("=" * 80)
            conteudo.append(f"Obra:      {self.var_obra.get()}")
            conteudo.append(f"Pavimento: {self.var_pavimento.get()}")
            conteudo.append(f"Pilares Ativos: {', '.join(sorted(list(self.pilares_ativos)))}")
            conteudo.append(f"Data:      {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            conteudo.append("=" * 80)
            conteudo.append("")

            if not dados:
                 conteudo.append("Nenhum dado encontrado para os pilares selecionados.")
                 conteudo.append("=" * 80)
                 return "\n".join(conteudo)

            if agrupamento_chave == 'GERAL':
                pilar_atual = None
                for dado in dados:
                    pilar, pos, bitola, qtde, comp_m, peso_kg, formato_dobra, medidas_m = dado
                    if pilar != pilar_atual:
                        pilar_atual = pilar
                        conteudo.append("")
                        conteudo.append(f">>> {pilar_atual}")
                        conteudo.append("-" * 60)
                    
                    conteudo.append(
                        f"    {pos:<6} Ø{bitola:<6.1f} Qtd: {qtde:<4} "
                        f"Comp: {comp_m:<6.2f}m  Peso: {peso_kg:<8.2f}kg | Forma: {formato_dobra}"
                    )

            elif agrupamento_chave == 'TIPO':
                tipos_agrupados = {}
                for dado in dados:
                    formato_dobra = dado[6]
                    if formato_dobra not in tipos_agrupados:
                        tipos_agrupados[formato_dobra] = []
                    tipos_agrupados[formato_dobra].append(dado)
                
                for tipo in sorted(tipos_agrupados.keys()):
                    conteudo.append("")
                    conteudo.append(f"╔{'═' * 78}╗")
                    conteudo.append(f"║ TIPO: {tipo:<70} ║")
                    conteudo.append(f"╚{'═' * 78}╝")
                    
                    subtotal_tipo = 0.0
                    subtotal_barras = 0
                    
                    for dado in tipos_agrupados[tipo]:
                        pilar, pos, bitola, qtde, comp_m, peso_kg, _, _ = dado
                        conteudo.append(
                            f"      {pilar}/{pos:<6} Ø{bitola:<6.1f} Qtd: {qtde:<4} "
                            f"Comp: {comp_m:<6.2f}m  Peso: {peso_kg:<8.2f}kg"
                        )
                        subtotal_tipo += peso_kg
                        subtotal_barras += qtde
                    
                    conteudo.append("  " + "-" * 60)
                    conteudo.append(f"  Subtotal {tipo}: Barras: {subtotal_barras} | Peso: {subtotal_tipo:.2f} kg")

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
                        pilar, pos, _, qtde, comp_m, peso_kg, formato_dobra, _ = dado
                        conteudo.append(
                            f"      {pilar}/{pos:<6} Qtd: {qtde:<4} Comp: {comp_m:<6.2f}m  "
                            f"Peso: {peso_kg:<8.2f}kg | Forma: {formato_dobra}"
                        )
                        subtotal_peso += peso_kg
                        subtotal_barras += qtde

                    conteudo.append("  " + "-" * 60)
                    conteudo.append(f"  Subtotal Ø {bitola:.1f}mm: Barras: {subtotal_barras} | Peso: {subtotal_peso:.2f} kg")
                    percentual = (subtotal_peso / total_kg) * 100 if total_kg > 0 else 0
                    conteudo.append(f"    Percentual do total: {percentual:.1f}%")
            
            # Rodapé final
            conteudo.append("")
            conteudo.append("=" * 80)
            conteudo.append(f"TOTAL GERAL DE PRODUÇÃO: {total_barras} barras | {total_kg:.2f} kg")
            conteudo.append("=" * 80)
            
            return "\n".join(conteudo)

        # ========== ABA 1: ROMANEIO GERAL ==========
        frame_geral = tk.Frame(notebook, bg="#1e1e1e")
        notebook.add(frame_geral, text="📋 Romaneio Geral")
        texto_geral = ScrolledText(frame_geral, bg="#1e1e1e", fg="#ff9800", font=("Courier New", 10), wrap="none")
        texto_geral.pack(fill="both", expand=True)
        conteudo_geral = gerar_conteudo_formatado(dados_filtrados, "ROMANEIO DE PILARES - GERAL", "#ff9800", 'GERAL')
        texto_geral.insert("1.0", conteudo_geral)

        # ========== ABA 2: POR TIPO DE BARRA ==========
        frame_tipo = tk.Frame(notebook, bg="#1e1e1e")
        notebook.add(frame_tipo, text="🔧 Por Tipo")
        texto_tipo = ScrolledText(frame_tipo, bg="#1e1e1e", fg="#00bcd4", font=("Courier New", 10), wrap="none")
        texto_tipo.pack(fill="both", expand=True)
        conteudo_tipo = gerar_conteudo_formatado(dados_filtrados, "ROMANEIO DE PILARES - POR TIPO DE BARRA", "#00bcd4", 'TIPO')
        texto_tipo.insert("1.0", conteudo_tipo)

        # ========== ABA 3: POR BITOLA ==========
        frame_bitola = tk.Frame(notebook, bg="#1e1e1e")
        notebook.add(frame_bitola, text="📏 Por Bitola")
        texto_bitola = ScrolledText(frame_bitola, bg="#1e1e1e", fg="#4caf50", font=("Courier New", 10), wrap="none")
        texto_bitola.pack(fill="both", expand=True)
        conteudo_bitola = gerar_conteudo_formatado(dados_filtrados, "ROMANEIO DE PILARES - POR BITOLA", "#4caf50", 'BITOLA')
        texto_bitola.insert("1.0", conteudo_bitola)

        # Adicionei a função de atualização de aba para salvar o texto ativo
        def on_tab_changed(event):
            selected_tab = notebook.index(notebook.select())
            textos = [texto_geral, texto_tipo, texto_bitola]
            if selected_tab < len(textos):
                self.texto_ativo = textos[selected_tab]
        
        notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
        self.texto_ativo = texto_geral # Define a primeira aba como ativa

    def gerar_romaneio_conferencia(self):
        """Gera romaneio de conferência (CHECK LIST) FILTRADO."""
        dados_filtrados, total_kg, total_barras = self.aplicar_filtro_producao()

        if not dados_filtrados:
            messagebox.showwarning("Atenção", "Nenhum Pilar selecionado ou processado!")
            return
        
        janela_conf = tk.Toplevel(self)
        janela_conf.title("📋 CHECK LIST - Conferência de Pilares")
        janela_conf.geometry("1100x700")
        janela_conf.configure(bg="#0d2818")
        
        janela_conf.update_idletasks()
        x = (janela_conf.winfo_screenwidth() // 2) - 550
        y = (janela_conf.winfo_screenheight() // 2) - 350
        janela_conf.geometry(f"1100x700+{x}+{y}")
        
        # Frame de botões e título
        top_frame = tk.Frame(janela_conf, bg="#1a3d2e")
        top_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(
            top_frame,
            text="CHECK LIST DE PRODUÇÃO",
            font=("Arial", 14, "bold"),
            bg="#1a3d2e",
            fg="#00acc1"
        ).pack(side="left", padx=10)

        # Botão Salvar Estado (para persistência)
        tk.Button(
            top_frame, 
            text="💾 Salvar Estado", 
            command=self.salvar_estado_persistencia, 
            bg="#5e35b1", 
            fg="white", 
            font=("Arial", 10, "bold")
        ).pack(side="right", padx=10)
        
        # Frame rolante para os Checkboxes
        scroll_frame = tk.Frame(janela_conf, bg="#1e1e1e")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        canvas = tk.Canvas(scroll_frame, bg="#1e1e1e", borderwidth=0, highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        v_scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # O frame interno que contém os widgets
        self.frame_checks = tk.Frame(canvas, bg="#1e1e1e")
        canvas.create_window((0, 0), window=self.frame_checks, anchor="nw")

        self.frame_checks.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Limpar o dicionário de variáveis de controle
        self.checkboxes_conf.clear()
        
        # Cabeçalho da tabela
        header_check = tk.Frame(self.frame_checks, bg="#34495e", relief="raised", bd=1)
        header_check.grid(row=0, column=0, columnspan=9, sticky="ew", padx=2, pady=2)
        
        headers = ["PILAR", "POS", "BITOLA", "QTD", "COMP", "CORTADO", "DOBRADO", "CONFERIDO", "CARREGADO"]
        for col, header in enumerate(headers):
            tk.Label(
                header_check,
                text=header,
                bg="#34495e",
                fg="white",
                font=("Arial", 9, "bold"),
                width=12 if col < 5 else 10
            ).grid(row=0, column=col, padx=2, pady=5)
        
        # Criar checkboxes para cada item FILTRADO
        pilar_atual = None
        row_num = 1
        
        for i, dado in enumerate(dados_filtrados):
            pilar, pos, bitola, qtde, comp_m, _, _, _ = dado
            item_key = (pilar, pos)
            
            # Separador entre pilares diferentes
            if pilar != pilar_atual:
                pilar_atual = pilar
                separator = tk.Frame(self.frame_checks, bg="#ff9800", height=2)
                separator.grid(row=row_num, column=0, columnspan=9, sticky="ew", pady=5)
                row_num += 1
            
            # Frame para cada linha
            bg_color = "#ecf0f1" if row_num % 2 == 0 else "white"
            row_frame = tk.Frame(self.frame_checks, bg=bg_color)
            row_frame.grid(row=row_num, column=0, columnspan=9, sticky="ew", padx=2, pady=1)
            
            # Dados
            tk.Label(row_frame, text=pilar, font=("Arial", 9), width=12, bg=bg_color).grid(row=0, column=0, padx=2)
            tk.Label(row_frame, text=pos, font=("Arial", 9), width=12, bg=bg_color).grid(row=0, column=1, padx=2)
            tk.Label(row_frame, text=f"ø{bitola:.1f}", font=("Arial", 9), width=12, bg=bg_color).grid(row=0, column=2, padx=2)
            tk.Label(row_frame, text=qtde, font=("Arial", 9), width=12, bg=bg_color).grid(row=0, column=3, padx=2)
            tk.Label(row_frame, text=f"{comp_m:.2f}m", font=("Arial", 9), width=12, bg=bg_color).grid(row=0, column=4, padx=2)
            
            # Variáveis e Checkboxes (CORTADO, DOBRADO, CONFERIDO, CARREGADO)
            self.checkboxes_conf[item_key] = {}
            col_start = 5
            
            # Tenta carregar o estado salvo, se existir
            chave_estado = f"{pilar}-{pos}"
            estado_salvo = self.estado_salvo_checklist.get(chave_estado, {})

            for j, status in enumerate(["cortado", "dobrado", "conferido", "carregado"]):
                # Inicializa com o estado salvo, se disponível
                initial_value = estado_salvo.get(status, False) 
                var = tk.BooleanVar(value=initial_value) 
                self.checkboxes_conf[item_key][status] = var
                
                check = tk.Checkbutton(
                    row_frame,
                    variable=var,
                    bg=bg_color,
                    selectcolor=bg_color,
                    activebackground=bg_color,
                    cursor="hand2"
                )
                check.grid(row=0, column=col_start + j, padx=10, pady=2)
            
            row_num += 1
        
        # Ajustar a largura do frame de verificação para preencher a janela
        self.frame_checks.grid_columnconfigure(8, weight=1)
        
        # Botão de Fechar no rodapé
        tk.Button(
            janela_conf,
            text="❌ Fechar Check List",
            command=janela_conf.destroy,
            bg="#757575",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        ).pack(pady=10)

    # --- ETIQUETAS E DESENHO ---
    
    def navegar_proximo(self):
        """Avança para a próxima página de etiquetas na lista filtrada."""
        total_paginas = math.ceil(len(self.dados_etiquetas_filtrados) / self.pecas_por_pagina)
        self.indice_etiqueta_pagina = (self.indice_etiqueta_pagina + 1) % total_paginas
        self.desenhar_pagina_etiquetas_pilares(self.indice_etiqueta_pagina)

    def navegar_anterior(self):
        """Volta para a página anterior de etiquetas na lista filtrada."""
        total_paginas = math.ceil(len(self.dados_etiquetas_filtrados) / self.pecas_por_pagina)
        self.indice_etiqueta_pagina = (self.indice_etiqueta_pagina - 1 + total_paginas) % total_paginas
        self.desenhar_pagina_etiquetas_pilares(self.indice_etiqueta_pagina)

    def desenhar_esquema_geometria(self, canvas: tk.Canvas, forma: str, medidas_m: List[float], x_base: int, y_base: int):
        """
        Desenha o esquema de dobra da barra no canvas (em cm).
        Medidas_m são convertidas para pixels (1cm = 10px)
        """
        canvas.delete("desenho") # Limpa desenhos anteriores
        
        x, y = x_base, y_base
        escala = 10 # 1 cm = 10 pixels (Tamanho ideal para o cartão 10x15)

        medidas_cm = [m * 100 for m in medidas_m]

        def draw_line(x1, y1, x2, y2, tag):
            canvas.create_line(x1, y1, x2, y2, width=3, fill="black", tags=("desenho", tag))

        def draw_dim_h(x1, y1, x2, text):
            # Desenha dimensão horizontal
            offset_y = 10 
            canvas.create_line(x1, y1 - offset_y, x2, y1 - offset_y, fill="#777", dash=(2, 2), tags="desenho")
            canvas.create_text((x1 + x2) / 2, y1 - offset_y - 8, text=text, font=("Arial", 7), fill="#555", tags="desenho")

        def draw_dim_v(x1, y1, y2, text):
            # Desenha dimensão vertical
            offset_x = 10
            canvas.create_line(x1 + offset_x, y1, x1 + offset_x, y2, fill="#777", dash=(2, 2), tags="desenho")
            canvas.create_text(x1 + offset_x + 8, (y1 + y2) / 2, text=text, font=("Arial", 7), fill="#555", tags="desenho")

        if forma.startswith("RETA"):
            if medidas_cm:
                comp_pix = medidas_cm[0] * escala
                draw_line(x, y, x + comp_pix, y, "reta")
                draw_dim_h(x, y, x + comp_pix, f"{medidas_cm[0]:.0f} cm")
        
        elif forma.startswith("DOBRA L") or forma.startswith("BARRA L"):
            if len(medidas_cm) >= 2:
                A_pix = medidas_cm[0] * escala
                B_pix = medidas_cm[1] * escala
                
                draw_line(x, y, x + A_pix, y, "l_a")
                draw_dim_h(x, y, x + A_pix, f"A: {medidas_cm[0]:.0f} cm")
                
                draw_line(x + A_pix, y, x + A_pix, y - B_pix, "l_b")
                draw_dim_v(x + A_pix, y, y - B_pix, f"B: {medidas_cm[1]:.0f} cm")

        elif forma.startswith("BARRA U"):
            if len(medidas_cm) >= 3:
                A_pix = medidas_cm[0] * escala
                B_pix = medidas_cm[1] * escala
                C_pix = medidas_cm[2] * escala
                
                # A: Gancho 1 (Vertical para baixo)
                draw_line(x, y, x, y + A_pix, "u_a")
                draw_dim_v(x, y, y + A_pix, f"A: {medidas_cm[0]:.0f} cm")
                
                # B: Vão (Horizontal)
                draw_line(x, y + A_pix, x + B_pix, y + A_pix, "u_b")
                draw_dim_h(x, y + A_pix, x + B_pix, f"B: {medidas_cm[1]:.0f} cm")
                
                # C: Gancho 2 (Vertical para cima)
                draw_line(x + B_pix, y + A_pix, x + B_pix, y + A_pix - C_pix, "u_c")
                draw_dim_v(x + B_pix, y + A_pix, y + A_pix - C_pix, f"C: {medidas_cm[2]:.0f} cm")

        elif forma.startswith("ESTRIBO"):
            # Estribo Retangular (Medidas A, B)
            if len(medidas_cm) >= 2:
                A_cm = medidas_cm[0]
                B_cm = medidas_cm[1]
                A_pix = A_cm * escala
                B_pix = B_cm * escala
                
                # Desenha o Estribo Retangular, posicionado em x_base, y_base
                x1, y1 = x, y 
                x2, y2 = x + A_pix, y + B_pix

                canvas.create_rectangle(x1, y1, x2, y2, outline="black", width=3, tags="desenho")
                
                # Desenha dimensão Horizontal A
                draw_dim_h(x1, y1, x2, f"A: {A_cm:.0f} cm")
                
                # Desenha dimensão Vertical B
                draw_dim_v(x2, y1, y2, f"B: {B_cm:.0f} cm")
                
                # Simula o gancho de fechamento
                gancho_len = 15 # Tamanho do gancho em pixels (aprox)
                canvas.create_line(x1, y1, x1 - gancho_len, y1 - gancho_len, width=3, fill="black", tags="desenho")
        
        # Título do desenho
        canvas.create_text(x_base + 100, y_base - 70, text="Esquema de Dobra (cm)", font=("Arial", 9, "bold"), fill="#333", tags="desenho")


    def desenhar_etiqueta_card(self, frame_pai: tk.Frame, dado: Tuple[str, str, float, int, float, float, str, List[float]], indice_global: int):
        """Cria um cartão 10x15 simulado com desenho e botão de edição."""
        
        pilar, pos, bitola, qtde, comp_m, peso_kg, formato_dobra, medidas_m = dado
        data_lancamento = datetime.now().strftime('%d/%m/%Y')
        
        # Card Frame (Simulando 10x15)
        card = tk.Frame(frame_pai, width=420, height=300, bg="white", bd=2, relief="groove")
        card.grid_propagate(False) # Mantém o tamanho fixo
        
        # Linha 1: CABEÇALHO (Empreendimento, Pavimento, Data)
        header_context = tk.Frame(card, bg="#f0f0f0", padx=5, pady=2)
        header_context.pack(fill="x")
        
        # Aprimoramento do Cabeçalho para ficar mais próximo do modelo
        # Obra | Pavimento
        tk.Label(header_context, text=f"OBRA: {self.var_obra.get()}", font=("Arial", 7, "bold"), bg="#f0f0f0", fg="#003366").grid(row=0, column=0, sticky="w")
        tk.Label(header_context, text=f"PAVIMENTO: {self.var_pavimento.get()}", font=("Arial", 7, "bold"), bg="#f0f0f0", fg="#003366").grid(row=0, column=1, sticky="w", padx=10)
        
        # Data
        tk.Label(header_context, text=f"LANÇAMENTO: {data_lancamento}", font=("Arial", 7), bg="#f0f0f0", fg="#555").grid(row=0, column=2, sticky="e", padx=5)
        
        header_context.grid_columnconfigure(2, weight=1) # Faz a data ir para a direita

        # Linha 2: TÍTULO (PILAR/POS/BITOLA)
        header_title = tk.Frame(card, bg="#003366")
        header_title.pack(fill="x", ipady=5)
        
        tk.Label(header_title, text=f"PEÇA #{indice_global+1} | {pilar}/{pos}", font=("Arial", 11, "bold"), bg="#003366", fg="white").pack(side="left", padx=5)
        tk.Label(header_title, text=f"Ø {bitola:.1f} MM", font=("Arial", 11, "bold"), bg="#003366", fg="#ffcc00").pack(side="right", padx=5)

        # Linha 3: Detalhes principais
        detail_frame = tk.Frame(card, bg="white", padx=5, pady=5)
        detail_frame.pack(fill="x")
        
        tk.Label(detail_frame, text=f"QTD: {qtde} pçs", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5)
        tk.Label(detail_frame, text=f"COMP. CORTE: {comp_m:.2f} m", font=("Arial", 10, "bold"), fg="#1976d2").grid(row=1, column=0, sticky="w", padx=5)
        tk.Label(detail_frame, text=f"FORMA: {formato_dobra}", font=("Arial", 10), fg="#333").grid(row=2, column=0, sticky="w", padx=5)
        
        # Linha 4: Canvas de Desenho
        draw_canvas = tk.Canvas(card, bg="#f5f5f5", width=380, height=150, bd=1, relief="sunken")
        draw_canvas.pack(padx=5, pady=5)
        
        # Desenha a geometria no canvas específico
        self.desenhar_esquema_geometria(draw_canvas, formato_dobra, medidas_m, x_base=100, y_base=100)

        # Linha 5: Botão de Edição
        btn_edit = tk.Button(
            card,
            text="✏️ Editar Dados",
            command=lambda i=indice_global: self.abrir_edicao_avancada(i),
            bg="#ff5722",
            fg="white",
            font=("Arial", 9, "bold"),
            pady=2,
            cursor="hand2"
        )
        btn_edit.pack(fill="x", padx=5, pady=(0, 5))
        
        return card

    def desenhar_pagina_etiquetas_pilares(self, pagina_indice: int):
        """Desenha uma página inteira de etiquetas (grid de 2x3)."""
        if not self.dados_etiquetas_filtrados:
            return
        
        self.indice_etiqueta_pagina = pagina_indice
        
        # Calcular o range de peças para a página
        start_index = pagina_indice * self.pecas_por_pagina
        end_index = min(start_index + self.pecas_por_pagina, len(self.dados_etiquetas_filtrados))
        
        pecas_na_pagina = self.dados_etiquetas_filtrados[start_index:end_index]
        
        # Limpa o frame de conteúdo da janela de etiquetas
        for widget in self.frame_grid.winfo_children():
             widget.destroy()

        # Atualiza contador de navegação
        total_pecas = len(self.dados_etiquetas_filtrados)
        total_paginas = math.ceil(total_pecas / self.pecas_por_pagina)
        self.contagem_label.config(text=f"Página {pagina_indice + 1} de {total_paginas} ({start_index + 1} a {end_index} de {total_pecas})")
        
        # Desenha o Grid (2 colunas)
        for i, dado in enumerate(pecas_na_pagina):
            row = i // 2
            col = i % 2
            
            card = self.desenhar_etiqueta_card(
                self.frame_grid, 
                dado, 
                indice_global=(start_index + i)
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Garante que o grid se estenda para melhor visualização
        self.frame_grid.grid_columnconfigure(0, weight=1)
        self.frame_grid.grid_columnconfigure(1, weight=1)
        self.janela_etiq.update_idletasks()


    def abrir_edicao_avancada(self, indice_global: int):
        """Abre a janela de edição de forma, quantidade e comprimento para o índice global."""
        if not self.dados_etiquetas_filtrados:
            messagebox.showwarning("Atenção", "Nenhuma peça filtrada para edição.")
            return

        # Dado atual
        dado_original = list(self.dados_etiquetas_filtrados[indice_global])
        pilar, pos, bitola, qtde, comp_m, peso_kg, formato_dobra, medidas_m = dado_original
        bitola_mm = bitola # Bitola é float em mm

        janela_edit = tk.Toplevel(self)
        janela_edit.title(f"✏️ Editar {pilar}/{pos} - Ø{bitola:.1f}")
        janela_edit.geometry("600x650")
        janela_edit.configure(bg="#f0f0f0")
        
        # Frame de Dados Fixos
        frame_fixo = tk.Frame(janela_edit, bg="#e0e0e0", padx=10, pady=10)
        frame_fixo.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_fixo, text=f"Elemento: {pilar}/{pos} | Bitola: Ø{bitola:.1f} mm", font=("Arial", 12, "bold"), bg="#e0e0e0").pack()

        # Variáveis de Controle
        var_qtde = tk.IntVar(value=qtde)
        var_formato = tk.StringVar(value=formato_dobra)
        var_comp_corte_calc = tk.StringVar(value=f"{comp_m:.2f}")
        medida_vars: Dict[str, tk.StringVar] = {}
        
        # --- FUNÇÕES DE LÓGICA DE EDIÇÃO ---

        def recalcular_comp_corte(event=None):
            """Recalcula o comprimento de corte com base nas novas medidas."""
            
            # 1. Coletar medidas atuais (em metros)
            medidas_atuais_m: List[float] = []
            
            for name, var in medida_vars.items():
                try:
                    # Converte de cm para m
                    medida_cm = float(var.get().replace(',', '.'))
                    medidas_atuais_m.append(medida_cm / 100.0) 
                except (ValueError, AttributeError):
                    medidas_atuais_m.append(0.0)
            
            # 2. Recalcular o comprimento total em metros
            novo_formato = var_formato.get()
            novo_comp_m = self._calcular_comp_corte_com_forma(novo_formato, medidas_atuais_m, bitola_mm)
            
            # 3. Atualizar o label de C. Corte calculado
            var_comp_corte_calc.set(f"{novo_comp_m:.2f}")
        
        def atualizar_campos_medida(event=None):
            """Redesenha campos de entrada baseados na forma selecionada."""
            
            # Limpar frame de medidas
            for widget in frame_medidas.winfo_children():
                widget.destroy()
            medida_vars.clear()

            forma_selecionada = var_formato.get()
            
            # Define as letras dos segmentos e os valores iniciais
            segmentos_map: Dict[str, float] = {}
            
            # Inicializa com os valores originais, se o formato for o mesmo
            valores_originais_cm = [m * 100 for m in medidas_m]
            
            if forma_selecionada.startswith("RETA"):
                segmentos_map = {"A": valores_originais_cm[0] if valores_originais_cm else comp_m * 100}
            elif forma_selecionada.startswith("DOBRA L") or forma_selecionada.startswith("BARRA L"):
                 segmentos_map = {"A": valores_originais_cm[0], "B": valores_originais_cm[1]} if len(valores_originais_cm) >= 2 else {"A": 15.0, "B": (comp_m - 0.15) * 100}
            elif forma_selecionada.startswith("BARRA U"):
                segmentos_map = {"A": valores_originais_cm[0], "B": valores_originais_cm[1], "C": valores_originais_cm[2]} if len(valores_originais_cm) >= 3 else {"A": 15.0, "B": (comp_m - 0.30) * 100, "C": 15.0}
            elif forma_selecionada.startswith("ESTRIBO"):
                # Estribo (A, B) - O cálculo faz 2*A + 2*B
                segmentos_map = {"LADO A": valores_originais_cm[0], "LADO B": valores_originais_cm[1]} if len(valores_originais_cm) >= 2 else {"LADO A": 20.0, "LADO B": 30.0}
            elif forma_selecionada.startswith("GRAMPO"):
                 segmentos_map = {"A": valores_originais_cm[0], "B": valores_originais_cm[1], "C": valores_originais_cm[2], "D": valores_originais_cm[3]} if len(valores_originais_cm) >= 4 else {"A": 10.0, "B": 20.0, "C": 10.0, "D": 20.0}
            
            
            # Cria os campos de entrada (em cm)
            for i, (name, valor_inicial_cm) in enumerate(segmentos_map.items()):
                
                tk.Label(frame_medidas, text=f"{name} (cm):", bg="#f0f0f0", font=("Arial", 10)).grid(row=i, column=0, padx=5, pady=5, sticky="w")
                
                var = tk.StringVar(value=f"{valor_inicial_cm:.2f}")
                entry = tk.Entry(frame_medidas, textvariable=var, width=15, font=("Arial", 10))
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
                
                # Adiciona o callback para recalcular ao perder o foco (Leave) ou ao digitar (KeyRelease)
                entry.bind("<KeyRelease>", recalcular_comp_corte)
                entry.bind("<FocusOut>", recalcular_comp_corte)
                
                medida_vars[name] = var

            # Força o primeiro recalculo
            recalcular_comp_corte()

        # --- FRAME DE CONTROLES ---

        # Frame de Quantidade e Forma
        frame_controles = tk.Frame(janela_edit, bg="#f0f0f0", padx=10, pady=5)
        frame_controles.pack(fill="x", padx=10)
        
        # Campo Quantidade
        tk.Label(frame_controles, text="Nova Quantidade:", bg="#f0f0f0", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Entry(frame_controles, textvariable=var_qtde, width=8, font=("Arial", 10)).pack(side="left", padx=10)
        
        # Campo Forma da Dobra (Combo Box)
        formas_disponiveis = ["RETA (01)", "DOBRA L (13)", "BARRA U (11)", "ESTRIBO (12)", "GRAMPO (14)"]
        tk.Label(frame_controles, text="Forma da Dobra:", bg="#f0f0f0", font=("Arial", 10)).pack(side="left", padx=20)
        
        combo_formato = ttk.Combobox(frame_controles, textvariable=var_formato, values=formas_disponiveis, state="readonly", width=15)
        combo_formato.pack(side="left", padx=5)
        combo_formato.bind("<<ComboboxSelected>>", atualizar_campos_medida)
        
        # Frame de Medidas Dinâmicas
        frame_medidas = tk.Frame(janela_edit, bg="#f0f0f0", padx=10, pady=10, relief="groove", bd=1)
        frame_medidas.pack(fill="x", padx=10, pady=5)
        
        atualizar_campos_medida() # Inicializa os campos de medida

        # Frame de Resultados e Botão Salvar
        frame_resultado = tk.Frame(janela_edit, bg="#e0e0e0", padx=10, pady=10)
        frame_resultado.pack(fill="x", padx=10, pady=(10, 0))

        tk.Label(frame_resultado, text="Corte Calculado (m):", font=("Arial", 12, "bold"), bg="#e0e0e0").pack(side="left", padx=5)
        tk.Label(frame_resultado, textvariable=var_comp_corte_calc, font=("Arial", 12, "bold"), bg="#e0e0e0", fg="blue").pack(side="left")

        # --- FUNÇÃO SALVAR ---
        def salvar_edicao():
            try:
                nova_qtde = var_qtde.get()
                novo_formato = var_formato.get()
                
                # 1. Coletar medidas finais em metros
                novas_medidas_m: List[float] = []
                for name, var in medida_vars.items():
                    medida_cm = float(var.get().replace(',', '.'))
                    novas_medidas_m.append(medida_cm / 100.0)
                
                # Dicionário de novos dados para atualização
                novos_dados = {
                    'qtde': nova_qtde,
                    'formato_dobra': novo_formato,
                    'medidas_m': novas_medidas_m
                }
                
                # 3. Atualizar dados globais e Treeview
                self._atualizar_dados_globais(pilar, pos, novos_dados)
                
                messagebox.showinfo("Sucesso", f"Dados da peça {pilar}/{pos} atualizados.")
                janela_edit.destroy()

            except ValueError:
                messagebox.showerror("Erro de Entrada", "Quantidade e medidas devem ser números válidos.")
            except Exception as e:
                messagebox.showerror("Erro de Salvamento", f"Ocorreu um erro ao salvar: {e}")

        tk.Button(
            frame_resultado,
            text="✅ Salvar e Atualizar",
            command=salvar_edicao,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side="right", padx=10)

        janela_edit.transient(self)
        janela_edit.grab_set()
        self.wait_window(janela_edit)

    def gerar_etiquetas(self):
        """Gera etiquetas de corte e dobra para PILARES FILTRADOS."""
        self.dados_etiquetas_filtrados, total_kg, total_barras = self.aplicar_filtro_producao()

        if not self.dados_etiquetas_filtrados:
            messagebox.showwarning("Atenção", "Nenhum Pilar selecionado ou processado!")
            return

        if self.janela_etiq and self.janela_etiq.winfo_exists():
            self.janela_etiq.destroy()

        self.janela_etiq = tk.Toplevel(self)
        self.janela_etiq.title("Etiquetas de Corte e Dobra - PILARES")
        self.janela_etiq.geometry("950x750")
        self.janela_etiq.configure(bg="#f5f5f5")
        
        # Frame de controle (navegação)
        control_frame = tk.Frame(self.janela_etiq, bg="#e0e0e0")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(control_frame, text="Total de Barras Filtradas:", bg="#e0e0e0").pack(side="left", padx=10)
        tk.Label(control_frame, text=f"{total_barras}", bg="#e0e0e0", font=("Arial", 10, "bold")).pack(side="left")
        
        # Rótulo de contagem de peças
        self.contagem_label = tk.Label(control_frame, text="", bg="#e0e0e0", font=("Arial", 10, "bold"), fg="#1976d2")
        self.contagem_label.pack(side="right", padx=10)
        
        # Botões de Navegação (Agora por página)
        tk.Button(control_frame, text="◀ Página Anterior", command=self.navegar_anterior, padx=10).pack(side="right", padx=5)
        tk.Button(control_frame, text="Próxima Página ▶", command=self.navegar_proximo, padx=10).pack(side="right", padx=5)
        
        # Botão Imprimir (Mantido)
        tk.Button(
            control_frame,
            text="🖨️ Imprimir Página",
            command=lambda: messagebox.showinfo("Aviso", "Função Imprimir Etiquetas a ser implementada."),
            bg="#9c27b0",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=2
        ).pack(side="right", padx=20)

        # Frame que contém o GRID das etiquetas
        self.frame_grid = tk.Frame(self.janela_etiq, bg="#cccccc")
        self.frame_grid.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.indice_etiqueta_pagina = 0
        self.desenhar_pagina_etiquetas_pilares(self.indice_etiqueta_pagina)
        self.janela_etiq.transient(self)

    # --- FUNÇÕES AUXILIARES (Salvar/Limpar/Exportar) ---
    
    def exportar_excel(self):
        dados_filtrados, total_kg, total_barras = self.aplicar_filtro_producao()
        
        if not dados_filtrados:
            messagebox.showwarning("Atenção", "Nenhum Pilar selecionado ou processado!")
            return
            
        messagebox.showinfo("Aviso", f"Exportação para Excel iniciada com dados de {len(dados_filtrados)} barras. (Total kg: {total_kg:.2f})")
        
    def limpar(self):
        """Limpa todos os dados da aplicação (Planilhamento, Filtros, Checklist e Estado de Cabeçalho)."""
        
        # Confirmação de segurança
        if not messagebox.askyesno("Confirmação", "Você tem certeza que deseja LIMPAR TODOS OS DADOS (Planilhamento, Filtros e Checklist)? Esta ação é irreversível!"):
            return

        self.arquivos_selecionados = []
        self.dados_processados = []
        self.pilares_ativos = set()
        self.total_kg = 0.0
        self.total_barras = 0
        self.checkboxes_conf.clear()
        self.estado_salvo_checklist.clear() 
        
        # Limpa variáveis do cabeçalho
        self.var_obra.set("OBRA 001")
        self.var_pavimento.set("TÉRREO")
        
        # Tentativa de remover arquivos de estado e planilhamento
        try:
            if os.path.exists(ESTADO_FILEPATH):
                os.remove(ESTADO_FILEPATH)
            if os.path.exists(PLANILHAMENTO_FILEPATH):
                 os.remove(PLANILHAMENTO_FILEPATH)
        except OSError:
            pass
            
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.status_label.config(text="✅ Pronto para processar")
        self.info_label.config(text="")
        messagebox.showinfo("Limpeza", "TODOS os dados de processamento, filtros e estado foram limpos.")

    def salvar_txt(self, conteudo):
        """Salva conteúdo em arquivo texto"""
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt")],
            initialfile=f"romaneio_pilares_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        )
        if arquivo:
            with open(arquivo, "w", encoding="utf-8") as f:
                f.write(conteudo)
            messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")

# Executar aplicação
if __name__ == "__main__":
    app = PilaresApp()
    app.mainloop()