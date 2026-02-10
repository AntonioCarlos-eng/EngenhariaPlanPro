"""Script para adicionar exibição do corpo na dobra_dupla"""

with open('vigas_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Atualizar canvas para mostrar corpo na dobra_dupla
old_dupla_canvas = '''        elif forma == 'dobra_dupla':
            # Duas dobras: uma em cada extremidade (formato tipo "U" com perninhas)
            x_esq = x + int(ctx_w * 0.15)
            x_dir = x + int(ctx_w * 0.85)
            y_base = y + int(ctx_h * 0.60)
            y_top = y + int(ctx_h * 0.25)

            # Barra horizontal principal
            canvas.create_line(x_esq, y_base, x_dir, y_base, width=esp, fill=cor)
            # Pernas (dobras) nas extremidades
            canvas.create_line(x_esq, y_base, x_esq, y_top, width=esp, fill=cor)
            canvas.create_line(x_dir, y_base, x_dir, y_top, width=esp, fill=cor)

            # Medidas: cada perna + corpo horizontal
            if isinstance(medida_dobra, (list, tuple)) and len(medida_dobra) >= 2:
                m_esq, m_dir = medida_dobra[0], medida_dobra[1]
                canvas.create_text(x_esq - 8, (y_base + y_top)//2, text=f"{m_esq:.0f}cm", font=("Arial", 28, "bold"), fill="#000000", anchor="e")
                canvas.create_text(x_dir + 8, (y_base + y_top)//2, text=f"{m_dir:.0f}cm", font=("Arial", 28, "bold"), fill="#000000", anchor="w")
                # Adicionar medida do corpo (se tiver lado1 nas medidas customizadas)
                # O corpo está em lado1, vamos buscar do contexto
                # Para exibir, precisamos ter acesso ao chave ou passar como parâmetro adicional
                # Por ora, vamos só marcar visualmente no meio'''

new_dupla_canvas = '''        elif forma == 'dobra_dupla':
            # Duas dobras: uma em cada extremidade (formato tipo "U" com perninhas)
            x_esq = x + int(ctx_w * 0.15)
            x_dir = x + int(ctx_w * 0.85)
            y_base = y + int(ctx_h * 0.60)
            y_top = y + int(ctx_h * 0.25)

            # Barra horizontal principal
            canvas.create_line(x_esq, y_base, x_dir, y_base, width=esp, fill=cor)
            # Pernas (dobras) nas extremidades
            canvas.create_line(x_esq, y_base, x_esq, y_top, width=esp, fill=cor)
            canvas.create_line(x_dir, y_base, x_dir, y_top, width=esp, fill=cor)

            # Medidas: cada perna + corpo horizontal
            if isinstance(medida_dobra, (list, tuple)):
                if len(medida_dobra) >= 3:
                    m_esq, m_dir, m_corpo = medida_dobra[0], medida_dobra[1], medida_dobra[2]
                    canvas.create_text(x_esq - 8, (y_base + y_top)//2, text=f"{m_esq:.0f}cm", font=("Arial", 28, "bold"), fill="#000000", anchor="e")
                    canvas.create_text(x_dir + 8, (y_base + y_top)//2, text=f"{m_dir:.0f}cm", font=("Arial", 28, "bold"), fill="#000000", anchor="w")
                    if m_corpo > 0:
                        canvas.create_text((x_esq + x_dir)//2, y_base + 8, text=f"{m_corpo:.0f}cm", font=("Arial", 28, "bold"), fill="#000000", anchor="n")
                elif len(medida_dobra) >= 2:
                    m_esq, m_dir = medida_dobra[0], medida_dobra[1]
                    canvas.create_text(x_esq - 8, (y_base + y_top)//2, text=f"{m_esq:.0f}cm", font=("Arial", 28, "bold"), fill="#000000", anchor="e")
                    canvas.create_text(x_dir + 8, (y_base + y_top)//2, text=f"{m_dir:.0f}cm", font=("Arial", 28, "bold"), fill="#000000", anchor="w")'''

content = content.replace(old_dupla_canvas, new_dupla_canvas)

# Atualizar PIL para mostrar corpo na dobra_dupla
old_dupla_pil = '''        elif forma == 'dobra_dupla':
            x_esq = x + int(w * 0.15)
            x_dir = x + int(w * 0.85)
            y_base = y + int(h * 0.60)
            y_top = y + int(h * 0.25)
            draw.line([x_esq, y_base, x_dir, y_base], fill=cor, width=esp)
            draw.line([x_esq, y_base, x_esq, y_top], fill=cor, width=esp)
            draw.line([x_dir, y_base, x_dir, y_top], fill=cor, width=esp)
            if isinstance(medida_dobra, (list, tuple)) and len(medida_dobra) >= 2:
                m_esq, m_dir = medida_dobra[0], medida_dobra[1]
                draw.text((x_esq - 8, (y_base + y_top)//2), f"{m_esq:.0f}cm", fill=(0,0,0), font=font, anchor='rm')
                draw.text((x_dir + 8, (y_base + y_top)//2), f"{m_dir:.0f}cm", fill=(0,0,0), font=font, anchor='lm')'''

new_dupla_pil = '''        elif forma == 'dobra_dupla':
            x_esq = x + int(w * 0.15)
            x_dir = x + int(w * 0.85)
            y_base = y + int(h * 0.60)
            y_top = y + int(h * 0.25)
            draw.line([x_esq, y_base, x_dir, y_base], fill=cor, width=esp)
            draw.line([x_esq, y_base, x_esq, y_top], fill=cor, width=esp)
            draw.line([x_dir, y_base, x_dir, y_top], fill=cor, width=esp)
            if isinstance(medida_dobra, (list, tuple)):
                if len(medida_dobra) >= 3:
                    m_esq, m_dir, m_corpo = medida_dobra[0], medida_dobra[1], medida_dobra[2]
                    draw.text((x_esq - 8, (y_base + y_top)//2), f"{m_esq:.0f}cm", fill=(0,0,0), font=font, anchor='rm')
                    draw.text((x_dir + 8, (y_base + y_top)//2), f"{m_dir:.0f}cm", fill=(0,0,0), font=font, anchor='lm')
                    if m_corpo > 0:
                        draw.text(((x_esq + x_dir)//2, y_base + 8), f"{m_corpo:.0f}cm", fill=(0,0,0), font=font, anchor='mt')
                elif len(medida_dobra) >= 2:
                    m_esq, m_dir = medida_dobra[0], medida_dobra[1]
                    draw.text((x_esq - 8, (y_base + y_top)//2), f"{m_esq:.0f}cm", fill=(0,0,0), font=font, anchor='rm')
                    draw.text((x_dir + 8, (y_base + y_top)//2), f"{m_dir:.0f}cm", fill=(0,0,0), font=font, anchor='lm')'''

content = content.replace(old_dupla_pil, new_dupla_pil)

with open('vigas_app.py', 'w', encoding='utf-8') as f:
    f.write(content)
    
print("✓ Exibição do corpo na dobra_dupla adicionada!")
print("  - Canvas e PIL agora mostram as 2 dobras + corpo horizontal")
