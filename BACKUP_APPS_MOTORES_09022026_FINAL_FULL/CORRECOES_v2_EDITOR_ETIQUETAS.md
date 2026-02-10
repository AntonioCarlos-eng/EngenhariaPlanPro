# CORRECOES IMPLEMENTADAS - Editor de Etiquetas v2

## 1. CAMPOS DINAMICOS POR FORMA ✓

**Problema:** Só tinha 1 campo de "Medida Dobra" para todos os tipos de forma

**Solução:** Diálogo agora mostra campos específicos conforme a forma selecionada

### Campos por tipo:
- **Reta**: Sem campos adicionais
- **Dobra Única**: 1 campo "Medida Dobra (cm)"
- **Dobra Dupla**: 2 campos "1ª Dobra" e "2ª Dobra (cm)"
- **Estribo Quadrado**: 4 campos "Lado 1", "Lado 2", "Lado 3", "Lado 4 (cm)"
- **Estribo Retângulo**: 4 campos "Largura", "Altura", "Lado 3", "Lado 4 (cm)"
- **Estribo Redondo**: 1 campo "Raio (cm)"

**Implementação:**
- Diálogo expandido de 480x420 → 520x550
- Frame dinâmico `frame_medidas` que se atualiza ao trocar forma
- Evento `<<ComboboxSelected>>` triggers `atualizar_campos_forma()`
- Todos os valores armazenados em `medidas_customizadas[(viga, pos)]`

---

## 2. FORMAS PERSISTIDAS NO GERADOR ✓

**Problema:** Quando salvava a edição, o desenho voltava a "Reta"

**Causa:** Gerador não estava recebendo/usando `formas_customizadas`

**Solução:** 

### Em `vigas_app.py`:
- Função `_confirmar_e_imprimir_etiquetas()` já passa `formas_customizadas` ao gerador:
```python
if self.formas_customizadas:
    gerador.formas_customizadas = self.formas_customizadas
```

### Em `etiquetas_generator.py`:
- Adicionados atributos ao `__init__`:
```python
self.medidas_customizadas = {}
self.formas_customizadas = {}
```
- Função `gerar_dados_etiqueta()` agora retorna:
```python
'medidas_customizadas': self.medidas_customizadas.get((viga, pos), {}),
'forma_customizada': self.formas_customizadas.get((viga, pos), "Reta")
```

**Resultado:** Formas agora são persistidas durante toda a geração de etiquetas!

---

## 3. CHECKBOXES VISUAIS MELHORADOS ✓

**Problema:** Checkboxes não eram claros visualmente

**Solução:** Renderização visual melhorada com checkmark

### Antes:
- Quadrado verde com símbolo ✓ (unicode problemático)
- Tamanho pequeno

### Depois:
- Quadrado **marcado**: Verde (#27ae60) com checkmark desenhado com linhas
- Quadrado **desmarcado**: Branco com borda preta e borda interna cinza
- Tamanho aumentado: 24px
- Área de clique expandida: -4 a +4px de margem

**Código de renderização:**
```python
if marcado:
    # Verde + checkmark com linhas
    create_rectangle(fill="#27ae60", outline="#1a5c3a", width=2)
    create_line(x1, y1, x2, y2, x3, y3, fill="white", width=3)  # Checkmark
else:
    # Branco com bordas
    create_rectangle(outline="#333333", width=2, fill="white")
    create_rectangle(interno, outline="#cccccc", width=1)
```

---

## ESTRUTURA DE DADOS ATUALIZADA

```python
# Medidas customizadas (expandida com campos por forma)
self.medidas_customizadas = {
    ('V8', 'N1'): {
        'bitola': 12.0,
        'qtde': 3,
        'comp': 1.50,
        'medida_dobra': 5.5,      # Dobra Única
        'medida_dobra_2': 0.0,    # Dobra Dupla (2ª dobra)
        'lado1': 0.0,             # Estribo
        'lado2': 0.0,
        'lado3': 0.0,
        'lado4': 0.0,
        'raio': 0.0               # Estribo Redondo
    }
}

# Formas persistidas
self.formas_customizadas = {
    ('V8', 'N1'): 'Dobra Única',
    ('V8', 'N2'): 'Estribo Quadrado',
    ('V9', 'N1'): 'Estribo Redondo'
}

# Seleção individual (marca uma por vez)
self.etiquetas_selecionadas = {
    0: False,
    1: False,
    2: True,   # <-- Apenas esta está selecionada
    3: False
}
```

---

## FLUXO DE USO

1. **Abrir editor** → Clica "ETIQUETAS"
2. **Ver checkboxes** → Checkboxes visuais aparecem à esquerda
3. **Selecionar uma** → Clica no checkbox (marca apenas aquela)
4. **Editar medidas** → Clica na etiqueta → Dialog abre
5. **Escolher forma** → Combobox atualiza campos conforme tipo
6. **Preencher medidas** → Campos dinâmicos aparecem/desaparecem
7. **Salvar** → Forma e medidas são guardadas em `formas_customizadas` e `medidas_customizadas`
8. **Imprimir** → Dados customizados são enviados ao gerador mantendo forma!

---

## VALIDACOES

✅ Checkboxes renderizam corretamente (visual melhorado)
✅ Clique em checkbox seleciona UMA etiqueta (marca única)
✅ Dialog expande e mostra campos corretos por forma
✅ Medidas são armazenadas ALL os campos (lado1-4, dobra, raio)
✅ Formas são persistidas no gerador (não volta a "Reta")
✅ Sem erros de sintaxe em ambos arquivos
✅ Impressão recebe `formas_customizadas` e `medidas_customizadas`
