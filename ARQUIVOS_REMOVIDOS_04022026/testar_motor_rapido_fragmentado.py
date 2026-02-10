"""
Testar Motor Rápido com textos fragmentados simulados
"""

from core.pilares_motor_dual import _processar_textos_fragmentados

# Simular textos fragmentados de um arquivo DXF
# Formato: (texto, x, y)
# Y=50.0 é uma linha com dados
textos_fragmentados = [
    # Título do pilar
    ("PILAR P28", 10, 60.0),
    
    # Linha 1: N1 | ø6.3 | 20 | 350
    ("N1", 15, 50.0),
    ("%%c6.3", 25, 50.0),
    ("20", 35, 50.0),
    ("350", 45, 50.0),
    
    # Linha 2: N2 | ø12.5 | 8 | 450
    ("N2", 15, 45.0),
    ("%%c12.5", 25, 45.0),
    ("8", 35, 45.0),
    ("450", 45, 45.0),
    
    # Outra pilar
    ("P29", 10, 35.0),
    
    # Linha 3: N1 | ø10.0 | 15 | 280
    ("N1", 15, 30.0),
    ("%%c10.0", 25, 30.0),
    ("15", 35, 30.0),
    ("280", 45, 30.0),
]

print("=" * 60)
print("TESTE: Motor Rápido com Textos Fragmentados")
print("=" * 60)

resultado = _processar_textos_fragmentados(textos_fragmentados)

print(f"\n[RESULTADO] Extraídas {len(resultado)} linhas")
print("\nDados processados:")
for i, (pilar, pos, bit, qty, comp, peso, formato, medidas) in enumerate(resultado, 1):
    print(f"  {i}. {pilar} {pos} ø{bit} x{qty} L={comp*100:.0f}cm = {peso:.2f}kg [{formato}]")

total_peso = sum(r[5] for r in resultado)
total_barras = sum(r[3] for r in resultado)
print(f"\nTotal: {total_barras} barras, {total_peso:.2f} kg")

print("\n" + "=" * 60)
if len(resultado) == 3:
    print("✓ TESTE PASSOU: 3 linhas processadas corretamente")
else:
    print(f"✗ TESTE FALHOU: esperado 3 linhas, obtido {len(resultado)}")
