import sys
import os
import re
sys.path.append('core')

from vigas_motor_v2 import processar_vigas

# Arquivos DXF para teste
arquivos_teste = [
    'dxf/vig terreo f 1-R2 - Copia.DXF',
    # Adicione mais se houver
]

print("Iniciando teste de cobertura total para vigas_motor_v2.py")
print("Arquivos a processar:", arquivos_teste)

try:
    dados, total_kg, total_barras = processar_vigas(arquivos_teste)

    print(f"\nResultado:")
    print(f"Total de barras: {total_barras}")
    print(f"Total de peso (kg): {total_kg}")
    print(f"Número de entradas de dados: {len(dados)}")

    if dados:
        print("\nPrimeiras 5 entradas de dados (viga, pos, bit, qty, comp, peso):")
        for i, d in enumerate(dados[:5]):
            print(f"{i+1}: {d}")
        if len(dados) > 5:
            print(f"... e mais {len(dados)-5} entradas.")
    else:
        print("Nenhum dado foi processado.")

    # Verificações adicionais
    print("\nVerificações:")
    # Verificar se totais fazem sentido
    if total_barras > 0:
        peso_calculado = sum(d[5] for d in dados)
        barras_calculadas = sum(d[3] for d in dados)
        print(f"Peso calculado manualmente: {round(peso_calculado, 2)} kg (deve bater com total_kg)")
        print(f"Barras calculadas manualmente: {barras_calculadas} (deve bater com total_barras)")
        if abs(peso_calculado - total_kg) < 0.01 and barras_calculadas == total_barras:
            print("✓ Totais corretos!")
        else:
            print("✗ Totais incorretos!")
    else:
        print("Nenhuma barra processada.")

    # Verificar ordenação
    if len(dados) > 1:
        def extrair_ordem_viga(nome_viga: str):
            nome_upper = nome_viga.upper()
            if nome_upper.startswith('VN'):
                tipo, resto = 1, nome_upper[2:]
            elif nome_upper.startswith('VT'):
                tipo, resto = 2, nome_upper[2:]
            elif nome_upper.startswith('VP'):
                tipo, resto = 3, nome_upper[2:]
            elif nome_upper.startswith('VB'):
                tipo, resto = 4, nome_upper[2:]
            elif nome_upper.startswith('V'):
                tipo, resto = 0, nome_upper[1:]
            else:
                tipo, resto = 99, nome_upper
            m = re.match(r'(\d+)', resto)
            if m:
                n1 = int(m.group(1)); sufixo = resto[len(m.group(1)):]
            else:
                n1, sufixo = 9999, resto
            n2, letra = 9999, ''
            if '-' in sufixo:
                partes = sufixo.split('-', 1)
                m2 = re.match(r'(\d+)([A-Z]*)', partes[1])
                if m2:
                    n2 = int(m2.group(1)); letra = m2.group(2)
            return (tipo, n1, n2, letra)

        def ordem_final(item):
            viga, pos, bit, qty, comp, peso = item
            v_ord = extrair_ordem_viga(viga)
            try:
                pos_num = int(pos[1:])
            except:
                pos_num = 9999
            return (v_ord, pos_num, bit, comp)

        ordenado = True
        for i in range(1, len(dados)):
            if ordem_final(dados[i-1]) > ordem_final(dados[i]):
                ordenado = False
                break
        if ordenado:
            print("✓ Dados ordenados corretamente!")
        else:
            print("✗ Dados não estão ordenados!")

    print("\nTeste concluído com sucesso!")

except Exception as e:
    print(f"Erro durante o teste: {e}")
    import traceback
    traceback.print_exc()
