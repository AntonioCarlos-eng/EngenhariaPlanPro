#!/usr/bin/env python3
"""Testar se expansão funciona com espaços"""

import sys
sys.path.insert(0, '.')

from core.pilares_motor_dual import _expandir_titulos_pilares

# Teste com espaços (como vem do DXF)
titulo_com_espacos = 'P14=P32   (X2)'
resultado = _expandir_titulos_pilares(titulo_com_espacos)

print(f'Entrada: "{titulo_com_espacos}"')
print(f'Resultado: {resultado}')
print(f'Expandiu? {len(resultado) > 1}')

# Teste sem espaços
titulo_sem_espacos = 'P14=P32(X2)'
resultado2 = _expandir_titulos_pilares(titulo_sem_espacos)

print(f'\nEntrada: "{titulo_sem_espacos}"')
print(f'Resultado: {resultado2}')
print(f'Expandiu? {len(resultado2) > 1}')
