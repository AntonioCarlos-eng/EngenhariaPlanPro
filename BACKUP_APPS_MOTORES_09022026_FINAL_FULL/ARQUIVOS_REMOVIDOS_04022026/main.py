# main.py - Menu Principal com LAJES
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

class MenuPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("EngenhariaPlanPro - Menu Principal")
        self.geometry("600x500")
        self.configure(bg="#1a1a1a")
        
        # Centralizar janela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 300
        y = (self.winfo_screenheight() // 2) - 250
        self.geometry(f"600x500+{x}+{y}")
        
        self._criar_interface()
    
    def _criar_interface(self):
        # Container principal
        container = tk.Frame(self, bg="#1a1a1a")
        container.pack(expand=True)
        
        # Título
        tk.Label(
            container,
            text="ENGENHARIAPLANPRO",
            font=("Arial", 28, "bold"),
            bg="#1a1a1a",
            fg="#00ff00"
        ).pack(pady=20)
        
        # Subtítulo
        tk.Label(
            container,
            text="Sistema de Planilhamento Instantâneo",
            font=("Arial", 12),
            bg="#1a1a1a",
            fg="#ffffff"
        ).pack(pady=5)
        
        # Frame para botões
        frame_botoes = tk.Frame(container, bg="#1a1a1a")
        frame_botoes.pack(pady=30)
        
        # Botão PILARES
        btn_pilares = tk.Button(
            frame_botoes,
            text="📊 PILARES",
            font=("Arial", 14, "bold"),
            bg="#2e7d32",
            fg="white",
            width=20,
            height=2,
            command=self.abrir_pilares,
            cursor="hand2",
            relief="raised",
            bd=3
        )
        btn_pilares.pack(pady=10)
        
        # Botão VIGAS
        btn_vigas = tk.Button(
            frame_botoes,
            text="📐 VIGAS",
            font=("Arial", 14, "bold"),
            bg="#c62828",
            fg="white",
            width=20,
            height=2,
            command=self.abrir_vigas,
            cursor="hand2",
            relief="raised",
            bd=3
        )
        btn_vigas.pack(pady=10)
        
        # NOVO - Botão LAJES
        btn_lajes = tk.Button(
            frame_botoes,
            text="🏗️ LAJES",
            font=("Arial", 14, "bold"),
            bg="#1565c0",
            fg="white",
            width=20,
            height=2,
            command=self.abrir_lajes,
            cursor="hand2",
            relief="raised",
            bd=3
        )
        btn_lajes.pack(pady=10)
        
        # Botão SAIR
        btn_sair = tk.Button(
            frame_botoes,
            text="❌ SAIR",
            font=("Arial", 12),
            bg="#424242",
            fg="white",
            width=20,
            height=2,
            command=self.sair,
            cursor="hand2",
            relief="raised",
            bd=2
        )
        btn_sair.pack(pady=20)
        
        # Rodapé
        tk.Label(
            self,
            text="Versão 2.1 - Sistema com Lajes",
            font=("Arial", 9),
            bg="#1a1a1a",
            fg="#666666"
        ).pack(side="bottom", pady=10)
    
    def abrir_pilares(self):
        try:
            subprocess.Popen([sys.executable, "pilares_app.py"])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir Pilares:\n{str(e)}")
    
    def abrir_vigas(self):
        try:
            subprocess.Popen([sys.executable, "vigas_app.py"])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir Vigas:\n{str(e)}")
    
    def abrir_lajes(self):
        try:
            subprocess.Popen([sys.executable, "lajes_app.py"])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir Lajes:\n{str(e)}")
    
    def sair(self):
        if messagebox.askyesno("Confirmar", "Deseja realmente sair?"):
            self.destroy()

if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()