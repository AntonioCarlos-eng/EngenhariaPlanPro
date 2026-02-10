"""Script para corrigir fonte e desenho PNG"""

with open('vigas_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Reduzir fonte de 55 para 35
content = content.replace('font_medidas = ImageFont.truetype("arialbd.ttf", 55)', 
                         'font_medidas = ImageFont.truetype("arialbd.ttf", 35)')

# 2. Substituir a função _desenhar_forma_png completamente
old_func = '''    def _desenhar_forma_png(self, draw, forma, medidas, largura, y_start, altura, font_medidas=None):
        """Desenha a forma da armadura no PNG"""
        x_center = largura // 2
        y_center = y_start + altura // 2
        
        if forma in ["reta", "Reta"]:
            # Linha horizontal simples - AUMENTADA
            draw.line([(x_center - 400, y_center), (x_center + 400, y_center)], fill='black', width=16)
            
        elif forma in ["dobra", "Dobra", "Dobra Única", "dobra_unica"]:
            # L invertido - AUMENTADO
            medida = medidas.get('medida_dobra', 30)
            draw.line([(x_center - 300, y_center + 120), (x_center - 300, y_center - 120)], fill='black', width=16)
            draw.line([(x_center - 300, y_center - 120), (x_center + 300, y_center - 120)], fill='black', width=16)
            draw.text((x_center - 400, y_center), f"{medida}cm", fill='black', font=font_medidas, anchor='mm')
            
        elif forma in ["dobra_dupla", "Dobra Dupla"]:
            # U invertido - AUMENTADO
            medida1 = medidas.get('medida_dobra', 25)
            medida2 = medidas.get('medida_dobra_2', 25)
            draw.line([(x_center - 300, y_center + 120), (x_center - 300, y_center - 120)], fill='black', width=16)
            draw.line([(x_center - 300, y_center - 120), (x_center + 300, y_center - 120)], fill='black', width=16)
            draw.line([(x_center + 300, y_center - 120), (x_center + 300, y_center + 120)], fill='black', width=16)
            draw.text((x_center - 400, y_center), f"{medida1}cm", fill='black', font=font_medidas, anchor='mm')
            draw.text((x_center + 400, y_center), f"{medida2}cm", fill='black', font=font_medidas, anchor='mm')
            
        elif forma in ["estribo", "estribo_quadrado", "Estribo", "Estribo Quadrado", "Estribo Retângulo"]:
            # Retângulo - AUMENTADO
            lado1 = medidas.get('lado1', 20)
            lado2 = medidas.get('lado2', 30)
            w = min(400, lado1 * 8)  # DOBRADO
            h = min(300, lado2 * 8)  # DOBRADO
            draw.rectangle([(x_center - w//2, y_center - h//2), (x_center + w//2, y_center + h//2)], 
                          outline='black', width=16)
            draw.text((x_center, y_center - h//2 - 60), f"{lado1}cm", fill='black', font=font_medidas, anchor='mm')
            draw.text((x_center + w//2 + 100, y_center), f"{lado2}cm", fill='black', font=font_medidas, anchor='lm')
            
        elif forma in ["estribo_redondo", "Estribo Redondo"]:
            # Círculo - AUMENTADO
            raio = medidas.get('raio', 15)
            r_px = min(240, raio * 12)  # DOBRADO
            draw.ellipse([(x_center - r_px, y_center - r_px), (x_center + r_px, y_center + r_px)], 
                        outline='black', width=16)
            draw.text((x_center, y_center + r_px + 70), f"R={raio}cm", fill='black', font=font_medidas, anchor='mm')'''

new_func = '''    def _desenhar_forma_png(self, draw, forma, medidas, largura, y_start, altura, font_medidas=None):
        """Desenha a forma da armadura no PNG - COMPATÍVEL COM TUPLAS"""
        x_center = largura // 2
        y_center = y_start + altura // 2
        
        if forma in ["reta", "Reta"]:
            draw.line([(x_center - 400, y_center), (x_center + 400, y_center)], fill='black', width=16)
            
        elif forma in ["dobra", "Dobra", "Dobra Única", "dobra_unica"]:
            # Dobra simples: L invertido com dobra (vertical) e corpo (horizontal)
            m_dobra = medidas.get('medida_dobra', 30)
            m_corpo = medidas.get('medida_dobra_2', 0)
            
            x1, x2 = x_center - 300, x_center + 300
            y1, yb = y_center + 80, y_center - 80
            
            draw.line([(x1, y1), (x2, y1)], fill='black', width=16)  # Horizontal (corpo)
            draw.line([(x2, y1), (x2, yb)], fill='black', width=16)  # Vertical (dobra)
            
            # Medidas
            if m_dobra > 0:
                draw.text((x2 + 60, (y1 + yb)//2), f"{m_dobra:.0f}cm", fill='black', font=font_medidas, anchor='lm')
            if m_corpo > 0:
                draw.text(((x1 + x2)//2, y1 + 50), f"{m_corpo:.0f}cm", fill='black', font=font_medidas, anchor='mt')
            
        elif forma in ["dobra_dupla", "Dobra Dupla"]:
            # Dobra dupla: U invertido com 2 dobras (verticais) e corpo (horizontal)
            m_dobra1 = medidas.get('medida_dobra', 25)
            m_dobra2 = medidas.get('medida_dobra_2', 25)
            m_corpo = medidas.get('lado1', 0)
            
            x_esq, x_dir = x_center - 300, x_center + 300
            y_base, y_top = y_center + 80, y_center - 80
            
            draw.line([(x_esq, y_base), (x_dir, y_base)], fill='black', width=16)  # Horizontal (corpo)
            draw.line([(x_esq, y_base), (x_esq, y_top)], fill='black', width=16)   # Vertical esq
            draw.line([(x_dir, y_base), (x_dir, y_top)], fill='black', width=16)   # Vertical dir
            
            # Medidas
            if m_dobra1 > 0:
                draw.text((x_esq - 60, (y_base + y_top)//2), f"{m_dobra1:.0f}cm", fill='black', font=font_medidas, anchor='rm')
            if m_dobra2 > 0:
                draw.text((x_dir + 60, (y_base + y_top)//2), f"{m_dobra2:.0f}cm", fill='black', font=font_medidas, anchor='lm')
            if m_corpo > 0:
                draw.text(((x_esq + x_dir)//2, y_base + 50), f"{m_corpo:.0f}cm", fill='black', font=font_medidas, anchor='mt')
            
        elif forma in ["gancho", "Gancho"]:
            # Gancho: formato Z com 3 medidas
            lado1 = medidas.get('lado1', 20)  # Dobra A
            lado2 = medidas.get('lado2', 20)  # Dobra B
            lado3 = medidas.get('lado3', 0)   # Corpo
            
            x1, x2 = x_center - 280, x_center + 280
            y1, y2, yb = y_center + 80, y_center + 80, y_center - 40
            
            draw.line([(x1, y1), (x1, yb)], fill='black', width=16)
            draw.line([(x1, yb), (x2, yb)], fill='black', width=16)
            draw.line([(x2, yb), (x2, y2)], fill='black', width=16)
            
            if lado1 > 0:
                draw.text((x1 - 60, (y1 + yb)//2), f"{lado1:.0f}cm", fill='black', font=font_medidas, anchor='rm')
            if lado2 > 0:
                draw.text((x2 + 60, (y2 + yb)//2), f"{lado2:.0f}cm", fill='black', font=font_medidas, anchor='lm')
            if lado3 > 0:
                draw.text(((x1 + x2)//2, yb - 50), f"{lado3:.0f}cm", fill='black', font=font_medidas, anchor='mb')
            
        elif forma in ["estribo", "estribo_quadrado", "Estribo", "Estribo Quadrado", "Estribo Retângulo"]:
            lado1 = medidas.get('lado1', 20)
            lado2 = medidas.get('lado2', 30)
            w = min(400, lado1 * 8)
            h = min(300, lado2 * 8)
            draw.rectangle([(x_center - w//2, y_center - h//2), (x_center + w//2, y_center + h//2)], 
                          outline='black', width=16)
            draw.text((x_center, y_center - h//2 - 50), f"{lado1:.0f}cm", fill='black', font=font_medidas, anchor='mm')
            draw.text((x_center + w//2 + 80, y_center), f"{lado2:.0f}cm", fill='black', font=font_medidas, anchor='lm')
            
        elif forma in ["estribo_redondo", "Estribo Redondo"]:
            raio = medidas.get('raio', 15)
            r_px = min(240, raio * 12)
            draw.ellipse([(x_center - r_px, y_center - r_px), (x_center + r_px, y_center + r_px)], 
                        outline='black', width=16)
            draw.text((x_center, y_center + r_px + 60), f"R={raio:.0f}cm", fill='black', font=font_medidas, anchor='mm')'''

content = content.replace(old_func, new_func)

with open('vigas_app.py', 'w', encoding='utf-8') as f:
    f.write(content)
    
print("✓ PNG corrigido!")
print("  - Fonte reduzida para 35")
print("  - Dobra/dobra_dupla/gancho agora mostram corpo no PNG")
