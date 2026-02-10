"""Script para adicionar print no início da função salvar"""

with open('vigas_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar print ANTES do try
old_text = '''        def salvar():
            try:
                novo_bitola = float(ent_bitola.get())'''

new_text = '''        def salvar():
            print(f"\\n[SALVAR CHAMADO!] Função salvar foi executada para {chave}")
            try:
                novo_bitola = float(ent_bitola.get())'''

if old_text in content:
    content = content.replace(old_text, new_text)
    with open('vigas_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Print adicionado no início de salvar()")
else:
    print("✗ Texto não encontrado")
