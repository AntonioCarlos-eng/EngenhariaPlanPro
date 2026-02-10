# 🎯 SOLUÇÃO REAL E SIMPLES

## O Problema Real
Você tem 2 telas:
1. **EDITOR** (com checkboxes) - ✅ FUNCIONA, mostra edições
2. **PREVIEW** (janela separada) - ❌ NÃO FUNCIONA, mostra PNGs antigos

## A Solução Mais Simples

**NÃO USAR O PREVIEW SEPARADO!**

Adicionar botão "IMPRIMIR SELECIONADAS" **DENTRO DO EDITOR** que já funciona!

### Implementação

No editor (janela com checkboxes), adicionar botão:

```python
# No final do editor, onde tem os botões:
ttk.Button(
    frame_botoes,
    text="🖨️ IMPRIMIR SELECIONADAS",
    command=self._imprimir_direto_do_editor
).pack(side=tk.LEFT, padx=5)

def _imprimir_direto_do_editor(self):
    """Imprime direto do editor (sem preview separado)"""
    # Pegar selecionadas
    selecionadas = [i for i, var in enumerate(self.check_vars) if var.get()]
    
    if not selecionadas:
        messagebox.showwarning("Atenção", "Selecione pelo menos uma etiqueta!")
        return
    
    # Confirmar
    if not messagebox.askyesno(
        "Confirmar Impressão",
        f"Imprimir {len(selecionadas)} etiqueta(s) selecionada(s)?"
    ):
        return
    
    # Gerar e imprimir (COM customizações)
    from core.etiquetas_generator import GeradorEtiquetasDinamico
    
    gerador = GeradorEtiquetasDinamico(
        arquivos_dxf=self.arquivos_selecionados,
        pasta_etiquetas="etiquetas",
        obra=self.var_obra.get(),
        pavimento=self.var_pavimento.get()
    )
    
    # COPIAR customizações
    gerador.medidas_customizadas = self.medidas_customizadas.copy()
    gerador.formas_customizadas = self.formas_customizadas.copy()
    
    # Filtrar selecionadas
    gerador.dados = [self.dados_processados[i] for i in selecionadas]
    
    # Imprimir
    sucesso = gerador.gerar_e_imprimir_direto()
    
    if sucesso:
        messagebox.showinfo("Sucesso", f"{len(selecionadas)} etiqueta(s) impressa(s)!")
    else:
        messagebox.showerror("Erro", "Falha na impressão")
```

## Por Que Isso Funciona?

1. ✅ Editor JÁ mostra as edições corretamente
2. ✅ Não precisa de preview separado
3. ✅ Imprime direto com as customizações
4. ✅ Usuário VÊ no editor antes de imprimir
5. ✅ Simples e direto

## Implementar Agora?

Posso adicionar esse botão no editor agora mesmo. É só 1 botão e 1 função.

Muito mais simples que tentar consertar o preview com cache!
