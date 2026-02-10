#!/usr/bin/env python3
"""
Script para aplicar correção: dividir quantidade quando há expansão com =
"""

import re

arquivo = r"c:\EngenhariaPlanPro\core\pilares_motor_dual.py"

with open(arquivo, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Encontrar e substituir o bloco
old_block = """        # Se houve expansão, replicar dados para cada pilar
        if len(titulos_expandidos) > 1:
            # Há múltiplos pilares na nomenclatura - replicar cada entrada
            for titulo_expandido in titulos_expandidos:
                for entrada_original in linhas_por_posicao.values():
                    nome_original, pos_key, bit, qty, comp_m, peso, formato, medidas = entrada_original
                    # Substituir nome original pelo pilare específico expandido
                    entries.append((
                        titulo_expandido,  # Nome do pilar expandido (P14, P15, etc)
                        pos_key, bit, qty, comp_m, peso, formato, medidas
                    ))"""

new_block = """        # Se houve expansão, replicar dados para cada pilar
        if len(titulos_expandidos) > 1:
            # Há múltiplos pilares na nomenclatura
            # Se '=' presente: dividir quantidades (tabela tem soma)
            # Se '-' presente: replicar quantidades (tabela tem por pilar)
            dividir_quantidade = '=' in title["nome"]
            num_pilares = len(titulos_expandidos)
            
            for titulo_expandido in titulos_expandidos:
                for entrada_original in linhas_por_posicao.values():
                    nome_original, pos_key, bit, qty, comp_m, peso, formato, medidas = entrada_original
                    
                    # Se '=' (dados compartilhados): dividir quantidade e peso
                    if dividir_quantidade:
                        qty_ajustado = qty // num_pilares
                        peso_ajustado = peso / num_pilares
                    else:
                        qty_ajustado = qty
                        peso_ajustado = peso
                    
                    entries.append((
                        titulo_expandido,
                        pos_key, bit, qty_ajustado, comp_m, peso_ajustado, formato, medidas
                    ))"""

if old_block in conteudo:
    conteudo = conteudo.replace(old_block, new_block)
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print("✓ Correção aplicada!")
    print("  - Agora divide quantidade quando há '=' (P14=P32)")
    print("  - Mantém quantidade quando há '-' (P14-P32)")
else:
    print("✗ Bloco não encontrado - arquivo pode ter sido modificado")
