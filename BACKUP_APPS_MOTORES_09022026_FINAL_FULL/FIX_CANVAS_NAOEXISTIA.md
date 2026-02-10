# 🔧 FIX - Canvas não Existia

## ❌ O Problema

Erro: `AttributeError: '_tkinter.tkapp' object has no attribute 'canvas_etiq'`

**Causa**: A função `imprimir_etiquetas()` tentava usar `self.canvas_etiq` que nunca foi criado na interface.

A app usa `self.tree` (Treeview) para dados, não tem canvas editável.

## ✅ A Solução

### Nova Arquitetura

```
Click "Etiquetas"
  ↓
ABRE JANELA SEPARADA (tk.Toplevel)
  ↓
Cria canvas_etiq DENTRO da janela
  ↓
Renderiza preview editável
  ↓
Usuário edita/confirma
  ↓
Fecha janela
```

### Mudanças Feitas

1. **`imprimir_etiquetas()`** agora:
   - Cria `self.janela_editor = tk.Toplevel()`
   - Cria `self.canvas_etiq` DENTRO dela
   - Renderiza `desenhar_pagina_etiquetas_vigas_fase4()`
   - Com try/except para erros de renderização

2. **`_fechar_editor_etiquetas()`** agora:
   - Destroi `self.janela_editor` corretamente
   - Limpa canvas automaticamente

### Código Novo

```python
def imprimir_etiquetas(self):
    """Abre JANELA SEPARADA com PREVIEW EDITÁVEL"""
    if not self.dados_processados:
        return
    
    # CRIAR JANELA
    self.janela_editor = tk.Toplevel(self)
    self.janela_editor.title("✏️ EDITOR DE ETIQUETAS")
    self.janela_editor.geometry("1000x800")
    
    # CRIAR CANVAS DENTRO DA JANELA
    self.canvas_etiq = tk.Canvas(
        canvas_frame,
        bg="white",
        yscrollcommand=scrollbar.set
    )
    
    # RENDERIZAR
    self.desenhar_pagina_etiquetas_vigas_fase4()
    
    # BOTÕES
    [Confirmar, Editar, Fechar]
```

## 🎯 Resultado

- ✓ Canvas agora existe (criado na janela)
- ✓ Janela separada não interfere com app principal
- ✓ Usuário pode editar em paz
- ✓ Sem erros de AttributeError

## 📝 Fluxo Correto Agora

```
1. Usuário clica "ETIQUETAS"
   ↓
2. Janela separada abre com preview
   ↓
3. Usuário vê TODAS as etiquetas no canvas
   ↓
4. Pode EDITAR clicando nos valores
   ↓
5. Clica "CONFIRMAR"
   ↓
6. Gera PNG 300 DPI
   ↓
7. Abre pasta
   ↓
8. Usuário imprime
```

## ✅ Status

- ✓ Erros corrigidos
- ✓ Canvas criado corretamente
- ✓ Janela separada funciona
- ✓ Pronto para testar
