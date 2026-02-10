import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox


def main():
    root = tk.Tk()
    root.title("EngenhariaPlanPro - Launcher")
    root.geometry("620x420")
    root.configure(bg="#0d2818")
    root.resizable(False, False)

    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - 310
    y = (root.winfo_screenheight() // 2) - 210
    root.geometry(f"620x420+{x}+{y}")

    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    header = tk.Frame(root, bg="#1a3d2e", padx=16, pady=14)
    header.grid(row=0, column=0, sticky="ew")

    tk.Label(
        header,
        text="EngenhariaPlanPro",
        bg="#1a3d2e",
        fg="white",
        font=("Segoe UI", 18, "bold")
    ).pack()

    tk.Label(
        header,
        text="Planilhamento automatico profissional",
        bg="#1a3d2e",
        fg="#cde7d8",
        font=("Segoe UI", 11)
    ).pack(pady=(6, 0))

    tk.Frame(header, bg="#2a5a44", height=2).pack(fill="x", pady=(10, 0))

    body = tk.Frame(root, bg="#0d2818", padx=22, pady=18)
    body.grid(row=1, column=0, sticky="nsew")
    body.grid_columnconfigure(0, weight=1)

    card = tk.Frame(body, bg="#123126", padx=24, pady=18, bd=1, relief="solid")
    card.grid(row=0, column=0, sticky="nsew")

    tk.Label(
        card,
        text="Apps disponiveis",
        bg="#123126",
        fg="#cde7d8",
        font=("Segoe UI", 12, "bold")
    ).pack(pady=(0, 10))

    btn_style = {
        "fg": "white",
        "font": ("Segoe UI", 12, "bold"),
        "padx": 10,
        "pady": 10,
        "width": 24,
        "cursor": "hand2",
    }

    status_var = tk.StringVar(value="Status: pronto")
    root._launcher_procs = []

    def _run_app(script_name):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_dir, script_name)
        if not os.path.exists(script_path):
            messagebox.showerror("Erro", f"Arquivo nao encontrado:\n{script_path}")
            return

        log_path = os.path.join(base_dir, "launcher.log")
        try:
            log_file = open(log_path, "a", encoding="utf-8")
        except Exception:
            log_file = None

        try:
            proc = subprocess.Popen(
                [sys.executable, script_path],
                cwd=base_dir,
                stdout=log_file or subprocess.DEVNULL,
                stderr=log_file or subprocess.DEVNULL,
            )
        except Exception as exc:
            if log_file:
                log_file.close()
            messagebox.showerror("Erro", f"Falha ao abrir {script_name}:\n{exc}")
            return

        status_var.set(f"Status: abrindo {script_name}...")
        root._launcher_procs.append((proc, log_file))

        def _check_exit():
            if proc.poll() is None:
                status_var.set("Status: pronto")
                return
            if log_file:
                log_file.flush()
                log_file.close()
            status_var.set("Status: falha ao abrir (ver launcher.log)")
            messagebox.showerror(
                "Erro",
                f"Falha ao abrir {script_name}.\nVeja o arquivo launcher.log."
            )

        root.after(1200, _check_exit)

    tk.Button(
        card,
        text="Vigas",
        command=lambda: _run_app("vigas_app.py"),
        bg="#2e7d32",
        **btn_style,
    ).pack(pady=5)

    tk.Button(
        card,
        text="Pilares",
        command=lambda: _run_app("pilares_app.py"),
        bg="#1565c0",
        **btn_style,
    ).pack(pady=5)

    tk.Button(
        card,
        text="Lajes",
        command=lambda: _run_app("lajes_app.py"),
        bg="#6a1b9a",
        **btn_style,
    ).pack(pady=5)

    footer = tk.Frame(root, bg="#0d2818", padx=12, pady=10)
    footer.grid(row=2, column=0, sticky="ew")
    footer.grid_columnconfigure(0, weight=1)

    tk.Label(
        footer,
        textvariable=status_var,
        bg="#0d2818",
        fg="#7fa792",
        font=("Segoe UI", 9)
    ).grid(row=0, column=0, sticky="w")

    tk.Button(
        footer,
        text="Sair",
        command=root.destroy,
        bg="#757575",
        fg="white",
        font=("Segoe UI", 10),
        padx=16,
        pady=6,
    ).grid(row=0, column=1, sticky="e")

    root.mainloop()


if __name__ == "__main__":
    main()
