"""Script para ajustar campos de dobra/gancho"""

with open('vigas_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corrigir gancho para ter 3 campos (A, B, Corpo)
old_gancho = '''            elif forma == "gancho":
                f = tk.Frame(frame_medidas, bg="#0d2818")
                f.pack(pady=5)
                tk.Label(f, text="Lado 1 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
                tk.Entry(f, textvariable=var_lado1, width=12, font=("Arial", 10)).pack(side="left", padx=5)
                f2 = tk.Frame(frame_medidas, bg="#0d2818")
                f2.pack(pady=5)
                tk.Label(f2, text="Lado 2 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
                tk.Entry(f2, textvariable=var_lado2, width=12, font=("Arial", 10)).pack(side="left", padx=5)'''

new_gancho = '''            elif forma == "gancho":
                f = tk.Frame(frame_medidas, bg="#0d2818")
                f.pack(pady=3)
                tk.Label(f, text="Dobra A (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9)).pack(side="left", padx=5)
                tk.Entry(f, textvariable=var_lado1, width=10, font=("Arial", 10)).pack(side="left", padx=5)
                f2 = tk.Frame(frame_medidas, bg="#0d2818")
                f2.pack(pady=3)
                tk.Label(f2, text="Dobra B (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9)).pack(side="left", padx=5)
                tk.Entry(f2, textvariable=var_lado2, width=10, font=("Arial", 10)).pack(side="left", padx=5)
                f3 = tk.Frame(frame_medidas, bg="#0d2818")
                f3.pack(pady=3)
                tk.Label(f3, text="Corpo (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9)).pack(side="left", padx=5)
                tk.Entry(f3, textvariable=var_lado3, width=10, font=("Arial", 10)).pack(side="left", padx=5)'''

content = content.replace(old_gancho, new_gancho)

# Corrigir dobra simples para ter 2 campos (Dobra + Corpo)
old_dobra = '''            elif forma == "dobra":
                f = tk.Frame(frame_medidas, bg="#0d2818")
                f.pack(pady=5)
                tk.Label(f, text="Dobra (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
                tk.Entry(f, textvariable=var_medida_dobra, width=12, font=("Arial", 10)).pack(side="left", padx=5)'''

new_dobra = '''            elif forma == "dobra":
                f = tk.Frame(frame_medidas, bg="#0d2818")
                f.pack(pady=3)
                tk.Label(f, text="Dobra (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9)).pack(side="left", padx=5)
                tk.Entry(f, textvariable=var_medida_dobra, width=10, font=("Arial", 10)).pack(side="left", padx=5)
                f2 = tk.Frame(frame_medidas, bg="#0d2818")
                f2.pack(pady=3)
                tk.Label(f2, text="Corpo (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9)).pack(side="left", padx=5)
                tk.Entry(f2, textvariable=var_medida_dobra_2, width=10, font=("Arial", 10)).pack(side="left", padx=5)'''

content = content.replace(old_dobra, new_dobra)

# Corrigir dobra_dupla para ter 3 campos (Dobra 1 + Dobra 2 + Corpo)
old_dobra_dupla = '''            elif forma == "dobra_dupla":
                f1 = tk.Frame(frame_medidas, bg="#0d2818")
                f1.pack(pady=5)
                tk.Label(f1, text="Dobra 1 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
                tk.Entry(f1, textvariable=var_medida_dobra, width=12, font=("Arial", 10)).pack(side="left", padx=5)
                f2 = tk.Frame(frame_medidas, bg="#0d2818")
                f2.pack(pady=5)
                tk.Label(f2, text="Dobra 2 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9, "bold")).pack(side="left", padx=5)
                tk.Entry(f2, textvariable=var_medida_dobra_2, width=12, font=("Arial", 10)).pack(side="left", padx=5)'''

new_dobra_dupla = '''            elif forma == "dobra_dupla":
                f1 = tk.Frame(frame_medidas, bg="#0d2818")
                f1.pack(pady=3)
                tk.Label(f1, text="Dobra 1 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9)).pack(side="left", padx=5)
                tk.Entry(f1, textvariable=var_medida_dobra, width=10, font=("Arial", 10)).pack(side="left", padx=5)
                f2 = tk.Frame(frame_medidas, bg="#0d2818")
                f2.pack(pady=3)
                tk.Label(f2, text="Dobra 2 (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9)).pack(side="left", padx=5)
                tk.Entry(f2, textvariable=var_medida_dobra_2, width=10, font=("Arial", 10)).pack(side="left", padx=5)
                f3 = tk.Frame(frame_medidas, bg="#0d2818")
                f3.pack(pady=3)
                tk.Label(f3, text="Corpo (cm):", bg="#0d2818", fg="#ffcc00", font=("Arial", 9)).pack(side="left", padx=5)
                tk.Entry(f3, textvariable=var_lado1, width=10, font=("Arial", 10)).pack(side="left", padx=5)'''

content = content.replace(old_dobra_dupla, new_dobra_dupla)

with open('vigas_app.py', 'w', encoding='utf-8') as f:
    f.write(content)
    
print("✓ Campos refinados!")
print("  - Gancho: 3 campos (Dobra A, Dobra B, Corpo)")
print("  - Dobra simples: 2 campos (Dobra, Corpo)")
print("  - Dobra dupla: 3 campos (Dobra 1, Dobra 2, Corpo)")
print("  - Campos menores e mais espaçados para caber melhor")
