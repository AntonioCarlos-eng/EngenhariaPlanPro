"""Script para adicionar debug mínimo na função salvar"""

with open('vigas_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar print após forma_sel = var_forma.get()
old_text = '''            forma_sel = var_forma.get()
            if chave not in self.medidas_customizadas:'''

new_text = '''            forma_sel = var_forma.get()
            print(f"[SALVAR] chave={chave}, forma_sel='{forma_sel}'")
            if chave not in self.medidas_customizadas:'''

if old_text in content:
    content = content.replace(old_text, new_text)
    
    # Adicionar print nas seções de dobra
    old_dobra = '''            # Se for dobra simples, salvar medida (cm) no medidas_customizadas - MESMA LOGICA DO ESTRIBO
            if forma_sel == 'dobra':
                try:
                    vdobra = float(ent_dobra.get()) if ent_dobra.get() else 0.0'''
    
    new_dobra = '''            # Se for dobra simples, salvar medida (cm) no medidas_customizadas - MESMA LOGICA DO ESTRIBO
            if forma_sel == 'dobra':
                try:
                    vdobra = float(ent_dobra.get()) if ent_dobra.get() else 0.0
                    print(f"[SALVAR DOBRA] vdobra={vdobra}")'''
    
    content = content.replace(old_dobra, new_dobra)
    
    # Adicionar print na seção dobra_dupla
    old_dupla = '''            # Se for dobra dupla, salvar ambas medidas - MESMA LOGICA DO ESTRIBO
            if forma_sel == 'dobra_dupla':
                try:
                    vdobra1 = float(ent_dobra.get()) if ent_dobra.get() else 0.0
                    vdobra2 = float(ent_dobra2.get()) if ent_dobra2.get() else 0.0'''
    
    new_dupla = '''            # Se for dobra dupla, salvar ambas medidas - MESMA LOGICA DO ESTRIBO
            if forma_sel == 'dobra_dupla':
                try:
                    vdobra1 = float(ent_dobra.get()) if ent_dobra.get() else 0.0
                    vdobra2 = float(ent_dobra2.get()) if ent_dobra2.get() else 0.0
                    print(f"[SALVAR DOBRA_DUPLA] vdobra1={vdobra1}, vdobra2={vdobra2}")'''
    
    content = content.replace(old_dupla, new_dupla)
    
    with open('vigas_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Debug adicionado com sucesso!")
else:
    print("✗ Texto não encontrado.")
