"""Script para corrigir a montagem de medida_dobra com corpo"""

with open('vigas_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corrigir a montagem de medida_dobra para incluir corpo
old_dobra_load = '''                    if forma == 'dobra':
                        # Para dobra única, usar medida_dobra
                        medida_dobra = medidas_dict.get('medida_dobra', 0.0)
                        if medida_dobra and medida_dobra > 0:
                            print(f"✓ Dobra CARREGADA {viga}/{pos}: medida={medida_dobra}cm")
                        else:
                            print(f"⚠ Dobra {viga}/{pos}: medida=0.0cm (VAZIA)")'''

new_dobra_load = '''                    if forma == 'dobra':
                        # Para dobra simples, usar medida_dobra (dobra) e medida_dobra_2 (corpo)
                        m_dobra = medidas_dict.get('medida_dobra', 0.0)
                        m_corpo = medidas_dict.get('medida_dobra_2', 0.0)
                        medida_dobra = (m_dobra, m_corpo)
                        if m_dobra > 0 or m_corpo > 0:
                            print(f"✓ Dobra CARREGADA {viga}/{pos}: dobra={m_dobra}cm, corpo={m_corpo}cm")
                        else:
                            print(f"⚠ Dobra {viga}/{pos}: medida=0.0cm (VAZIA)")'''

content = content.replace(old_dobra_load, new_dobra_load)

# Também corrigir para dobra_dupla incluir o corpo (lado1)
old_dobra_dupla_load = '''                    elif forma == 'dobra_dupla':
                        # Para dobra dupla, usar ambas as medidas
                        m1 = medidas_dict.get('medida_dobra', 0.0)
                        m2 = medidas_dict.get('medida_dobra_2', 0.0)
                        medida_dobra = (m1, m2)
                        if m1 > 0 or m2 > 0:
                            print(f"✓ Dobra Dupla {viga}/{pos}: medidas={m1}cm, {m2}cm")'''

new_dobra_dupla_load = '''                    elif forma == 'dobra_dupla':
                        # Para dobra dupla, usar medida_dobra (dobra1), medida_dobra_2 (dobra2) e lado1 (corpo)
                        m1 = medidas_dict.get('medida_dobra', 0.0)
                        m2 = medidas_dict.get('medida_dobra_2', 0.0)
                        m_corpo = medidas_dict.get('lado1', 0.0)
                        medida_dobra = (m1, m2, m_corpo)
                        if m1 > 0 or m2 > 0 or m_corpo > 0:
                            print(f"✓ Dobra Dupla {viga}/{pos}: dobra1={m1}cm, dobra2={m2}cm, corpo={m_corpo}cm")'''

content = content.replace(old_dobra_dupla_load, new_dobra_dupla_load)

with open('vigas_app.py', 'w', encoding='utf-8') as f:
    f.write(content)
    
print("✓ Montagem de medida_dobra corrigida!")
print("  - Dobra simples: tupla (dobra, corpo)")
print("  - Dobra dupla: tupla (dobra1, dobra2, corpo)")
