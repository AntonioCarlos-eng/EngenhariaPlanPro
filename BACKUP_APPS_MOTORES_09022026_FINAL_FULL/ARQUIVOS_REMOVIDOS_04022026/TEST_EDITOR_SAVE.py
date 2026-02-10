"""
TESTE - Abrir editor de etiquetas com dados simulados
"""

import sys
sys.path.insert(0, r'c:\EngenhariaPlanPro')

# Simular dados
dados_teste = [
    ('P1', 'A1', 12.5, 8, 50.0),
    ('P1', 'A2', 10.0, 6, 45.0),
    ('P1', 'A3', 8.0, 10, 40.0),
]

print("=" * 60)
print("TESTE - EDITOR DE ETIQUETAS")
print("=" * 60)
print(f"\nDados simulados: {len(dados_teste)} etiquetas")
for i, d in enumerate(dados_teste):
    print(f"  [{i}] {d}")

print("\n[INSTRUÇÕES]")
print("1. Processe os arquivos DXF normalmente")
print("2. Chegue até a tela 'VIGAS - Editor Etiquetas'")
print("3. Clique em uma ETIQUETA (não no checkbox) para editar")
print("4. Escolha uma FORMA (ex: 'Dobra Única')")
print("5. Preencha as MEDIDAS (ex: Medida Dobra = 5.0)")
print("6. Clique SALVAR")
print("\n[VERIFICAR]")
print("✓ Dialog abre com campos para editar")
print("✓ Combobox muda os campos de medidas")
print("✓ Ao clicar SALVAR, os dados são salvos")
print("✓ Dialog fecha e etiqueta é re-renderizada")
print("✓ Console mostra [DEBUG] mensagens de progresso")

print("\n" + "=" * 60)
print("Iniciando a aplicação...")
print("=" * 60)

# Importar e abrir a aplicação
try:
    from vigas_app import VivasApp
    import tkinter as tk
    
    root = tk.Tk()
    app = VivasApp(root)
    
    # A aplicação será aberta normalmente
    root.mainloop()
    
except Exception as e:
    print(f"[ERRO] {e}")
    import traceback
    traceback.print_exc()
