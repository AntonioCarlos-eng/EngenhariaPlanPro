#!/usr/bin/env python
# -*- coding: utf-8 -*-

content = open('vigas_app.py', 'r', encoding='utf-8').read()

old = '''            # Informações de identificação na parte superior (E numero da etiqueta)
            info_y = y_cursor + 8
            self.canvas_etiq.create_text(x_base + 8, info_y, text=f"E {i+1}", font=("Arial", int(9*zf), "bold"), fill="#333333", anchor="nw")'''

new = '''            # Informações de identificação na parte superior (E numero da etiqueta + Viga/OS)
            info_y = y_cursor + 8
            self.canvas_etiq.create_text(x_base + 8, info_y, text=f"E {i+1} | OS: {viga}/{pos}", font=("Arial", int(12*zf), "bold"), fill="#000000", anchor="nw")
            info_y2 = y_cursor + 28
            self.canvas_etiq.create_text(x_base + 8, info_y2, text=f"Ø {bitola:.1f}mm | Q: {qtde} | C: {comp:.2f}m", font=("Arial", int(11*zf), "bold"), fill="#000000", anchor="nw")'''

if old in content:
    content = content.replace(old, new)
    open('vigas_app.py', 'w', encoding='utf-8').write(content)
    print('Sucesso! Preview atualizado')
else:
    print('Texto nao encontrado')
