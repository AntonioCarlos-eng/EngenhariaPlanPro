# 🎯 PROBLEMA REAL IDENTIFICADO

## 📸 Análise das Imagens

### Imagem 1: PREVIEW (CORRETO) ✅
- Título: "PREVIEW DE 46 ETIQUETA(S) - Como vai sair na impressora"
- Mostra PNG gerado pelo `etiquetas_generator.py`
- Desenho técnico COMPLETO e detalhado
- Layout profissional
- **ESTE ESTÁ CORRETO!**

### Imagem 2: EDITOR (ERRADO) ❌
- Título: "EDITOR DE ETIQUETAS - Edite, Selecione e Imprima"
- Redesenha no canvas usando `desenhar_etiquetas_com_selecao()`
- Desenho INCOMPLETO (só uma linha preta)
- Tabela cortada
- **ESTE ESTÁ ERRADO!**

## 🔍 CAUSA RAIZ

Você tem **2 janelas diferentes**:

1. **Preview Simples** (`imprimir_etiquetas()`) - ✅ JÁ ESTÁ CORRETO (mostra PNGs)
2. **Editor com Checkboxes** (`desenhar_etiquetas_com_selecao()`) - ❌ ESTÁ ERRADO (redesenha)

O **EDITOR** é o problema! Ele usa `desenhar_etiquetas_com_selecao()` que:
- Redesenha tudo no canvas
- Não carrega os PNGs gerados
- Desenho técnico fica incompleto

## ✅ SOLUÇÃO

O EDITOR também deve **CARREGAR os PNGs** ao invés de redesenhar!

### Modificar `desenhar_etiquetas_com_selecao()` no vigas_app.py

Procure pelo método `desenhar_etiquetas_com_selecao(self):` e substitua TODO o conteúdo por:

```python
def desenhar_etiquetas_com_selecao(self):
    """
    CORRIGIDO: Carrega PNGs gerados + adiciona checkboxes para seleção
    """
    print("\n[EDITOR] Carregando PNGs gerados com checkboxes...")
    
    # Salvar posição do scroll
    try:
        yview_prev = self.canvas_etiq.yview()
    except Exception:
        yview_prev = None
    
    # Limpar canvas
    self.canvas_etiq.delete("all")
    self._barcode_images = []
    self._desenho_images = []
    self._checkbox_positions = {}
    
    # Verificar se há PNGs gerados
    if not hasattr(self, 'caminhos_etiquetas_geradas') or not self.caminhos_etiquetas_geradas:
        pasta_etiquetas = r"c:\EngenhariaPlanPro\etiquetas"
        if os.path.exists(pasta_etiquetas):
            pngs = sorted([os.path.join(pasta_etiquetas, f) 
                          for f in os.listdir(pasta_etiquetas) 
                          if f.startswith('ETIQUETA_') and f.endswith('.png')])
            self.caminhos_etiquetas_geradas = pngs
    
    if not self.caminhos_etiquetas_geradas:
        messagebox.showerror("Erro", "Nenhuma etiqueta PNG gerada!\n\nProcesse primeiro.")
        return
    
    # Calcular índices da página
    inicio = self.pagina_atual * self.etiquetas_por_pagina
    fim = min(inicio + self.etiquetas_por_pagina, len(self.caminhos_etiquetas_geradas))
    
    # Dimensões
    canvas_w = int(self.canvas_etiq.cget('width'))
    margem = 20
    y_cursor = margem
    
    # Carregar e exibir cada PNG COM CHECKBOX
    for idx in range(inicio, fim):
        caminho_png = self.caminhos_etiquetas_geradas[idx]
        
        try:
            # Carregar PNG gerado
            img = Image.open(caminho_png)
            
            # Redimensionar para caber no canvas
            max_width = canvas_w - (2 * margem) - 40  # Espaço para checkbox
            max_height = 600
            
            scale_w = max_width / img.size[0] if img.size[0] > max_width else 1.0
            scale_h = max_height / img.size[1] if img.size[1] > max_height else 1.0
            scale = min(scale_w, scale_h)
            
            if scale < 1.0:
                new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Converter para PhotoImage
            photo = ImageTk.PhotoImage(img)
            self._desenho_images.append(photo)
            
            # Posição da imagem (deixar espaço à esquerda para checkbox)
            x_img = margem + 40
            
            # Desenhar PNG no canvas
            self.canvas_etiq.create_image(x_img, y_cursor, image=photo, anchor="nw")
            
            # ===== CHECKBOX NO CANTO SUPERIOR ESQUERDO =====
            checkbox_size = 28
            x_checkbox = margem + 8
            y_checkbox = y_cursor + 8
            
            # Armazenar posição do checkbox
            self._checkbox_positions[idx] = {
                'x1': x_checkbox - 5, 'y1': y_checkbox - 5,
                'x2': x_checkbox + checkbox_size + 5, 'y2': y_checkbox + checkbox_size + 5
            }
            
            # Desenhar fundo branco para checkbox
            self.canvas_etiq.create_rectangle(
                x_checkbox-2, y_checkbox-2, 
                x_checkbox+checkbox_size+2, y_checkbox+checkbox_size+2,
                fill="white", outline="white", width=1
            )
            
            # Desenhar checkbox
            if self.etiquetas_selecionadas.get(idx, True):
                # Marcado - verde com checkmark
                self.canvas_etiq.create_rectangle(
                    x_checkbox, y_checkbox, 
                    x_checkbox+checkbox_size, y_checkbox+checkbox_size,
                    fill="#27ae60", outline="#1a5c3a", width=3
                )
                # Checkmark
                self.canvas_etiq.create_line(
                    x_checkbox+6, y_checkbox+14, 
                    x_checkbox+11, y_checkbox+20, 
                    x_checkbox+22, y_checkbox+5, 
                    fill="white", width=3, capstyle="round", joinstyle="round"
                )
            else:
                # Desmarcado
                self.canvas_etiq.create_rectangle(
                    x_checkbox, y_checkbox, 
                    x_checkbox+checkbox_size, y_checkbox+checkbox_size,
                    outline="#333333", width=2, fill="white"
                )
            
            # Label
            self.canvas_etiq.create_text(
                x_img + img.width // 2, y_cursor + img.height + 10,
                text=f"Etiqueta #{idx + 1}",
                font=("Arial", 9, "bold"),
                fill="#ff6f00"
            )
            
            # Atualizar cursor
            y_cursor += img.height + 50
            
        except Exception as e:
            print(f"[ERRO] {caminho_png}: {e}")
            # Placeholder de erro
            self.canvas_etiq.create_rectangle(
                margem, y_cursor, canvas_w - margem, y_cursor + 200,
                outline="red", width=2, fill="#ffe6e6"
            )
            self.canvas_etiq.create_text(
                canvas_w // 2, y_cursor + 100,
                text=f"❌ ERRO ao carregar",
                font=("Arial", 10),
                fill="red"
            )
            y_cursor += 220
    
    # Atualizar scroll
    self.canvas_etiq.configure(scrollregion=(0, 0, canvas_w, y_cursor + margem))
    
    # Restaurar posição do scroll
    if yview_prev:
        try:
            self.canvas_etiq.yview_moveto(yview_prev[0])
        except Exception:
            pass
    
    # Atualizar label
    if hasattr(self, 'label_pagina'):
        self.label_pagina.config(text=f"Página {self.pagina_atual + 1} de {self.total_paginas}")
    
    print(f"[EDITOR] ✅ Editor atualizado com PNGs!\n")
```

## 🎯 RESULTADO ESPERADO

Após a correção, o **EDITOR** vai:
- ✅ Carregar os PNGs gerados (igual ao preview simples)
- ✅ Mostrar desenhos técnicos COMPLETOS
- ✅ Manter os checkboxes para seleção
- ✅ Layout profissional idêntico ao gerador

## 📝 RESUMO

**ANTES**:
- Preview Simples ✅ (mostra PNGs)
- Editor ❌ (redesenha errado)

**DEPOIS**:
- Preview Simples ✅ (mostra PNGs)
- Editor ✅ (mostra PNGs + checkboxes)

Ambos vão mostrar EXATAMENTE o que será impresso!
