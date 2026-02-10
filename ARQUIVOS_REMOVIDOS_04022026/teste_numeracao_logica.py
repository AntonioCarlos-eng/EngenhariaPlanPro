"""
Teste: Verificar se a renderização agora mostra números corretos
Simula dados_processados com múltiplas vigas e posições
"""
import sys
sys.path.insert(0, r'c:\EngenhariaPlanPro')

# Simular dados como se viessem do motor
dados_teste = [
    ('V8', 'N1', 10.0, 2, 2.95, 18.15),
    ('V8', 'N2', 8.0, 3, 3.00, 20.00),
    ('V8', 'N4', 12.5, 1, 4.50, 30.00),
    ('V10', 'N1', 10.0, 2, 3.50, 21.50),
    ('V10', 'N2', 8.0, 4, 2.80, 17.50),
]

print("="*80)
print("TESTE DE NUMERAÇÃO OS - SIMULANDO GERADOR")
print("="*80)
print()

# Simular a lógica de cálculo de OS número
print("Dados processados:")
print("-"*80)

for idx, (viga, pos, bitola, qtde, comp, peso) in enumerate(dados_teste):
    # Contar quantas vigas iguais existem ANTES desta
    viga_index = 0
    for i in range(idx):
        if dados_teste[i][0] == viga:
            viga_index += 1
    
    # Contar total de vigas iguais
    viga_total = sum(1 for d in dados_teste if d[0] == viga)
    
    # Formatar OS
    os_num = f"{viga_index + 1}-{viga_total}"
    
    print(f"[{idx+1}] {viga:6} {pos:4} Ø{bitola:6.1f} qtd={qtde} → OS={os_num:6}")

print()
print("="*80)
print("VERIFICAÇÃO:")
print("="*80)
print()

vigas = {}
for idx, (viga, pos, bitola, qtde, comp, peso) in enumerate(dados_teste):
    if viga not in vigas:
        vigas[viga] = 0
    vigas[viga] += 1

print("Vigas encontradas:")
for viga in sorted(vigas.keys()):
    print(f"  {viga}: {vigas[viga]} etiquetas")

print()
print("Sequência esperada de OS números:")
print("-"*80)

for idx, (viga, pos, bitola, qtde, comp, peso) in enumerate(dados_teste):
    viga_index = 0
    for i in range(idx):
        if dados_teste[i][0] == viga:
            viga_index += 1
    
    viga_total = sum(1 for d in dados_teste if d[0] == viga)
    os_num = f"{viga_index + 1}-{viga_total}"
    
    print(f"  Etiqueta #{idx+1}: {viga} → OS={os_num:6}")

print()
print("✓ Se a sequência mostrar:")
print("  - V8: 1-3, 2-3, 3-3 (3 etiquetas)")
print("  - V10: 1-2, 2-2 (2 etiquetas)")
print("  Então a lógica está ✓ CORRETA")
print()
