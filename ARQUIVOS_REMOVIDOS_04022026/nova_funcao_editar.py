import tkinter as tk
from tkinter import ttk

def _editar_etiqueta_dados(self, idx, viga, pos, bitola, qtde, comp):
    """Abre diálogo para editar dados + FORMA/DESENHO + MEDIDAS ESPECÍFICAS por tipo"""
    dado = self.dados_processados[idx]
    
    # Diálogo de edição
    dialog = tk.Toplevel(self.janela_editor)
    dialog.title(f"Editar Etiqueta #{idx+1} - {viga}/{pos}")
    dialog.geometry("520x550")
    dialog.configure(bg="#0d2818")
    
    # Centralizar no editor
    dialog.update_idletasks()
    x = self.janela_editor.winfo_x() + 400
    y = self.janela_editor.winfo_y() + 200
    dialog.geometry(f"520x550+{x}+{y}")
    
    # Campos de edição
    tk.Label(dialog, text=f"Editar: V{viga} {pos}", bg="#0d2818", fg="#ff9800", 
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
    var_comp = tk.DoubleVar(value=comp)
    tk.Entry(frame3, textvariable=var_comp, width=10, font=("Arial", 10)).pack(side="left", padx=5)
    
    # FORMA/DESENHO
    frame4 = tk.Frame(dialog, bg="#0d2818")
    frame4.pack(padx=10, pady=5)
    tk.Label(frame4, text="Forma/Desenho:", bg="#0d2818", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
    
    formas_disponiveis = ["Reta", "Dobra Única", "Dobra Dupla", "Estribo Quadrado", "Estribo Retângulo", "Estribo Redondo"]
    
    forma_atual = self.formas_customizadas.get((viga, pos), "Reta")
    if isinstance(forma_atual, str):
        if "dupla" in forma_atual.lower():
            forma_atual = "Dobra Dupla"
        elif "única" in forma_atual.lower() or "unica" in forma_atual.lower():
            forma_atual = "Dobra Única"
        elif "quadrado" in forma_atual.lower():
            forma_atual = "Estribo Quadrado"
        elif "retângulo" in forma_atual.lower() or "retangulo" in forma_atual.lower():
            forma_atual = "Estribo Retângulo"
        elif "redondo" in forma_atual.lower():
            forma_atual = "Estribo Redondo"
        else:
            forma_atual = "Reta"
    
    var_forma = tk.StringVar(value=forma_atual)
    combo_forma = ttk.Combobox(frame4, textvariable=var_forma, values=formas_disponiveis, 
                               state="readonly", width=20)
    combo_forma.set(forma_atual)  # Garantir seleção inicial
    combo_forma.pack(side="left", padx=5)
    
    # FRAME para medidas dinâmicas
    frame_medidas = tk.Frame(dialog, bg="#0d2818")
    frame_medidas.pack(padx=10, pady=5, fill="both", expand=True)
    
    # Obter valores atuais
    medidas_atual = self.medidas_customizadas.get((viga, pos), {})
    
    # Variáveis para medidas
    var_medida_dobra = tk.DoubleVar(value=medidas_atual.get('medida_dobra', 0.0))
    var_medida_dobra_2 = tk.DoubleVar(value=medidas_atual.get('medida_dobra_2', 0.0))
    var_lado1 = tk.DoubleVar(value=medidas_atual.get('lado1', 0.0))
    var_lado2 = tk.DoubleVar(value=medidas_atual.get('lado2', 0.0))
    var_lado3 = tk.DoubleVar(value=medidas_atual.get('lado3', 0.0))
    var_lado4 = tk.DoubleVar(value=medidas_atual.get('lado4', 0.0))
    var_raio = tk.DoubleVar(value=medidas_atual.get('raio', 0.0))
    
    def atualizar_campos_forma(*args):
        """Mostrar/ocultar campos conforme forma"""
        for widget in frame_medidas.winfo_children():
            widget.destroy()
        
        forma = var_forma.get()
        
        if forma == "Reta":
            tk.Label(frame_medidas, text="(Sem medidas adicionais)", bg="#0d2818", fg="#888888", 
                    font=("Arial", 9)).pack(pady=10)
        elif forma == "Dobra Única":
            f = tk.Frame(frame_medidas, bg="#0d2818")
            f.pack(pady=5)
            tk.Label(f, text="Medida Dobra (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
            tk.Entry(f, textvariable=var_medida_dobra, width=12, font=("Arial", 10)).pack(side="left", padx=5)
        elif forma == "Dobra Dupla":
            f1 = tk.Frame(frame_medidas, bg="#0d2818")
            f1.pack(pady=5)
            tk.Label(f1, text="1ª Dobra (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
            tk.Entry(f1, textvariable=var_medida_dobra, width=12, font=("Arial", 10)).pack(side="left", padx=5)
            f2 = tk.Frame(frame_medidas, bg="#0d2818")
            f2.pack(pady=5)
            tk.Label(f2, text="2ª Dobra (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
            tk.Entry(f2, textvariable=var_medida_dobra_2, width=12, font=("Arial", 10)).pack(side="left", padx=5)
        elif forma == "Estribo Quadrado":
            for i, var, label_txt in [(1, var_lado1, "Lado 1 (cm):"),
                                      (2, var_lado2, "Lado 2 (cm):"),
                                      (3, var_lado3, "Lado 3 (cm):"),
                                      (4, var_lado4, "Lado 4 (cm):")]:
                f = tk.Frame(frame_medidas, bg="#0d2818")
                f.pack(pady=3)
                tk.Label(f, text=label_txt, bg="#0d2818", fg="#ffcc00", font=("Arial", 9)).pack(side="left", padx=5)
                tk.Entry(f, textvariable=var, width=12, font=("Arial", 10)).pack(side="left", padx=5)
        elif forma == "Estribo Retângulo":
            f1 = tk.Frame(frame_medidas, bg="#0d2818")
            f1.pack(pady=5)
            tk.Label(f1, text="Largura (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
            tk.Entry(f1, textvariable=var_lado1, width=12, font=("Arial", 10)).pack(side="left", padx=5)
            tk.Label(f1, text="Altura (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9)).pack(side="left", padx=5)
            tk.Entry(f1, textvariable=var_lado2, width=12, font=("Arial", 10)).pack(side="left", padx=5)
            f2 = tk.Frame(frame_medidas, bg="#0d2818")
            f2.pack(pady=5)
            tk.Label(f2, text="Lado 3 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9)).pack(side="left", padx=5)
            tk.Entry(f2, textvariable=var_lado3, width=12, font=("Arial", 10)).pack(side="left", padx=5)
            tk.Label(f2, text="Lado 4 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9)).pack(side="left", padx=5)
            tk.Entry(f2, textvariable=var_lado4, width=12, font=("Arial", 10)).pack(side="left", padx=5)
        elif forma == "Estribo Redondo":
            f = tk.Frame(frame_medidas, bg="#0d2818")
            f.pack(pady=5)
            tk.Label(f, text="Raio (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
            tk.Entry(f, textvariable=var_raio, width=12, font=("Arial", 10)).pack(side="left", padx=5)
    
    combo_forma.bind("<<ComboboxSelected>>", atualizar_campos_forma)
    atualizar_campos_forma()
    
    # Botões
    btn_frame = tk.Frame(dialog, bg="#0d2818")
    btn_frame.pack(pady=15)
    
    def salvar_edicao():
        peso_novo = dado[5] if len(dado) > 5 else 0
        self.dados_processados[idx] = (viga, pos, var_bitola.get(), var_qtde.get(), var_comp.get(), peso_novo)
        
        medidas_novo = {
            'bitola': var_bitola.get(),
            'qtde': var_qtde.get(),
            'comp': var_comp.get(),
            'medida_dobra': var_medida_dobra.get(),
            'medida_dobra_2': var_medida_dobra_2.get(),
            'lado1': var_lado1.get(),
            'lado2': var_lado2.get(),
            'lado3': var_lado3.get(),
            'lado4': var_lado4.get(),
            'raio': var_raio.get()
        }
        self.medidas_customizadas[(viga, pos)] = medidas_novo
        
        forma_selecionada = var_forma.get()
        self.formas_customizadas[(viga, pos)] = forma_selecionada
        
        dialog.destroy()
        self.desenhar_etiquetas_com_selecao()
    
    tk.Button(btn_frame, text="✅ SALVAR", command=salvar_edicao,
             bg="#27ae60", fg="white", font=("Arial", 10), padx=15, pady=5).pack(side="left", padx=5)
    tk.Button(btn_frame, text="✕ CANCELAR", command=dialog.destroy,
             bg="#e74c3c", fg="white", font=("Arial", 10), padx=15, pady=5).pack(side="left", padx=5)
