"""Script para adicionar print quando o botão é criado"""

with open('vigas_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar print após criar o botão
old_text = '''        tk.Button(btns, text="✓ Salvar", command=salvar, bg="#27ae60", fg="white", font=("Arial", 11, "bold"), width=12).pack(side="left", padx=10)
        # Botão cancelar apenas limpa campos, não fecha dialog'''

new_text = '''        tk.Button(btns, text="✓ Salvar", command=salvar, bg="#27ae60", fg="white", font=("Arial", 11, "bold"), width=12).pack(side="left", padx=10)
        print(f"[BOTÃO CRIADO] Botão Salvar criado para {chave} com command=salvar")
        # Botão cancelar apenas limpa campos, não fecha dialog'''

if old_text in content:
    content = content.replace(old_text, new_text)
    with open('vigas_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Print adicionado após criar botão")
else:
    print("✗ Texto não encontrado")
