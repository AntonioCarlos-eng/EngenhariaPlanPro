# 🔧 CORREÇÃO: Preview de Etiquetas Idêntico ao Gerador

## 📋 PROBLEMA IDENTIFICADO

**Sintoma**: O layout e principalmente o DESENHO técnico saem DIFERENTES entre o gerador e o preview.

**Causa Raiz**: 
- O `etiquetas_generator.py` gera PNGs corretos (100x150mm com desenhos técnicos)
- O `vigas_app.py` REDESENHA tudo do zero no canvas
- Resultado: Preview ≠ Impressão

## ✅ SOLUÇÃO IMPLEMENTADA

### Estratégia: **PREVIEW = CARREGAR PNGs do GERADOR**

Ao invés de redesenhar, o preview agora:
1. ✅ Carrega os PNGs já gerados pelo `GeradorEtiquetasDinamico`
2. ✅ Exibe as imagens reais que serão impressas
3. ✅ Garante que Preview = Impressão (100% idênticos)

### Mudanças no `vigas_app.py`

#### 1. Novo método: `desenhar_preview_com_pngs_gerados()`

```python
def desenhar_preview_com_pngs_gerados(self):
    """
    NOVO MÉTODO: Carrega e exibe os PNGs já gerados pelo GeradorEtiquetasDinamico
    Garante que PREVIEW = IMPRESSÃO (100% idêntico)
    """
    # Limpar canvas
    self.canvas_etiq.delete("all")
    self._barcode_images = []
    self._desenho_images = []
    
    # Verificar se há PNGs gerados
    if not hasattr(self, 'caminhos_etiquetas_geradas') or not self.caminhos_etiquetas_geradas:
        # Fallback: tentar localizar PNGs na pasta
        pasta_etiquetas = r"c:\EngenhariaPlanPro\etiquetas"
        if os.path.exists(pasta_etiquetas):
            pngs = sorted([os.path.join(pasta_etiquetas, f) 
                          for f in os.listdir(pasta_etiquetas) 
                          if f.startswith('ETIQUETA_') and f.endswith('.png')])
            self.caminhos_etiquetas_geradas = pngs
    
    if not self.caminhos_etiquetas_geradas:
        messagebox.showerror("Erro", "Nenhuma etiqueta PNG foi gerada!\n\nProcesse os arquivos primeiro.")
        return
    
    # Calcular índices da página atual
    inicio = self.pagina_atual * self.etiquetas_por_pagina
    fim = min(inicio + self.etiquetas_por_pagina, len(self.caminhos_etiquetas_geradas))
    
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
            
            # Redimensionar para caber no canvas (mantendo proporção)
            max_width = canvas_w - (2 * margem)
            max_height = 600  # Altura máxima por etiqueta
            
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
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
                text=f"Etiqueta #{idx + 1} - {os.path.basename(caminho_png)}",
                font=("Arial", 8),
                fill="gray"
            )
            
            # Atualizar cursor
            y_cursor += img.height + 40
            
        except Exception as e:
            print(f"[ERRO] Falha ao carregar PNG {caminho_png}: {e}")
            # Desenhar placeholder de erro
            self.canvas_etiq.create_rectangle(
                margem, y_cursor, canvas_w - margem, y_cursor + 200,
                outline="red", width=2
            )
            self.canvas_etiq.create_text(
                canvas_w // 2, y_cursor + 100,
                text=f"❌ ERRO ao carregar\n{os.path.basename(caminho_png)}",
                font=("Arial", 10),
                fill="red"
            )
            y_cursor += 220
    
    # Atualizar scroll region
    self.canvas_etiq.configure(scrollregion=(0, 0, canvas_w, y_cursor + margem))
    
    # Atualizar label de página
    if hasattr(self, 'label_pagina'):
        self.label_pagina.config(text=f"Página {self.pagina_atual + 1} de {self.total_paginas}")
```

#### 2. Modificar `imprimir_etiquetas()` para usar novo método

```python
def imprimir_etiquetas(self):
    """Abre janela de preview com PNGs gerados"""
    if not self.dados_processados:
        messagebox.showwarning("Atenção", "Processe os arquivos primeiro!")
        return
    
    # Verificar se PNGs foram gerados
    if not hasattr(self, 'caminhos_etiquetas_geradas') or not self.caminhos_etiquetas_geradas:
        messagebox.showinfo(
            "Gerando Etiquetas",
            "As etiquetas serão geradas agora.\n\nAguarde..."
        )
        # Gerar PNGs se ainda não foram gerados
        # (código de geração aqui)
    
    # Criar janela de preview
    # ... (código da janela)
    
    # USAR NOVO MÉTODO ao invés do antigo
    self.desenhar_preview_com_pngs_gerados()  # ← MUDANÇA AQUI
```

## 🎯 BENEFÍCIOS

1. ✅ **Preview = Impressão** (100% idêntico)
2. ✅ **Mais rápido** (não redesenha, só carrega imagens)
3. ✅ **Sem bugs de sincronização** (usa mesma fonte)
4. ✅ **Desenhos técnicos corretos** (do gerador)
5. ✅ **Layout profissional** (do gerador)

## 📝 PRÓXIMOS PASSOS

1. Implementar o novo método no `vigas_app.py`
2. Testar com arquivos DXF reais
3. Validar que preview mostra exatamente o que será impresso

## 🔍 VALIDAÇÃO

Para confirmar que funcionou:
```python
# No preview, verificar:
1. Desenhos técnicos aparecem corretamente
2. Layout é idêntico ao PNG gerado
3. Todas as informações estão visíveis
4. Código de barras está legível
```

---
**Data**: 2024
**Status**: ✅ Solução Pronta para Implementação
