import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core.motor_blocos import processar_blocos


class BlocosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EngenhariaPlanPro — Blocos e Estacas")
        self.root.geometry("1600x900")
        self.root.configure(bg="#0e2d1f")

        self.arquivos = []

        # -------------------------
        # BARRA SUPERIOR
        # -------------------------
        frame_top = tk.Frame(root, bg="#0e2d1f")
        frame_top.pack(fill="x", pady=10)

        btn_sel = tk.Button(
            frame_top, text="📁 Selecionar Arquivos",
            command=self.selecionar_arquivos,
            bg="#1a4d8f", fg="white",
            font=("Arial", 12, "bold"), width=20
        )
        btn_sel.pack(side="left", padx=10)

        btn_proc = tk.Button(
            frame_top, text="⚙ Processar",
            command=self.processar,
            bg="#2e8b57", fg="white",
            font=("Arial", 12, "bold"), width=15
        )
        btn_proc.pack(side="left")

        btn_limpar = tk.Button(
            frame_top, text="🗑 Limpar",
            command=self.limpar,
            bg="#b22222", fg="white",
            font=("Arial", 12, "bold"), width=10
        )
        btn_limpar.pack(side="right", padx=10)

        # -------------------------
        # TABELA
        # -------------------------
        colunas = ("elemento", "pos", "bitola", "qtd", "comp", "peso")

        self.tree = ttk.Treeview(root, columns=colunas, show="headings", height=30)

        self.tree.heading("elemento", text="ELEMENTO")
        self.tree.heading("pos", text="POS")
        self.tree.heading("bitola", text="BITOLA (mm)")
        self.tree.heading("qtd", text="QTD (barras)")
        self.tree.heading("comp", text="COMPRIMENTO (m)")
        self.tree.heading("peso", text="PESO TOTAL (kg)")

        self.tree.column("elemento", width=250)
        self.tree.column("pos", width=80)
        self.tree.column("bitola", width=120)
        self.tree.column("qtd", width=120)
        self.tree.column("comp", width=140)
        self.tree.column("peso", width=150)

        self.tree.pack(fill="both", expand=True, padx=15, pady=15)

        # -------------------------
        # STATUS
        # -------------------------
        self.lbl_status = tk.Label(
            root,
            text="0 barras • 0.00 kg",
            bg="#0e2d1f", fg="white",
            font=("Arial", 12)
        )
        self.lbl_status.pack(side="bottom", pady=5)

    # ==========================================================
    # FUNÇÕES
    # ==========================================================
    def selecionar_arquivos(self):
        arqs = filedialog.askopenfilenames(
            title="Selecionar arquivos DXF",
            filetypes=[("Arquivos DXF", "*.dxf")]
        )
        if arqs:
            self.arquivos = list(arqs)
            messagebox.showinfo("Arquivos adicionados",
                                f"{len(self.arquivos)} arquivos selecionados.")

    def limpar(self):
        """ Limpa apenas a tabela, não limpa a lista de arquivos """
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.lbl_status.config(text="0 barras • 0.00 kg")

    def processar(self):
        if not self.arquivos:
            messagebox.showwarning("Aviso", "Selecione arquivos DXF.")
            return

        try:
            dados, total_kg, total_barras = processar_blocos(self.arquivos)

        except Exception as e:
            messagebox.showerror("Erro", str(e))
            return

        # LIMPA SOMENTE A TABELA
        self.limpar()

        # ================================
        # PREENCHER TABELA COM AS CHAVES CORRETAS
        # ================================
        for d in dados:
            self.tree.insert("", "end", values=(
                d.get("elemento", ""),
                d.get("pos", ""),
                d.get("bitola", ""),
                d.get("qtd", ""),
                d.get("comp", ""),  # <=== AQUI ESTÁ A CORREÇÃO REAL
                d.get("peso", "")
            ))

        self.lbl_status.config(text=f"{total_barras} barras • {total_kg:.2f} kg")

        messagebox.showinfo("Processamento concluído", "✔ PROCESSADO")


# ==========================
# EXECUÇÃO
# ==========================
if __name__ == "__main__":
    root = tk.Tk()
    BlocosApp(root)
    root.mainloop()
