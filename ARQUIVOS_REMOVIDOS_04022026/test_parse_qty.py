import sys
sys.path.insert(0, r'c:\EngenhariaPlanPro')

from core.vigas_motor_v2 import _parse_qty, _parse_pos, _parse_bitola, _parse_comp

# Testes
print("="*80)
print("TESTES DE PARSING")
print("="*80)

# Quantidade
test_qtys = ["18", "2x13", "10X2", "2x5", "2", "3", "7", "62", "2x22"]
print("\n1. QUANTIDADES:")
for t in test_qtys:
    result = _parse_qty(t)
    print(f"  '{t:8s}' => {result}")

# Posição
test_pos = ["N1", "N2", "N3", "N6", "N7", "N10", "N11", "N12", "N13", "N18", "N19"]
print("\n2. POSIÇÕES:")
for t in test_pos:
    result = _parse_pos(t)
    print(f"  '{t:8s}' => {result}")

# Bitola
test_bit = ["%%c 20", "%%c 10", "%%c 8", "%%c 12.5", "%%c 6.3", "%%c 5"]
print("\n3. BITOLAS:")
for t in test_bit:
    result = _parse_bitola(t)
    print(f"  '{t:12s}' => {result}")

# Comprimento
test_comp = ["C=607", "C=94", "C=225", "C=304", "C=511", "C=1190", "C=545"]
print("\n4. COMPRIMENTOS:")
for t in test_comp:
    result = _parse_comp(t)
    print(f"  '{t:12s}' => {result}")
