# CORREÇÕES IMPLEMENTADAS - Etiquetas Vazias

## Resumo
Foram implementadas **8 melhorias críticas** para diagnosticar e corrigir o problema de etiquetas vazias na impressão.

## Mudanças Realizadas

### 1. ✅ Validação Robusta de Dados em `_gerar_imagem_etiqueta()`
**Arquivo**: `vigas_app.py` (linha ~3376)

**Antes**: 
```python
viga = str(dado[0])  # Pode falhar silenciosamente
```

**Depois**:
```python
# Validar se dado está vazio
if not dado or len(dado) < 5:
    draw.text((10, 50), "ERRO: Dados incompletos", fill="red")
    return img

# Conversão segura com valores padrão
viga = str(dado[0]) if dado[0] is not None else "?"
```

**Benefício**: Se os dados estiverem inválidos, a etiqueta mostrará "ERRO: Dados incompletos" em vermelho em vez de ficar em branco.

---

### 2. ✅ Debug Print em `imprimir_etiquetas()`
**Arquivo**: `vigas_app.py` (linha ~3239)

**Adicionado**:
```python
print(f"[DEBUG] Total de etiquetas a imprimir: {len(self.dados_processados)}")
print(f"[DEBUG] Primeira etiqueta: {self.dados_processados[0] if self.dados_processados else 'VAZIA'}")
```

**Benefício**: Você pode abrir o console e verificar se os dados foram realmente carregados antes de tentar imprimir.

---

### 3. ✅ Check de Dados Vazio em `_imprimir_etiquetas_exec()`
**Arquivo**: `vigas_app.py` (linha ~3480)

**Adicionado**:
```python
if not self.dados_processados:
    messagebox.showwarning("Atenção", "Nenhuma etiqueta para imprimir!\nProcesse os arquivos primeiro.")
    return
```

**Benefício**: Previne tentativa de imprimir sem dados e mostra mensagem clara.

---

### 4. ✅ Validação Expandida no Preview
**Arquivo**: `vigas_app.py` (linha ~3490)

**Antes**:
```python
if idx < total_etiquetas:
    img = _gerar_imagem_etiqueta(...)
```

**Depois**:
```python
if idx < total_etiquetas and idx < len(self.dados_processados):
    try:
        img = _gerar_imagem_etiqueta(...)
        # ... salva e abre arquivo
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar prévia:\n{e}")
```

**Benefício**: Mais robustez e mensagens de erro claras na prévia.

---

### 5. ✅ Melhorias em `preencher_tabela()`
**Arquivo**: `vigas_app.py` (linha ~705)

**Adicionado**:
```python
for dado in self.dados_processados:
    if not dado or len(dado) < 5:
        print(f"[WARN] Dado inválido ou incompleto: {dado}")
        continue
    
    try:
        viga, pos, bitola, qtd, comp = dado[0], dado[1], dado[2], dado[3], dado[4]
        peso = dado[5] if len(dado) > 5 else 0.0
    except (ValueError, TypeError, IndexError) as e:
        print(f"[WARN] Erro ao extrair dados: {e}")
        continue
```

**Benefício**: Identifica e pula linhas de dados inválidas em vez de travar.

---

### 6. ✅ Debug Print em `_imprimir_etiquetas_exec()`
**Arquivo**: `vigas_app.py` (linha ~3352)

**Adicionado**:
```python
print(f"[DEBUG] _imprimir_etiquetas_exec iniciado")
print(f"[DEBUG] Total de dados: {len(self.dados_processados)}")
print(f"[DEBUG] Páginas: {page_from} até {page_to}")
if self.dados_processados:
    print(f"[DEBUG] Primeiro dado: {self.dados_processados[0]}")
else:
    print(f"[DEBUG] AVISO: dados_processados está VAZIO!")
```

**Benefício**: Diagnóstico completo do estado dos dados antes da impressão.

---

### 7. ✅ Validação no Loop de Impressão
**Arquivo**: `vigas_app.py` (linha ~3528)

**Adicionado**:
```python
try:
    img = _gerar_imagem_etiqueta(dado, idx, total_etiquetas, dpi_x, dpi_y)
    # ... resto do código
    print(f"[DEBUG] Etiqueta {idx+1} impressa com sucesso")
except Exception as e:
    print(f"[ERRO] Falha ao processar etiqueta {idx+1}: {e}")
    import traceback
    traceback.print_exc()
    continue
```

**Benefício**: Continua impressão mesmo se uma etiqueta falhar, mostrando exatamente qual e por quê.

---

### 8. ✅ Arquivo de Diagnóstico
**Arquivo**: `DIAGNOSTICO_ETIQUETAS_VAZIAS.md`

Documento completo com:
- Possíveis causas do problema
- Passos para diagnosticar
- Como ler os logs de debug
- O que fazer em cada cenário

---

## Como Usar as Correções

### Teste 1: Verificar se dados foram carregados
1. Processe os arquivos (clique "PROCESSAR" ou "PROCESSAR 2.0")
2. Abra o console/terminal (ou execute via PowerShell)
3. Procure por: `[DEBUG] Total de etiquetas a imprimir: X`

### Teste 2: Gerar prévia com debug
1. Clique em "Etiquetas"
2. Na janela, clique em "Prévia"
3. No console, você verá:
   - Se os dados estão OK
   - Exatamente qual etiqueta foi previsuada
   - Se houve algum erro

### Teste 3: Imprimir com debug
1. Na janela de etiquetas, clique "Imprimir"
2. Escolha impressora e clique "Imprimir"
3. No console verá:
   - Quantas etiquetas serão impressas
   - Progresso de cada uma
   - Qualquer erro específico

---

## Se Ainda Assim Não Funcionar

### Cenário A: Console mostra "Total de etiquetas: 0"
- ✗ Os dados NÃO foram processados
- ✓ Solução: Selecione os arquivos e clique PROCESSAR

### Cenário B: Console mostra "AVISO: dados_processados está VAZIO"
- ✗ Os dados foram apagados ou não foram salva
- ✓ Solução: Processe novamente

### Cenário C: Etiqueta mostra "ERRO: Dados incompletos"
- ✗ A estrutura dos dados está errada
- ✓ Solução: Tente o outro motor (v1 ou v2)

### Cenário D: Console mostra "[ERRO] Falha ao processar etiqueta"
- ✗ Erro durante a geração da imagem
- ✓ Solução: Veja a mensagem de erro específica no console

---

## Próximas Melhorias (Futuro)
- [ ] Interface de debug visual integrada
- [ ] Log permanente em arquivo
- [ ] Validação automática de dados
- [ ] Wizard de diagnóstico
