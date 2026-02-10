
# Adicionar após linha 3626 no vigas_app.py:
# As seguintes linhas devem substituir:
#             self.canvas_etiq.create_text(x_base + 8, info_y, text=f"E {i+1}", font=("Arial", int(9*zf), "bold"), fill="#333333", anchor="nw")
#
# Por:
#             self.canvas_etiq.create_text(x_base + 8, info_y, text=f"E {i+1} | OS: {viga}/{pos}", font=("Arial", int(12*zf), "bold"), fill="#000000", anchor="nw")
#             info_y2 = y_cursor + 28
#             self.canvas_etiq.create_text(x_base + 8, info_y2, text=f"Ø {bitola:.1f}mm | Q: {qtde} | C: {comp:.2f}m", font=("Arial", int(11*zf), "bold"), fill="#000000", anchor="nw")

# Executar este comando:
import sys
sys.path.insert(0, r'c:\EngenhariaPlanPro')

with open(r'c:\EngenhariaPlanPro\vigas_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_text = 'self.canvas_etiq.create_text(x_base + 8, info_y, text=f"E {i+1}", font=("Arial", int(9*zf), "bold"), fill="#333333", anchor="nw")'

new_text = '''self.canvas_etiq.create_text(x_base + 8, info_y, text=f"E {i+1} | OS: {viga}/{pos}", font=("Arial", int(12*zf), "bold"), fill="#000000", anchor="nw")
            info_y2 = y_cursor + 28
            self.canvas_etiq.create_text(x_base + 8, info_y2, text=f"Ø {bitola:.1f}mm | Q: {qtde} | C: {comp:.2f}m", font=("Arial", int(11*zf), "bold"), fill="#000000", anchor="nw")'''

if old_text in content:
    content = content.replace(old_text, new_text)
    with open(r'c:\EngenhariaPlanPro\vigas_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Preview corrigido com sucesso!")
else:
    print("❌ Texto não encontrado")
    print("Procurando por fragmento...")
    if 'self.canvas_etiq.create_text(x_base + 8, info_y' in content:
        print("✓ Encontrado trecho similar")
