"""Script para adicionar print no início de _editar_desenho_canvas"""

with open('vigas_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar print logo no início
old_text = '''    def _editar_desenho_canvas(self, viga, pos):
        """Editar o desenho (forma e comprimento) e, para estribo, os 4 lados (A,B,C,D)."""
        chave = (viga, pos)'''

new_text = '''    def _editar_desenho_canvas(self, viga, pos):
        """Editar o desenho (forma e comprimento) e, para estribo, os 4 lados (A,B,C,D)."""
        print(f"\\n[CLIQUE DETECTADO!] _editar_desenho_canvas chamado para {viga}/{pos}")
        chave = (viga, pos)'''

if old_text in content:
    content = content.replace(old_text, new_text)
    with open('vigas_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Print adicionado no início de _editar_desenho_canvas")
else:
    print("✗ Texto não encontrado")
