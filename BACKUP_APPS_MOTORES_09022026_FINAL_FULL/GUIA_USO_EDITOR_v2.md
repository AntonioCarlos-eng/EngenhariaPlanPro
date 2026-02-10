# GUIA DE USO - Editor de Etiquetas v2

## NOVO NO v2: 3 RECURSOS PRINCIPAIS

### 1️⃣ CHECKBOXES VISUAIS PARA SELECAO

**Onde:** À esquerda de cada etiqueta no canvas

**Aparencia:**
```
  ✅ Checkbox VERDE com checkmark = Etiqueta selecionada
  ☐  Checkbox BRANCO vazio = Etiqueta desmarcada
```

**Como usar:**
1. Clique no checkbox para marcar/desmarcar
2. **OBS:** Clique MARCA UMA ETIQUETA APENAS (desmarca todas as outras)
3. Use "Marcar Todas" / "Desmarca Todas" para operacoes em lote

---

### 2️⃣ CAMPOS DE MEDIDAS POR FORMA

**Onde:** Dialog de edicao (ao clicar na etiqueta)

**Como mudar:**
1. Clique na etiqueta para abrir dialog
2. No combobox "Forma/Desenho:", escolha:
   - `Reta` - Sem campos extras
   - `Dobra Única` - 1 campo: "Medida Dobra (cm)"
   - `Dobra Dupla` - 2 campos: "1ª Dobra" e "2ª Dobra (cm)"
   - `Estribo Quadrado` - 4 campos: "Lado 1", "Lado 2", "Lado 3", "Lado 4 (cm)"
   - `Estribo Retângulo` - 4 campos: "Largura", "Altura", "Lado 3", "Lado 4 (cm)"
   - `Estribo Redondo` - 1 campo: "Raio (cm)"
3. Os campos aparecem/desaparecem AUTOMATICAMENTE
4. Preencha os valores
5. Clique "SALVAR"

**Exemplo 1 - Estribo Quadrado:**
```
Forma/Desenho: [Estribo Quadrado ▼]

Lado 1 (cm): [10.0]
Lado 2 (cm): [20.0]
Lado 3 (cm): [10.0]
Lado 4 (cm): [20.0]

✅ SALVAR | ✕ CANCELAR
```

**Exemplo 2 - Dobra Dupla:**
```
Forma/Desenho: [Dobra Dupla ▼]

1ª Dobra (cm): [5.5]
2ª Dobra (cm): [7.0]

✅ SALVAR | ✕ CANCELAR
```

---

### 3️⃣ PERSISTENCIA DE FORMAS

**O que era:** Quando salvava a edicao, o desenho voltava a "Reta"

**Agora:** A forma escolhida é MANTIDA mesmo apos salvar e reimprimir

**Como funciona:**
1. Edita etiqueta e escolhe forma "Estribo Quadrado"
2. Clica SALVAR
3. Forma é armazenada em `formas_customizadas[(viga, pos)]`
4. Mesmo apos fechar e reabrir, forma permanece "Estribo Quadrado"
5. Na impressao, gerador recebe a forma correta

---

## FLUXO TIPICO DE USO

```
1. Carregar DXF
   ↓
2. Clica "ETIQUETAS"
   ↓
3. Editor abre com checkboxes visuais à esquerda
   ↓
4. Clica checkbox de etiqueta que deseja editar
   ↓
5. Clica na etiqueta para abrir dialog
   ↓
6. Muda Bitola, Quantidade, Comprimento (se necessário)
   ↓
7. Escolhe Forma (ex: "Estribo Quadrado")
   ↓
8. Campos aparecem dinamicamente (Lado 1, 2, 3, 4)
   ↓
9. Preenche valores das medidas
   ↓
10. Clica "✅ SALVAR"
    ↓
11. Dialog fecha, etiqueta atualizada no canvas
    ↓
12. Clica "✅ IMPRIMIR SELECIONADAS"
    ↓
13. Confirma no diálogo
    ↓
14. Etiqueta é gerada COM forma e medidas mantidas! ✓
```

---

## CAMPOS DISPONIVEIS

### Reta
- Sem campos adicionais

### Dobra Única
- `medida_dobra` (cm)

### Dobra Dupla
- `medida_dobra` (1ª Dobra em cm)
- `medida_dobra_2` (2ª Dobra em cm)

### Estribo Quadrado
- `lado1`, `lado2`, `lado3`, `lado4` (em cm)

### Estribo Retângulo
- `lado1` (Largura em cm)
- `lado2` (Altura em cm)
- `lado3`, `lado4` (em cm)

### Estribo Redondo
- `raio` (em cm)

---

## BOTOES PRINCIPAIS

| Botão | O que faz |
|-------|-----------|
| ☑️ **MARCAR TODAS** | Marca todas as etiquetas |
| ☐ **DESMARCA TODAS** | Desmarca todas |
| ✅ **IMPRIMIR SELECIONADAS** | Envia ao gerador apenas as selecionadas |
| ✕ **FECHAR** | Fecha editor sem imprimir |
| ℹ️ **COMO** | Mostra instrucoes |

---

## DICAS

✓ Cada clique em checkbox desmarca os outros (selecao unica por vez)
✓ Use "Marcar Todas" se quiser imprimir multiplas etiquetas
✓ Todos os campos de medidas sao SEMPRE armazenados (mesmo os vazios)
✓ Forma nao volta mais a "Reta" apos salvar!
✓ Checkboxes visuais facilitam ver qual etiqueta vai ser impressa

---

## NOTAS TECNICAS

- Campos de forma sao dinamicos via `atualizar_campos_forma()`
- Medidas armazenam em `medidas_customizadas[(viga, pos)]` com TODOS os campos
- Formas armazenam em `formas_customizadas[(viga, pos)]`
- Gerador recebe ambos dicts e usa os valores salvos
- Selecao individual via `_toggle_etiqueta_selecao(idx)`
- Checkboxes renderizam com checkmark (linhas, nao Unicode)

---

## TROUBLESHOOTING

**Problema:** Clicou em checkbox mas nao marcou
- **Solucao:** Clicar NO checkbox (area verde/branca), nao na etiqueta

**Problema:** Campos nao aparecem apos trocar forma
- **Solucao:** Aguarde um segundo - frame dinamico esta atualizando

**Problema:** Forma voltou a "Reta" apos imprimir
- **Solucao:** Nao deve acontecer mais! Mas se acontecer, reabra o editor

**Problema:** Valores de medida sao zerados
- **Solucao:** Normal - campos vazios armazenam 0.0, preencha quando necessário

---

Pronto para usar! 🚀
