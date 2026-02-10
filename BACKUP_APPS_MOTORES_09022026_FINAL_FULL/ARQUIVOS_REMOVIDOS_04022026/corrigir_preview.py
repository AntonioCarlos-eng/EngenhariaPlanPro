#!/usr/bin/env python3
import re

# Ler arquivo
with open(r'c:\EngenhariaPlanPro\vigas_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar a linha com o texto a ser substituído
for i, line in enumerate(lines):
    if 'self.canvas_etiq.create_text(x_base + 8, info_y, text=f"E {i+1}"' in line:
        # Substituir a linha e adicionar nova linha depois
        lines[i] = '            self.canvas_etiq.create_text(x_base + 8, info_y, text=f"E {i+1} | OS: {viga}/{pos}", font=("Arial", int(12*zf), "bold"), fill="#000000", anchor="nw")\n'
        lines.insert(i+1, '            info_y2 = y_cursor + 28\n')
        lines.insert(i+2, '            self.canvas_etiq.create_text(x_base + 8, info_y2, text=f"Ø {bitola:.1f}mm | Q: {qtde} | C: {comp:.2f}m", font=("Arial", int(11*zf), "bold"), fill="#000000", anchor="nw")\n')
        lines.insert(i+3, '            \n')
        print(f"✅ Linha {i+1} atualizada!")
        break

# Escrever arquivo de volta
with open(r'c:\EngenhariaPlanPro\vigas_app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Arquivo salvo com sucesso!")
