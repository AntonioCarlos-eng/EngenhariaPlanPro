"""
TESTE VISUAL - Demonstra os checkboxes funcionando
Abra este arquivo para ver as checkboxes aparecendo nas etiquetas
"""

import tkinter as tk
from tkinter import Canvas
import math

# Simular dados
dados_processados = [
    ('P1', 'A1', 12.5, 8, 50.0),
    ('P1', 'A2', 10.0, 6, 45.0),
    ('P1', 'A3', 8.0, 10, 40.0),
]

etiquetas_selecionadas = {i: True for i in range(len(dados_processados))}

# Criar janela
root = tk.Tk()
root.title("TESTE - Checkboxes nas Etiquetas")
root.geometry("900x600")

# Canvas
canvas = Canvas(root, bg="white", width=880, height=550)
canvas.pack(padx=10, pady=10)

# Dimensões (simuladas)
PX_MM = 4
MARGEM = 40
LARGURA_ETIQ = 400  # 100mm * 4
ALTURA_TOPO = 372   # 93mm * 4
ALTURA_MICRO = 76   # 19mm * 4
ESPACO_PICOTE = 8   # 2mm * 4

altura_etiqueta = ALTURA_TOPO + (ESPACO_PICOTE // 2) + 3 * (ALTURA_MICRO + ESPACO_PICOTE)

canvas_w = 880
x_base = (canvas_w - (LARGURA_ETIQ + 2 * MARGEM)) // 2 + MARGEM

y_cursor = MARGEM

for i in range(len(dados_processados)):
    # Desenhar etiqueta (apenas moldura e cores)
    viga, pos, bitola, qtde, comp = dados_processados[i]
    
    # Moldura da etiqueta (simulada)
    canvas.create_rectangle(x_base, y_cursor, x_base + LARGURA_ETIQ, 
                           y_cursor + altura_etiqueta,
                           outline="#cccccc", width=2, fill="#f0f0f0")
    
    # Texto de exemplo
    canvas.create_text(x_base + LARGURA_ETIQ//2, y_cursor + ALTURA_TOPO//2,
                      text=f"{viga}/{pos} - {bitola}mm x {qtde} unidades",
                      font=("Arial", 12), fill="#333333")
    
    # ===== CHECKBOX (DESENHADO POR ÚLTIMO, FICA NA FRENTE) =====
    checkbox_size = 28
    x_checkbox = x_base + 8
    y_checkbox = y_cursor + 8
    
    # Fundo branco
    canvas.create_rectangle(x_checkbox-2, y_checkbox-2, x_checkbox+checkbox_size+2, y_checkbox+checkbox_size+2,
                           fill="white", outline="white", width=1)
    
    # Checkbox
    if etiquetas_selecionadas.get(i, True):
        # Marcado - verde
        canvas.create_rectangle(x_checkbox, y_checkbox, x_checkbox+checkbox_size, y_checkbox+checkbox_size,
                              fill="#27ae60", outline="#1a5c3a", width=3)
        # Checkmark
        canvas.create_line(x_checkbox+6, y_checkbox+14, x_checkbox+11, y_checkbox+20, 
                         x_checkbox+22, y_checkbox+5, fill="white", width=3)
        # Texto
        canvas.create_text(x_checkbox+checkbox_size+8, y_checkbox+checkbox_size//2, 
                          text="Selecionado", font=("Arial", 8, "bold"), fill="#27ae60", anchor="w")
    else:
        # Desmarcado - branco
        canvas.create_rectangle(x_checkbox, y_checkbox, x_checkbox+checkbox_size, y_checkbox+checkbox_size,
                              outline="#333333", width=2, fill="white")
        # Texto
        canvas.create_text(x_checkbox+checkbox_size+8, y_checkbox+checkbox_size//2, 
                          text="Clique para selecionar", font=("Arial", 7), fill="#999999", anchor="w")
    
    y_cursor += altura_etiqueta + (ESPACO_PICOTE * 3)

# Instruções
label = tk.Label(root, text="✓ Checkboxes aparecem no canto superior esquerdo\n" +
                           "✓ Verde = Selecionado | Branco = Desmarcado\n" +
                           "✓ Clique para selecionar/desselecionar",
                font=("Arial", 10), fg="#27ae60", bg="white", padx=10, pady=10)
label.pack(side=tk.BOTTOM, fill=tk.X)

# Bind click no checkbox
def toggle_checkbox(event):
    # Calcular qual etiqueta foi clicada
    y_cursor = MARGEM
    for i in range(len(dados_processados)):
        checkbox_size = 28
        x_checkbox = x_base + 8
        y_checkbox = y_cursor + 8
        
        if (x_checkbox-5 <= event.x <= x_checkbox+checkbox_size+5 and
            y_checkbox-5 <= event.y <= y_checkbox+checkbox_size+5):
            # Toggle
            etiquetas_selecionadas = {j: False for j in range(len(dados_processados))}
            etiquetas_selecionadas[i] = True
            print(f"[CLIQUE] Checkbox {i} selecionada!")
            print(f"Estado: {etiquetas_selecionadas}")
            # Redesenhar
            redraw()
            break
        
        y_cursor += altura_etiqueta + (ESPACO_PICOTE * 3)

def redraw():
    canvas.delete("all")
    y_cursor_local = MARGEM
    for i in range(len(dados_processados)):
        viga, pos, bitola, qtde, comp = dados_processados[i]
        
        canvas.create_rectangle(x_base, y_cursor_local, x_base + LARGURA_ETIQ, 
                               y_cursor_local + altura_etiqueta,
                               outline="#cccccc", width=2, fill="#f0f0f0")
        
        canvas.create_text(x_base + LARGURA_ETIQ//2, y_cursor_local + ALTURA_TOPO//2,
                          text=f"{viga}/{pos} - {bitola}mm x {qtde} unidades",
                          font=("Arial", 12), fill="#333333")
        
        checkbox_size = 28
        x_checkbox = x_base + 8
        y_checkbox = y_cursor_local + 8
        
        canvas.create_rectangle(x_checkbox-2, y_checkbox-2, x_checkbox+checkbox_size+2, y_checkbox+checkbox_size+2,
                               fill="white", outline="white", width=1)
        
        if etiquetas_selecionadas.get(i, True):
            canvas.create_rectangle(x_checkbox, y_checkbox, x_checkbox+checkbox_size, y_checkbox+checkbox_size,
                                  fill="#27ae60", outline="#1a5c3a", width=3)
            canvas.create_line(x_checkbox+6, y_checkbox+14, x_checkbox+11, y_checkbox+20, 
                             x_checkbox+22, y_checkbox+5, fill="white", width=3)
            canvas.create_text(x_checkbox+checkbox_size+8, y_checkbox+checkbox_size//2, 
                              text="Selecionado", font=("Arial", 8, "bold"), fill="#27ae60", anchor="w")
        else:
            canvas.create_rectangle(x_checkbox, y_checkbox, x_checkbox+checkbox_size, y_checkbox+checkbox_size,
                                  outline="#333333", width=2, fill="white")
            canvas.create_text(x_checkbox+checkbox_size+8, y_checkbox+checkbox_size//2, 
                              text="Clique para selecionar", font=("Arial", 7), fill="#999999", anchor="w")
        
        y_cursor_local += altura_etiqueta + (ESPACO_PICOTE * 3)

canvas.bind("<Button-1>", toggle_checkbox)

root.mainloop()
