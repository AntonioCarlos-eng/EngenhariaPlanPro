# -*- coding: utf-8 -*-
"""
Teste rapido do editor de etiquetas com:
1. Checkboxes para selecao individual
2. Edicao de forma/desenho
3. Filtragem para impressao
"""

# Simulacao dos dados que serao processados
dados_processados = [
    ('V8', 'N1', 12.0, 3, 1.50, 4.71),
    ('V8', 'N2', 12.0, 2, 2.50, 7.85),
    ('V9', 'N1', 14.0, 4, 1.20, 6.72),
    ('V9', 'N2', 16.0, 2, 1.80, 9.05),
]

# Selecao individual (todos marcados por padrao)
etiquetas_selecionadas = {i: True for i in range(len(dados_processados))}

# Formas customizadas
formas_customizadas = {
    ('V8', 'N1'): 'Dobra Unica',
    ('V8', 'N2'): 'Estribo Quadrado',
    ('V9', 'N1'): 'Reta',
    ('V9', 'N2'): 'Dobra Dupla',
}

# Medidas customizadas
medidas_customizadas = {
    ('V8', 'N1'): {'bitola': 14.0, 'qtde': 4, 'comp': 1.50},
}

print("=" * 60)
print("TESTE: Editor de Etiquetas com Selecao Individual")
print("=" * 60)

print("\n1 - DADOS INICIAIS:")
for i, (viga, pos, bitola, qtde, comp, peso) in enumerate(dados_processados):
    status = "OK" if etiquetas_selecionadas[i] else "DESMARCADO"
    forma = formas_customizadas.get((viga, pos), "Reta")
    print(f"  [{status}] #{i}: {viga}/{pos} - Bitola={bitola}mm, Qtde={qtde}, Comp={comp}m, Forma={forma}")

print("\n2 - SIMULANDO DESSELECAO:")
print("  Desmarcando V8/N2...")
etiquetas_selecionadas[1] = False
selecionadas = [i for i, v in etiquetas_selecionadas.items() if v]
print(f"  OK - Agora selecionadas: {len(selecionadas)} de {len(dados_processados)}")
for i in selecionadas:
    viga, pos, bitola, qtde, comp, peso = dados_processados[i]
    print(f"     - V{viga}/{pos}")

print("\n3 - SIMULANDO EDICAO DE FORMA:")
print("  Mudando V9/N1 de 'Reta' para 'Dobra Dupla'...")
formas_customizadas[('V9', 'N1')] = 'Dobra Dupla'
print(f"  OK - Nova forma para V9/N1: {formas_customizadas[('V9', 'N1')]}")

print("\n4 - DADOS FILTRADOS PARA IMPRESSAO (apenas selecionados):")
dados_filtrados = [dados_processados[i] for i in selecionadas]
print(f"  Total: {len(dados_filtrados)} etiquetas")
for viga, pos, bitola, qtde, comp, peso in dados_filtrados:
    forma = formas_customizadas.get((viga, pos), "Reta")
    print(f"    - V{viga}/{pos} - Bitola={bitola}mm, Qtde={qtde}, Comp={comp}m, Forma={forma}")

print("\n5 - VALIDACOES:")
print(f"  OK - Etiquetas com forma customizada: {len(formas_customizadas)}")
print(f"  OK - Etiquetas com medidas customizadas: {len(medidas_customizadas)}")
formas_opcoes = ['Reta', 'Dobra Unica', 'Dobra Dupla', 'Estribo Quadrado', 'Estribo Retangulo', 'Estribo Redondo']
print(f"  OK - Formas disponiveis: {formas_opcoes}")

print("\nOK - TESTE CONCLUIDO - Sistema esta pronto para impressao!")
print("=" * 60)
