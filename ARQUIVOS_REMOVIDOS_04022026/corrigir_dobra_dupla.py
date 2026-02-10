"""Script para adicionar a opção 'Dobra 2 lados' no vigas_app.py"""

with open('vigas_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Procurar e substituir a lista de formas_opcoes
old_text = '''        formas_opcoes = [
            ("Reta", "reta"),
            ("Gancho", "gancho"),
            ("Dobra 1 lado", "dobra"),
            ("Estribo ret.", "estribo"),
            ("Estribo red.", "estribo_redondo"),
        ]'''

new_text = '''        formas_opcoes = [
            ("Reta", "reta"),
            ("Gancho", "gancho"),
            ("Dobra 1 lado", "dobra"),
            ("Dobra 2 lados", "dobra_dupla"),
            ("Estribo ret.", "estribo"),
            ("Estribo red.", "estribo_redondo"),
        ]'''

if old_text in content:
    content = content.replace(old_text, new_text)
    with open('vigas_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Correção aplicada com sucesso!")
    print("  Adicionado radiobutton: ('Dobra 2 lados', 'dobra_dupla')")
else:
    print("✗ Texto não encontrado. O arquivo pode já estar corrigido.")
