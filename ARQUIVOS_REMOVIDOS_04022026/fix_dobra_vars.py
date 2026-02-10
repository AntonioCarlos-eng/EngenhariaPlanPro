"""Script para corrigir os campos de dobra para usar var_medida_dobra"""

with open('vigas_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corrigir dobra simples (linha ~3879-3886)
old_dobra = '''            elif forma == "dobra":
                f = tk.Frame(frame_medidas, bg="#0d2818")
                f.pack(pady=5)
                tk.Label(f, text="Lado 1 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
                tk.Entry(f, textvariable=var_lado1, width=12, font=("Arial", 10)).pack(side="left", padx=5)
                f2 = tk.Frame(frame_medidas, bg="#0d2818")
                f2.pack(pady=5)
                tk.Label(f2, text="Lado 2 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
                tk.Entry(f2, textvariable=var_lado2, width=12, font=("Arial", 10)).pack(side="left", padx=5)'''

new_dobra = '''            elif forma == "dobra":
                f = tk.Frame(frame_medidas, bg="#0d2818")
                f.pack(pady=5)
                tk.Label(f, text="Dobra (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
                tk.Entry(f, textvariable=var_medida_dobra, width=12, font=("Arial", 10)).pack(side="left", padx=5)'''

content = content.replace(old_dobra, new_dobra)

# Corrigir dobra_dupla (linha ~3887-3897)
old_dobra_dupla = '''            elif forma == "dobra_dupla":
                f1 = tk.Frame(frame_medidas, bg="#0d2818")
                f1.pack(pady=5)
                tk.Label(f1, text="Lado 1 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
                tk.Entry(f1, textvariable=var_lado1, width=12, font=("Arial", 10)).pack(side="left", padx=5)
                f2 = tk.Frame(frame_medidas, bg="#0d2818")
                f2.pack(pady=5)
                tk.Label(f2, text="Lado 2 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
                tk.Entry(f2, textvariable=var_lado2, width=12, font=("Arial", 10)).pack(side="left", padx=5)
                f3 = tk.Frame(frame_medidas, bg="#0d2818")
                f3.pack(pady=5)
                tk.Label(f3, text="Lado 3 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
                tk.Entry(f3, textvariable=var_lado3, width=12, font=("Arial", 10)).pack(side="left", padx=5)'''

new_dobra_dupla = '''            elif forma == "dobra_dupla":
                f1 = tk.Frame(frame_medidas, bg="#0d2818")
                f1.pack(pady=5)
                tk.Label(f1, text="Dobra 1 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
                tk.Entry(f1, textvariable=var_medida_dobra, width=12, font=("Arial", 10)).pack(side="left", padx=5)
                f2 = tk.Frame(frame_medidas, bg="#0d2818")
                f2.pack(pady=5)
                tk.Label(f2, text="Dobra 2 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
                tk.Entry(f2, textvariable=var_medida_dobra_2, width=12, font=("Arial", 10)).pack(side="left", padx=5)'''

content = content.replace(old_dobra_dupla, new_dobra_dupla)

with open('vigas_app.py', 'w', encoding='utf-8') as f:
    f.write(content)
    
print("✓ Correção aplicada!")
print("  - Dobra agora usa var_medida_dobra")
print("  - Dobra_dupla agora usa var_medida_dobra e var_medida_dobra_2")
