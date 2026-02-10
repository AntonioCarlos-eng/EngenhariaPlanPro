"""
PATCH_CORRECAO_PREVIEW.py
-------------------------
Adicione este método ao vigas_app.py logo após o método ultima_pagina()

INSTRUÇÕES:
1. Abra vigas_app.py
2. Procure por: def ultima_pagina(self):
3. Após esse método, adicione o método abaixo
4. Substitua todas as chamadas de desenhar_pagina_etiquetas_vigas_fase4() 
   por desenhar_preview_com_pngs_gerados()
"""

# ============================================================================
import os
from tkinter import messagebox
from PIL import Image, ImageTk
# ADICIONAR ESTE MÉTODO NO vigas_app.py (após ultima_pagina)
# ============================================================================

def desenhar_preview_com_pngs_gerados(self):
    """
    NOVO: Carrega e exibe os PNGs já gerados pelo GeradorEtiquetasDinamico
    Garante que PREVIEW = IMPRESSÃO (100% idêntico)
    
    Este método substitui desenhar_pagina_etiquetas_vigas_fase4() para
    garantir que o preview mostre exatamente o que será impresso.
    """
    print("\n[PREVIEW] Carregando PNGs gerados...")
    
    # Limpar canvas
    self.canvas_etiq.delete("all")
    self._barcode_images = []
    self._desenho_images = []
    
    # Verificar se há PNGs gerados
    if not hasattr(self, 'caminhos_etiquetas_geradas') or not self.caminhos_etiquetas_geradas:
        # Fallback: tentar localizar PNGs na pasta
        pasta_etiquetas = r"c:\EngenhariaPlanPro\etiquetas"
        print(f"[PREVIEW] Procurando PNGs em: {pasta_etiquetas}")
        
        if os.path.exists(pasta_etiquetas):
            pngs = sorted([os.path.join(pasta_etiquetas, f) 
                          for f in os.listdir(pasta_etiquetas) 
                          if f.startswith('ETIQUETA_') and f.endswith('.png')])
            self.caminhos_etiquetas_geradas = pngs
            print(f"[PREVIEW] Encontrados {len(pngs)} PNG(s)")
        else:
            print(f"[PREVIEW] Pasta não existe: {pasta_etiquetas}")
    
    if not self.caminhos_etiquetas_geradas:
        messagebox.showerror(
            "Erro - Etiquetas não geradas", 
            "Nenhuma etiqueta PNG foi gerada!\n\n"
            "Por favor, processe os arquivos DXF primeiro.\n"
            "O sistema irá gerar as etiquetas automaticamente."
        )
        return
    
    # Calcular índices da página atual
    inicio = self.pagina_atual * self.etiquetas_por_pagina
    fim = min(inicio + self.etiquetas_por_pagina, len(self.caminhos_etiquetas_geradas))
    
    print(f"[PREVIEW] Página {self.pagina_atual + 1}: exibindo etiquetas {inicio+1} a {fim}")
    
    # Dimensões e posicionamento
    canvas_w = int(self.canvas_etiq.cget('width'))
    margem = 20
    y_cursor = margem
    
    # Carregar e exibir cada PNG
    for idx in range(inicio, fim):
        caminho_png = self.caminhos_etiquetas_geradas[idx]
        
        try:
            # Carregar PNG gerado
            img = Image.open(caminho_png)
            print(f"[PREVIEW] Carregando: {os.path.basename(caminho_png)} ({img.size[0]}x{img.size[1]}px)")
            
            # Redimensionar para caber no canvas (mantendo proporção)
            max_width = canvas_w - (2 * margem)
            max_height = 600  # Altura máxima por etiqueta
            
            # Calcular escala mantendo proporção
            scale_w = max_width / img.size[0] if img.size[0] > max_width else 1.0
            scale_h = max_height / img.size[1] if img.size[1] > max_height else 1.0
            scale = min(scale_w, scale_h)
            
            if scale < 1.0:
                new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"[PREVIEW] Redimensionado para: {new_size[0]}x{new_size[1]}px")
            
            # Converter para PhotoImage
            photo = ImageTk.PhotoImage(img)
            self._desenho_images.append(photo)
            
            # Centralizar horizontalmente
            x_center = canvas_w // 2
            
            # Desenhar no canvas
            self.canvas_etiq.create_image(x_center, y_cursor, image=photo, anchor="n")
            
            # Adicionar label com número da etiqueta
            self.canvas_etiq.create_text(
                x_center, y_cursor + img.height + 10,
                text=f"Etiqueta #{idx + 1} de {len(self.caminhos_etiquetas_geradas)}",
                font=("Arial", 9, "bold"),
                fill="#ff6f00"
            )
            
            # Adicionar nome do arquivo (para debug)
            self.canvas_etiq.create_text(
                x_center, y_cursor + img.height + 25,
                text=os.path.basename(caminho_png),
                font=("Arial", 7),
                fill="gray"
            )
            
            # Atualizar cursor
            y_cursor += img.height + 50
            
        except Exception as e:
            print(f"[ERRO] Falha ao carregar PNG {caminho_png}: {e}")
            import traceback
            traceback.print_exc()
            
            # Desenhar placeholder de erro
            self.canvas_etiq.create_rectangle(
                margem, y_cursor, canvas_w - margem, y_cursor + 200,
                outline="red", width=2, fill="#ffe6e6"
            )
            self.canvas_etiq.create_text(
                canvas_w // 2, y_cursor + 100,
                text=f"❌ ERRO ao carregar\n{os.path.basename(caminho_png)}\n\n{str(e)}",
                font=("Arial", 10),
                fill="red",
                justify="center"
            )
            y_cursor += 220
    
    # Atualizar scroll region
    self.canvas_etiq.configure(scrollregion=(0, 0, canvas_w, y_cursor + margem))
    
    # Atualizar label de página
    if hasattr(self, 'label_pagina'):
        self.label_pagina.config(text=f"Página {self.pagina_atual + 1} de {self.total_paginas}")
    
    print(f"[PREVIEW] ✅ Preview atualizado com sucesso!\n")


# ============================================================================
# SUBSTITUIÇÕES NECESSÁRIAS
# ============================================================================

"""
Procure por TODAS as ocorrências de:
    self.desenhar_pagina_etiquetas_vigas_fase4()

E substitua por:
    self.desenhar_preview_com_pngs_gerados()

Locais encontrados (7 ocorrências):
1. Dentro de salvar_edicao() no diálogo de edição
2. Dentro de _editar_desenho_canvas()
3. No método primeira_pagina()
4. No método pagina_anterior()
5. No método proxima_pagina()
6. No método ultima_pagina()
7. No método inicial que abre o preview

EXEMPLO DE SUBSTITUIÇÃO:

ANTES:
    try:
        self.desenhar_pagina_etiquetas_vigas_fase4()
        self.atualizar_botoes_navegacao()
    except Exception as e:
        print(f"[ERRO] Falha ao desenhar etiquetas: {e}")

DEPOIS:
    try:
        self.desenhar_preview_com_pngs_gerados()
        self.atualizar_botoes_navegacao()
    except Exception as e:
        print(f"[ERRO] Falha ao desenhar etiquetas: {e}")
"""

# ============================================================================
# TESTE APÓS APLICAR O PATCH
# ============================================================================

"""
1. Abra o vigas_app.py
2. Processe um arquivo DXF
3. Clique em "Etiquetas"
4. Verifique que o preview mostra os PNGs gerados
5. Confirme que layout e desenhos estão corretos
6. Teste navegação entre páginas

Se tudo funcionar:
✅ Preview = Impressão (100% idêntico)
✅ Desenhos técnicos corretos
✅ Layout profissional

Se houver erro:
- Verifique se os PNGs foram gerados em c:\EngenhariaPlanPro\etiquetas
- Execute: python test_correcao_preview.py
- Verifique os logs no console
"""
