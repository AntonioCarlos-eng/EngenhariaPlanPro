# 🔧 REFERÊNCIA TÉCNICA: Sistema de Checkboxes + Editor

## Estrutura de Dados

### 1. Dicionário de Seleção (etiquetas_selecionadas)

```python
self.etiquetas_selecionadas = {
    0: True,   # Etiqueta 0 será impressa
    1: True,   # Etiqueta 1 será impressa  
    2: False,  # Etiqueta 2 será IGNORADA
    3: True,   # Etiqueta 3 será impressa
    ...
    22: False  # Etiqueta 22 (última)
}
```

**Inicialização:**
```python
# Todas começam como True (marcadas) ao abrir editor
self.etiquetas_selecionadas = {i: True for i in range(len(self.dados_processados))}
```

**Acesso:**
```python
# Verificar se etiqueta 5 está selecionada
if self.etiquetas_selecionadas.get(5, True):
    # Será impressa
    
# Contar selecionadas
selecionadas = [i for i, v in self.etiquetas_selecionadas.items() if v]
total = len(selecionadas)  # ex: 14 de 23
```

---

### 2. Dicionário de Medidas Customizadas (medidas_customizadas)

```python
self.medidas_customizadas = {
    ('V8', 'N1'): {
        'bitola': 12.0,
        'qtde': 3,
        'comp': 1.50
    },
    ('V9', 'N2'): {
        'bitola': 8.0,
        'qtde': 1,
        'comp': 1.80
    }
}
```

**Estrutura:**
- **Chave**: `(viga, posicao)` - Tupla identificando a barra
- **Valor**: Dict com campos originais que foram editados

**Acesso:**
```python
# Verificar se existe customização
if ('V8', 'N1') in self.medidas_customizadas:
    bitola_nova = self.medidas_customizadas[('V8', 'N1')]['bitola']
    
# Atualizar/criar customização
self.medidas_customizadas[('V9', 'N2')] = {
    'bitola': 10.0,
    'qtde': 2,
    'comp': 2.00
}
```

---

## Fluxo de Renderização

### desenhar_etiquetas_com_selecao()

```python
def desenhar_etiquetas_com_selecao(self):
    """Renderiza etiquetas COM CHECKBOXES para seleção"""
    
    # 1. Limpar canvas anterior
    self.canvas_etiq.delete("all")
    
    # 2. Calcular range da página atual
    inicio = self.pagina_atual * self.etiquetas_por_pagina  # ex: 0
    fim = min(len(self.dados_processados), inicio + self.etiquetas_por_pagina)  # ex: 6
    
    # 3. Loop para cada etiqueta na página
    for idx in range(inicio, fim):
        dado = self.dados_processados[idx]
        # dado = ('V8', 'N1', 12, 3, 1.50, 4.71)
        
        # 4. Desenhar checkbox (quadrado clicável)
        #    - Cor verde se marcado
        #    - Branco se desmarcado
        #    - Tag "checkbox_{idx}" para eventos
        
        # 5. Desenhar texto da etiqueta
        #    - "OS:1-7  V8-N1  Ø12mm  Q3  1.50m  4.71kg"
        #    - Tag "etiqueta_{idx}" para edição
        
        # 6. Incrementar y_offset para próxima linha
```

**Principais Cálculos:**

```python
# Posição do checkbox à esquerda
x_checkbox = 30
y_checkbox = y_offset + 15

# Desenhar checkbox (retângulo)
if self.etiquetas_selecionadas.get(idx, True):  # Marcado?
    # Verde com checkmark
    cor = "#27ae60"
    simbolo = "✓"
else:
    # Branco vazio
    cor = "white"
    simbolo = ""

# ID do retângulo para cliques
rect_id = self.canvas_etiq.create_rectangle(
    x_checkbox, y_checkbox,
    x_checkbox+20, y_checkbox+20,
    fill=cor, outline="black", width=2
)

# Bind para evento de clique
self.canvas_etiq.tag_bind(f"checkbox_{idx}", "<Button-1>",
    lambda e, i=idx: self._toggle_etiqueta_selecao(i))
```

---

## Lógica de Seleção

### _toggle_etiqueta_selecao(idx)

```python
def _toggle_etiqueta_selecao(self, idx):
    """Alterna estado de um checkbox individual"""
    
    # 1. Inverter estado
    self.etiquetas_selecionadas[idx] = \
        not self.etiquetas_selecionadas.get(idx, True)
    
    # 2. Atualizar counter
    selecionadas = sum(1 for v in self.etiquetas_selecionadas.values() if v)
    self.label_selecionadas.config(
        text=f"Selecionadas: {selecionadas}/{len(self.dados_processados)}"
    )
    
    # 3. Re-renderizar canvas
    self.desenhar_etiquetas_com_selecao()
```

**Fluxo:**
```
Usuário clica checkbox
    ↓
evento <Button-1> capturado
    ↓
_toggle_etiqueta_selecao(5) chamada
    ↓
etiquetas_selecionadas[5] = not etiquetas_selecionadas[5]
    ↓
label_selecionadas atualizado
    ↓
desenhar_etiquetas_com_selecao() reexecutada
    ↓
Canvas redesenhado com novo estado visual
```

---

### _marcar_todas_etiquetas()

```python
def _marcar_todas_etiquetas(self):
    """Marca TODAS as 23 etiquetas para imprimir"""
    
    # 1. Iterar todas e marcar
    for i in range(len(self.dados_processados)):
        self.etiquetas_selecionadas[i] = True
    
    # 2. Atualizar counter
    self.label_selecionadas.config(
        text=f"Selecionadas: {len(self.dados_processados)}/{len(self.dados_processados)}"
    )
    
    # 3. Re-renderizar
    self.desenhar_etiquetas_com_selecao()
```

### _desmarcar_todas_etiquetas()

```python
def _desmarcar_todas_etiquetas(self):
    """Desmarca TODAS as 23 etiquetas"""
    
    # 1. Iterar todas e desmarcar
    for i in range(len(self.dados_processados)):
        self.etiquetas_selecionadas[i] = False
    
    # 2. Atualizar counter
    self.label_selecionadas.config(
        text=f"Selecionadas: 0/{len(self.dados_processados)}"
    )
    
    # 3. Re-renderizar
    self.desenhar_etiquetas_com_selecao()
```

---

## Lógica de Edição

### _editar_etiqueta_dados(idx, viga, pos, bitola, qtde, comp)

```python
def _editar_etiqueta_dados(self, idx, viga, pos, bitola, qtde, comp):
    """Abre diálogo para editar medidas da etiqueta"""
    
    # 1. Criar janela de diálogo (Toplevel)
    dialog = tk.Toplevel(self.janela_editor)
    dialog.title(f"✏️ EDITAR ETIQUETA #{idx+1}")
    dialog.geometry("300x200")
    
    # 2. Criar campos de entrada (Entry widgets)
    tk.Label(dialog, text="Ø Bitola (mm):").grid(row=0, column=0)
    entry_bitola = tk.Entry(dialog)
    entry_bitola.insert(0, str(bitola))
    entry_bitola.grid(row=0, column=1)
    
    tk.Label(dialog, text="Quantidade:").grid(row=1, column=0)
    entry_qtde = tk.Entry(dialog)
    entry_qtde.insert(0, str(qtde))
    entry_qtde.grid(row=1, column=1)
    
    tk.Label(dialog, text="Comprimento (m):").grid(row=2, column=0)
    entry_comp = tk.Entry(dialog)
    entry_comp.insert(0, str(comp))
    entry_comp.grid(row=2, column=1)
    
    # 3. Função para salvar
    def salvar_edicao():
        try:
            # Validar e converter
            novo_bitola = float(entry_bitola.get())
            novo_qtde = int(entry_qtde.get())
            novo_comp = float(entry_comp.get())
            
            # Atualizar dados_processados
            self.dados_processados[idx] = (
                viga, pos, novo_bitola, novo_qtde, novo_comp,
                calcular_peso(novo_bitola, novo_qtde, novo_comp)
            )
            
            # Armazenar customização
            self.medidas_customizadas[(viga, pos)] = {
                'bitola': novo_bitola,
                'qtde': novo_qtde,
                'comp': novo_comp
            }
            
            # Fechar diálogo
            dialog.destroy()
            
            # Re-renderizar com novo valor
            self.desenhar_etiquetas_com_selecao()
            
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos!")
    
    # 4. Botões
    tk.Button(dialog, text="✅ SALVAR", 
              command=salvar_edicao,
              bg="#27ae60", fg="white").pack()
    tk.Button(dialog, text="✕ CANCELAR",
              command=dialog.destroy,
              bg="#e74c3c", fg="white").pack()
```

---

## Lógica de Impressão

### _confirmar_e_imprimir_etiquetas()

```python
def _confirmar_e_imprimir_etiquetas(self):
    """Imprime APENAS as etiquetas selecionadas nos checkboxes"""
    
    # 1. Validar se há seleção
    selecionadas_indices = [i for i, v in self.etiquetas_selecionadas.items() if v]
    
    if not selecionadas_indices:
        messagebox.showwarning("⚠️ NENHUMA SELEÇÃO",
            "Marque ao menos uma etiqueta para imprimir!")
        return
    
    # 2. Filtrar dados apenas das selecionadas
    dados_filtrados = [self.dados_processados[i] for i in selecionadas_indices]
    # Ex: [('V8', 'N1', 12, 3, 1.50, 4.71), ...]
    
    # 3. Confirmar impressão
    resultado = messagebox.askyesno(
        "🖨️ CONFIRMAR IMPRESSÃO",
        f"Você tem certeza que deseja imprimir?\n\n"
        f"Selecionadas: {len(selecionadas_indices)} de {len(self.dados_processados)}"
    )
    
    if not resultado:
        return  # Usuário cancelou
    
    # 4. Usar gerador com dados filtrados
    try:
        gerador = GeradorEtiquetasDinamico(
            arquivos_dxf=self.arquivos_selecionados,
            obra=self.var_obra.get(),
            pavimento=self.var_pavimento.get()
        )
        
        # Substituir dados originais pelos filtrados
        gerador.dados_processados = dados_filtrados
        
        # Aplicar customizações
        if self.medidas_customizadas:
            gerador.medidas_customizadas = self.medidas_customizadas
        
        # 5. Gerar PNGs
        caminhos = gerador.gerar_e_salvar_etiquetas_png(dpi_x=300, dpi_y=300)
        
        # 6. Mostrar resultado
        messagebox.showinfo("✅ ETIQUETAS GERADAS",
            f"✓ {len(caminhos)} etiquetas criadas!")
        
        # Abrir pasta
        os.startfile(r"c:\EngenhariaPlanPro\etiquetas")
        
    except Exception as e:
        messagebox.showerror("❌ ERRO", f"Erro ao gerar: {str(e)}")
```

**Exemplo de Filtro:**
```
Dados originais (23 etiquetas):
[0] ('V8', 'N1', 12, 3, 1.50, 4.71)
[1] ('V8', 'N2', 10, 2, 2.00, 3.14)
[2] ('V9', 'N1', 8, 1, 1.80, 0.79)
...
[22] ('VM2', 'N5', 6, 2, 0.90, 0.53)

Seleção:
{0: True, 1: True, 2: False, ..., 22: True}

Filtro (apenas True):
indices = [0, 1, 3, 4, 5, ..., 22]  # 14 total

Dados filtrados:
[('V8', 'N1', 12, 3, 1.50, 4.71),
 ('V8', 'N2', 10, 2, 2.00, 3.14),
 ('V9', 'N2', 8, 2, 2.20, 1.58),
 ...]  # Apenas 14 etiquetas

→ Gera PNG apenas para essas 14
→ Outras 9 não aparecem nos arquivos
```

---

## Navegação

### _ir_primeira_pagina_etiquetas()
```python
self.pagina_atual = 0
self.desenhar_etiquetas_com_selecao()
```

### _ir_proxima_pagina_etiquetas()
```python
if self.pagina_atual < self.total_paginas - 1:
    self.pagina_atual += 1
    self.desenhar_etiquetas_com_selecao()
```

### _ir_pagina_anterior_etiquetas()
```python
if self.pagina_atual > 0:
    self.pagina_atual -= 1
    self.desenhar_etiquetas_com_selecao()
```

### _ir_ultima_pagina_etiquetas()
```python
self.pagina_atual = self.total_paginas - 1
self.desenhar_etiquetas_com_selecao()
```

**Cálculo de Paginação:**
```python
import math

# Total de páginas
etiquetas_por_pagina = 6  # Máximo por página
total_etiquetas = len(self.dados_processados)  # 23
total_paginas = math.ceil(total_etiquetas / etiquetas_por_pagina)  # 4 (6+6+6+5)

# Calcular range de uma página
pagina_atual = 1  # 0-indexed
inicio = pagina_atual * etiquetas_por_pagina  # 1*6 = 6
fim = min(total_etiquetas, inicio + etiquetas_por_pagina)  # min(23, 12) = 12
# Mostra etiquetas 6-11 (índices 6 a 11)
```

---

## Variáveis de Estado

### Na Classe VigasApp

```python
# Seleção de etiquetas
self.etiquetas_selecionadas = {}  # {idx: bool, ...}

# Edições customizadas
self.medidas_customizadas = {}  # {(viga, pos): {bitola, qtde, comp}}

# Paginação
self.pagina_atual = 0  # Página sendo visualizada
self.etiquetas_por_pagina = 6  # Máximo por página
self.total_paginas = 0  # Calculado automaticamente

# Janelas
self.janela_editor = None  # Toplevel do editor
self.canvas_etiq = None  # Canvas dentro do editor
self.label_selecionadas = None  # Label mostrando contador
self.label_pagina = None  # Label mostrando página

# Zoom (se aplicável)
self.zoom_factor = 1.0
```

---

## Tags do Canvas

```python
# Para checkboxes
f"checkbox_{idx}"  # Ex: "checkbox_0", "checkbox_1", ...

# Para etiquetas (clicáveis para editar)
f"etiqueta_{idx}"  # Ex: "etiqueta_0", "etiqueta_1", ...
```

**Exemplo de Bind:**
```python
# Checkbox
self.canvas_etiq.tag_bind("checkbox_5", "<Button-1>",
    lambda e, i=5: self._toggle_etiqueta_selecao(i))

# Etiqueta
self.canvas_etiq.tag_bind("etiqueta_5", "<Button-1>",
    lambda e, i=5, v=viga, p=pos, b=bitola, q=qtde, c=comp: 
        self._editar_etiqueta_dados(i, v, p, b, q, c))
```

---

## Cores Utilizadas

| Elemento | Cor Hex | RGB | Uso |
|----------|---------|-----|-----|
| Checkbox marcado | #27ae60 | (39, 174, 96) | Verde (selecionado) |
| Checkbox branco | #ffffff | (255, 255, 255) | Vazio (não selecionado) |
| Borda | #000000 | (0, 0, 0) | Contorno do checkbox |
| Título editor | #ff6f00 | (255, 111, 0) | Laranja (destaque) |
| Canvas fundo | #ffffff | (255, 255, 255) | Branco (fundo) |
| Frame seleção | #1a3d2e | (26, 61, 46) | Verde escuro |
| Frame navegação | #34495e | (52, 73, 94) | Cinza azulado |
| Texto | #000000 | (0, 0, 0) | Preto (legibilidade) |
| Texto em fundo escuro | #ffffff | (255, 255, 255) | Branco (contraste) |

---

## Tratamento de Erros

### Validação de Edição

```python
try:
    novo_bitola = float(entry_bitola.get())
    novo_qtde = int(entry_qtde.get())
    novo_comp = float(entry_comp.get())
    
    if novo_bitola <= 0 or novo_qtde <= 0 or novo_comp <= 0:
        raise ValueError("Valores devem ser positivos")
    
    # Atualizar dados...
    
except ValueError as e:
    messagebox.showerror("❌ ERRO", f"Valores inválidos: {str(e)}")
except Exception as e:
    messagebox.showerror("❌ ERRO", f"Erro inesperado: {str(e)}")
```

### Geração de Etiquetas

```python
try:
    gerador = GeradorEtiquetasDinamico(...)
    caminhos = gerador.gerar_e_salvar_etiquetas_png()
except FileNotFoundError:
    messagebox.showerror("Erro", "Arquivo DXF não encontrado")
except PermissionError:
    messagebox.showerror("Erro", "Sem permissão para escrever na pasta")
except Exception as e:
    messagebox.showerror("❌ ERRO NA GERAÇÃO", f"Erro: {str(e)}")
```

---

## Performance

### Otimizações Aplicadas

1. **Render sob demanda**: Canvas redesenha apenas quando necessário
2. **Paginação**: Renderiza máximo 6 etiquetas por página (não 23)
3. **Cache**: Imagens de código/desenho reutilizadas quando possível
4. **Lazy binding**: Tags apenas para objetos visíveis

### Complexidade

```
O(n) para desenhar etiquetas (n = etiquetas na página, max 6)
O(n) para filtro de seleção (n = total, 23)
O(1) para toggle de checkbox
O(1) para atualizar counter
```

---

✨ **Referência Técnica Completa!**
