# ALTERACOES REALIZADAS - Editor de Etiquetas

## 1. CAMPO MEDIDA DOBRA ADICIONADO ✓

**Mudanças:**
- Expandido diálogo de edição de 450x350 para 480x420
- Adicionado campo "Medida Dobra (cm)" em amarelo (#ffcc00)
- Campo fica visível para qualquer forma (Dobra Única, Dobra Dupla, etc)
- Valor é salvo em: `self.medidas_customizadas[(viga, pos)]['medida_dobra']`

**Localização:** Função `_editar_etiqueta_dados()` - linha ~3500

**Armazenamento:**
```python
self.medidas_customizadas[(viga, pos)] = {
    'bitola': 14.0,
    'qtde': 4,
    'comp': 1.50,
    'medida_dobra': 5.0  # <-- NOVO CAMPO
}
```

---

## 2. SELECAO INDIVIDUAL CORRIGIDA ✓

**Problema:** Clique em uma etiqueta desmarcava/marcava alternadamente
**Solução:** Agora clique marca APENAS aquela etiqueta, desmarcando todas as outras

**Mudanças:**
- Função `_toggle_etiqueta_selecao()` agora faz:
  1. Desmarca TODAS as etiquetas
  2. Marca APENAS a clicada
  3. Re-renderiza canvas

**Código:**
```python
def _toggle_etiqueta_selecao(self, idx):
    # Desmarca todas
    self.etiquetas_selecionadas = {i: False for i in range(len(self.dados_processados))}
    # Marca só a clicada
    self.etiquetas_selecionadas[idx] = True
    # Re-renderizar...
```

---

## 3. IMPRESSAO ALTERADA ✓

**Antes:** 
- Gerava PNGs
- Salvava em pasta `c:\EngenhariaPlanPro\etiquetas\`
- Abria pasta no explorador

**Depois:**
- Gera PNGs 300 DPI
- Envia direto ao gerador (SEM salvar em pasta)
- Mostra mensagem de sucesso com contagem de etiquetas processadas

**Mensagem de Confirmação:**
```
✅ ENVIADO PARA IMPRESSORA
✓ 1 etiqueta(s) processada(s)!

📋 Formato: PNG 300 DPI
🖨️ Enviando para impressora térmica...

Etiqueta(s) selecionada(s) foram processadas com sucesso!
```

---

## RESUMO DAS MODIFICACOES

| Item | Antes | Depois | Linha |
|------|-------|--------|-------|
| Tamanho diálogo edição | 450x350 | 480x420 | 3485 |
| Campo medida dobra | NÃO | SIM (amarelo) | 3518 |
| Armazenamento dobra | NÃO | `medida_dobra` key | 3543 |
| Toggle checkbox | Toggle on/off | Marca única | 3456 |
| Impressão | Salva + abre pasta | Envia gerador | 3715 |
| Mensagem sucesso | Com path da pasta | Sem path | 3722 |

---

## COMO USAR

### Para editar medida de dobra:
1. Clique em uma etiqueta
2. No diálogo que abre, vá para "Medida Dobra (cm):"
3. Digite o valor
4. Clique "SALVAR"

### Para imprimir UMA ÚNICA etiqueta:
1. Clique sobre a etiqueta desejada (marca só aquela)
2. Clique "✅ CONFIRMAR E IMPRIMIR"
3. Confirme no diálogo
4. Será processada e enviada para impressora

### Para marcar várias:
1. Use botões "Marcar Todas" / "Desmarca Todas"
2. Depois clique "CONFIRMAR E IMPRIMIR"

---

## DADOS DISPONÍVEIS PARA GERADOR

```python
# Medidas customizadas (com novo campo)
{
    ('V8', 'N1'): {
        'bitola': 14.0,
        'qtde': 4,
        'comp': 1.50,
        'medida_dobra': 5.0  # ← NOVO
    }
}

# Formas customizadas (mantém igual)
{
    ('V8', 'N1'): 'Dobra Única',
    ('V8', 'N2'): 'Estribo Quadrado'
}

# Selecao individual (agora marca uma)
{
    0: True,   # ← Única etiqueta marcada
    1: False,
    2: False,
    3: False
}
```

---

## VALIDACOES

✅ Sem erros de sintaxe
✅ Campo medida dobra armazenado
✅ Seleção individual funciona
✅ Impressão remove save de pasta
✅ Mensagem de sucesso atualizada
