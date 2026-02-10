"""
Testar Motor Rápido com dados reais de arquivo fragmentado
Simulando a estrutura do arquivo pilares-030.DXF
"""

from core.pilares_motor_dual import _processar_textos_fragmentados

# Dados extraídos de pilares-030.DXF - formato fragmentado
# Y= 58.1 linha com cabeçalho e primeira linha de dados
# Padrão: PILAR P28 | AÇO | POS | BIT | QUANT | COMPRIMENTO

textos_reais = [
    # Título do pilar (Y=61.0)
    ("PILAR", 8.5, 61.0),
    ("P28", 13.0, 61.0),
    
    # Cabeçalho (Y=58.1)
    ("AÇO", 15.2, 58.1),
    ("POS", 18.5, 58.1),
    ("BIT", 22.3, 58.1),
    ("QUANT", 26.8, 58.1),
    ("COMPRIMENTO", 32.5, 58.1),
    
    # Dados linha 1 (Y=55.0) - N1 | ø6.3 | 22 | 365
    ("N1", 18.5, 55.0),
    ("%%c", 21.8, 55.0),
    ("6.3", 23.0, 55.0),
    ("22", 26.8, 55.0),
    ("365", 32.5, 55.0),
    
    # Dados linha 2 (Y=52.0) - N2 | ø8.0 | 16 | 285
    ("N2", 18.5, 52.0),
    ("%%c", 21.8, 52.0),
    ("8.0", 23.0, 52.0),
    ("16", 26.8, 52.0),
    ("285", 32.5, 52.0),
    
    # Novo pilar (Y=48.0)
    ("PILAR", 8.5, 48.0),
    ("P29", 13.0, 48.0),
    
    # Dados linha 3 (Y=42.0) - N1 | ø12.5 | 4 | 480
    ("N1", 18.5, 42.0),
    ("%%c", 21.8, 42.0),
    ("12.5", 23.0, 42.0),
    ("4", 26.8, 42.0),
    ("480", 32.5, 42.0),
    
    # Dados linha 4 (Y=39.0) - N2 | ø10.0 | 12 | 320
    ("N2", 18.5, 39.0),
    ("%%c", 21.8, 39.0),
    ("10.0", 23.0, 39.0),
    ("12", 26.8, 39.0),
    ("320", 32.5, 39.0),
]

print("=" * 70)
print("TESTE: Motor Rápido com Dados Reais (formato fragmentado)")
print("=" * 70)
print(f"\nTotal de textos: {len(textos_reais)}")

resultado = _processar_textos_fragmentados(textos_reais)

print(f"\n[RESULTADO] Extraídas {len(resultado)} linhas")
print("\nDados processados:")
for i, (pilar, pos, bit, qty, comp, peso, formato, medidas) in enumerate(resultado, 1):
    print(f"  {i}. {pilar} {pos} ø{bit} x{qty} L={comp*100:.0f}cm = {peso:.2f}kg [{formato}]")

total_peso = sum(r[5] for r in resultado)
total_barras = sum(r[3] for r in resultado)
print(f"\nTotal: {total_barras} barras, {total_peso:.2f} kg")

print("\n" + "=" * 70)
if len(resultado) == 4:
    print("✓ TESTE PASSOU: 4 linhas processadas (2 do P28 + 2 do P29)")
    print("\nDetalhes esperados:")
    print("  P28: N1 (22x365cm) + N2 (16x285cm)")
    print("  P29: N1 (4x480cm) + N2 (12x320cm)")
else:
    print(f"✗ TESTE FALHOU: esperado 4 linhas, obtido {len(resultado)}")
