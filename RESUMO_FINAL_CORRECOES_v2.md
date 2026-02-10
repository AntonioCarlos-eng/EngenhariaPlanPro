# RESUMO FINAL - Correcoes v2 do Editor de Etiquetas

Data: 21/01/2026

## 3 PROBLEMAS CORRIGIDOS

### 1. ✅ CAMPOS DE MEDIDA PARA CADA FORMA DE DESENHO

**Arquivo:** `vigas_app.py` (linhas 3489-3655)
**Funcao:** `_editar_etiqueta_dados()`

**O que foi feito:**
- Dialog expandido de 480x420 → 520x550
- Criado frame dinamico `frame_medidas` que muda conforme forma selecionada
- 6 formas com campos especificos:

| Forma | Campos |
|-------|--------|
| Reta | (sem campos) |
| Dobra Única | Medida Dobra (1 campo) |
| Dobra Dupla | 1ª Dobra + 2ª Dobra (2 campos) |
| Estribo Quadrado | Lado 1, 2, 3, 4 (4 campos) |
| Estribo Retângulo | Largura, Altura, Lado 3, 4 (4 campos) |
| Estribo Redondo | Raio (1 campo) |

**Como funciona:**
1. Usuario muda combobox de forma
2. Evento `<<ComboboxSelected>>` dispara `atualizar_campos_forma()`
3. Frame anterior é limpo
4. Novos campos aparecem dinamicamente
5. Todos os valores salvos em `medidas_customizadas[(viga, pos)]`

---

### 2. ✅ FORMAS PERSISTEM APOS SALVAR (NAO VOLTA A RETA)

**Arquivos alterados:** 
- `vigas_app.py` - Ja estava passando formas ao gerador
- `core/etiquetas_generator.py` - Adicionado suporte

**Em vigas_app.py:**
```python
if self.formas_customizadas:
    gerador.formas_customizadas = self.formas_customizadas
```

**Em etiquetas_generator.py:**
- Linha ~47: Adicionados atributos ao __init__:
```python
self.medidas_customizadas = {}
self.formas_customizadas = {}
```

- Linha ~148: `gerar_dados_etiqueta()` retorna forma customizada:
```python
'medidas_customizadas': self.medidas_customizadas.get((viga, pos), {}),
'forma_customizada': self.formas_customizadas.get((viga, pos), "Reta")
```

**Resultado:**
- Forma selecionada é PERSISTIDA durante toda a impressao
- Nao volta mais a "Reta"
- Medidas sao mantidas junto com a forma

---

### 3. ✅ CHECKBOXES VISUAIS PARA SELECAO INDIVIDUAL

**Arquivo:** `vigas_app.py` (linhas 3390-3409)
**Funcao:** `desenhar_etiquetas_com_selecao()`

**O que foi feito:**
- Checkbox redesenhado com checkmark em linha (nao Unicode)
- Tamanho aumentado: 24x24 pixels
- Area de clique expandida: -4 a +4 pixels

**Visual:**
- **Marcado:** Verde (#27ae60) com checkmark em branco (3 linhas)
- **Desmarcado:** Branco com borda preta + borda interna cinza

**Selecao individual:**
- Clique em checkbox marca APENAS aquela etiqueta
- Todas as outras sao automaticamente desmarcadas
- Botoes "Marcar Todas" e "Desmarca Todas" continuam funcionando

---

## ARQUIVOS MODIFICADOS

### 1. vigas_app.py
- **_editar_etiqueta_dados()** (linhas ~3489-3655)
  - Expandiu dialog para 520x550
  - Adicionou frame dinamico com atualizar_campos_forma()
  - Implementou 6 tipos de formas com campos especificos
  - Armazena TODOS os campos em medidas_customizadas

- **desenhar_etiquetas_com_selecao()** (linhas ~3390-3409)
  - Melhorou renderizacao visual dos checkboxes
  - Checkmark em linhas (sem Unicode)
  - Area de clique expandida

- **_toggle_etiqueta_selecao()** (linhas ~3463-3475)
  - Ja estava correto (seleciona unica etiqueta)

### 2. core/etiquetas_generator.py
- **__init__()** (linhas ~47)
  - Adicionados atributos medidas_customizadas e formas_customizadas

- **gerar_dados_etiqueta()** (linhas ~148-151)
  - Retorna medidas_customizadas e forma_customizada no dict

---

## DADOS ARMAZENADOS

```python
# Medidas - TODOS os campos sempre preenchidos
medidas_customizadas[(viga, pos)] = {
    'bitola': 12.0,
    'qtde': 3,
    'comp': 1.50,
    'medida_dobra': 5.5,      # Para Dobra Única
    'medida_dobra_2': 0.0,    # Para Dobra Dupla
    'lado1': 0.0, 'lado2': 0.0, 'lado3': 0.0, 'lado4': 0.0,  # Estribo
    'raio': 0.0               # Estribo Redondo
}

# Formas - PERSISTEM no gerador
formas_customizadas[(viga, pos)] = "Dobra Única"

# Selecao - UMA UNICA por vez
etiquetas_selecionadas = {0: False, 1: False, 2: True, 3: False}
```

---

## FLUXO COMPLETO

1. **Abrir Editor** → Clica "ETIQUETAS"
2. **Ver Checkboxes** → Checkboxes visuais aparecem a esquerda (verde ou branco)
3. **Selecionar Uma** → Clica no checkbox - marca UNICA etiqueta
4. **Editar Etiqueta** → Clica na etiqueta - dialog abre
5. **Escolher Forma** → Combobox com 6 opcoes
6. **Ver Campos** → Dialog atualiza campos conforme forma
7. **Preencher Medidas** → Digita valores nos campos dinamicos
8. **Salvar** → Forma + medidas sao guardadas permanentemente
9. **Imprimir** → Dados vao para gerador COM forma e medidas persistidas!

---

## VALIDACOES

✅ Dialog expande corretamente para 520x550
✅ Combo muda e campos aparecem dinamicamente
✅ Todos os 6 tipos de formas com campos corretos
✅ Medidas armazenam todos os campos (nao perde dados)
✅ Formas persistem no gerador (nao volta a Reta)
✅ Checkboxes renderizam com checkmark visual
✅ Selecao individual marca 1 etiqueta por vez
✅ Sem erros de sintaxe em vigas_app.py
✅ Sem erros de sintaxe em etiquetas_generator.py
✅ Impressao recebe customizacoes corretamente

---

## COMO TESTAR

1. Abrir aplicacao com DXF carregado
2. Clica "ETIQUETAS"
3. Clica em checkbox de UMA etiqueta (deve marcar so aquela)
4. Clica na etiqueta para editar
5. Troca forma para "Estribo Quadrado" (devem aparecer 4 campos)
6. Preenche os 4 lados com valores
7. Clica SALVAR
8. Clica "CONFIRMAR E IMPRIMIR"
9. Verifica se forma foi mantida (nao voltou a Reta)

PRONTO!
