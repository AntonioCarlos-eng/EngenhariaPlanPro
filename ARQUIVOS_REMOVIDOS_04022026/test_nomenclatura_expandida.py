#!/usr/bin/env python3
"""
Teste da lógica de expansão de nomenclatura de pilares
Validar que P14-P32, P32(X2), P14;P32, etc funcionam corretamente
"""

import sys
sys.path.insert(0, r"c:\EngenhariaPlanPro")

from core.pilares_motor_dual import _expandir_titulos_pilares

# Casos de teste
testes = [
    ("P1", ["P1"]),
    ("P2", ["P2"]),
    ("P14-P32", [f"P{i}" for i in range(14, 33)]),  # 19 pilares - INTERVALO
    ("P14=P32", ["P14", "P32"]),  # 2 pilares com dados compartilhados (NÃO intervalo!)
    ("P14=P32(X2)", ["P14", "P32"]),  # 2 pilares - (X2) é confirmação
    ("P14=P32=P35(X3)", ["P14", "P32", "P35"]),  # 3 pilares com dados compartilhados - NOVO!
    ("P14-P32(X2)", [f"P{i}" for i in range(14, 33)]),  # Intervalo (hífen)
    ("P32(X2)", ["P32"]),  # Pilare simples
    ("P14;P32", ["P14", "P32"]),
    ("P14/P32", ["P14", "P32"]),
    ("P1-P5", [f"P{i}" for i in range(1, 6)]),  # 5 pilares - INTERVALO
    ("P10", ["P10"]),
]

print("=" * 70)
print("TESTE DE EXPANSÃO DE NOMENCLATURA DE PILARES")
print("=" * 70)

erros = 0
sucessos = 0

for entrada, esperado in testes:
    resultado = _expandir_titulos_pilares(entrada)
    passou = resultado == esperado
    
    status = "✓ PASSOU" if passou else "✗ FALHOU"
    print(f"\n{status}")
    print(f"  Entrada:   {entrada}")
    print(f"  Esperado:  {esperado}")
    print(f"  Obtido:    {resultado}")
    
    if not passou:
        erros += 1
        print(f"  Diferença:")
        faltando = set(esperado) - set(resultado)
        extras = set(resultado) - set(esperado)
        if faltando:
            print(f"    Faltando: {faltando}")
        if extras:
            print(f"    Extras: {extras}")
    else:
        sucessos += 1

print("\n" + "=" * 70)
print(f"RESULTADO: {sucessos} sucessos, {erros} falhas")
print("=" * 70)

sys.exit(0 if erros == 0 else 1)
