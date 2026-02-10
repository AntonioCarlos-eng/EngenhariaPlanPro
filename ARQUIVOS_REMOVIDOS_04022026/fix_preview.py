#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Script para corrigir o preview adicionando informações maiores

arquivo = r'c:\EngenhariaPlanPro\vigas_app.py'

with open(arquivo, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Buscar e substituir
busca = '''            # Informações de identificação na parte superior (E numero da etiqueta)
            info_y = y_cursor + 8
            self.canvas_etiq.create_text(x_base + 8, info_y, text=f"E {i+1}", font=("Arial", int(9*zf), "bold"), fill="#333333", anchor="nw")'''

substituir = '''            # Informações de identificação na parte superior (E numero da etiqueta + Viga/OS)
            info_y = y_cursor + 8
            # Número da etiqueta, Viga (OS) e informações técnicas
            self.canvas_etiq.create_text(x_base + 8, info_y, text=f"E {i+1} | OS: {viga}/{pos}", font=("Arial", int(12*zf), "bold"), fill="#000000", anchor="nw")
            # Informações técnicas em tamanho maior (Bitola, Quantidade, Comprimento)
            info_y2 = y_cursor + 28
            self.canvas_etiq.create_text(x_base + 8, info_y2, text=f"Ø {bitola:.1f}mm | Q: {qtde} | C: {comp:.2f}m", font=("Arial", int(11*zf), "bold"), fill="#000000", anchor="nw")'''

if busca in conteudo:
    conteudo = conteudo.replace(busca, substituir)
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ Arquivo atualizado com sucesso!")
else:
    print("❌ Trecho não encontrado!")
