# 🔄 FASE 4: Layout 10x15cm com 3 Picotes (Pronto para Iniciar)

## Objetivo

Redesenhar as etiquetas para o formato final:
- **Tamanho**: 10cm x 15cm (conforme especificado)
- **Formato**: 3 seções perforadas idênticas
- **Cada seção**: Contém exatamente a mesma etiqueta
- **Marcas de corte**: Para facilitar recorte

---

## Especificação Técnica

### Dimensões
```
┌─────────────────────────────────────────────┐
│  10cm (largura)                             │
│  ┌─────────────────┬─────────────────┐     │
│  │                 │                 │     │
│  │  Seção 1        │  Picote 1       │     │
│  │  ~5cm x 5cm     │  (linha)        │ 5cm │
│  │                 │                 │     │
│  │  [Etiqueta]     │ [Etiqueta]      │     │
│  │                 │                 │     │
│  ├─────────────────┼─────────────────┤     │
│  │ Picote (linha tracejada)                │
│  ├─────────────────┼─────────────────┤     │
│  │                 │                 │     │
│  │  Seção 2        │  Picote 2       │ 5cm │
│  │                 │                 │     │
│  ├─────────────────┼─────────────────┤     │
│  │ Picote (linha tracejada)                │
│  ├─────────────────┼─────────────────┤     │
│  │                 │                 │     │
│  │  Seção 3        │  Picote 3       │ 5cm │
│  │                 │                 │     │
│  └─────────────────┴─────────────────┘     │
│  15cm (altura)                              │
└─────────────────────────────────────────────┘
```

### Especificações de Impressão
- **Papel**: A4 (210x297mm)
- **Orientação**: Retrato
- **Margem**: 5mm em todos os lados
- **Resolução**: 300 DPI (para impressão)
- **Formato final**: 10cm x 15cm por etiqueta

---

## Plano de Implementação

### Passo 1: Criar Novo Canvas (100x150mm)
```python
# Em gerar_etiquetas():
largura_etiqueta = 100   # mm (10cm)
altura_etiqueta = 150    # mm (15cm)
altura_secao = 50        # mm (5cm x 3)

# Canvas de impressão:
largura_canvas = 210     # A4 retrato
altura_canvas = 297
```

### Passo 2: Estruturar 3 Seções
```python
for secao in range(3):
    y_inicio = 30 + (secao * 55)  # 30mm margem + espaço
    
    # Desenhar moldura
    canvas.create_rectangle(
        30, y_inicio,
        180, y_inicio + 50,
        outline="blue", width=2
    )
    
    # Copiar conteúdo da etiqueta atual
    _desenhar_etiqueta_interna(
        x=35, 
        y=y_inicio+5,
        viga, pos, bitola, qtde, comp
    )
```

### Passo 3: Adicionar Picotes (Linhas Tracejadas)
```python
# Linhas tracejadas entre seções
for secao in range(2):
    y_picote = 30 + ((secao + 1) * 55)
    
    # Linha tracejada horizontal
    canvas.create_line(
        30, y_picote,
        180, y_picote,
        fill="red",
        dash=(5, 5),  # Padrão tracejado
        width=1
    )
    
    # Label "PICOTE" ou símbolo
    canvas.create_text(
        100, y_picote-3,
        text="✄ PICOTE - DESTACAR AQUI",
        font=("Arial", 6),
        fill="red"
    )
```

### Passo 4: Ajustar Informações Dinâmicas
```python
# Código de barras: redimensionar de 250x60 para ~90x30
# PNG técnico: redimensionar de 120x80 para ~80x50
# Textos: ajustar tamanhos para caber em 100mm
```

### Passo 5: Adicionar Marcas de Corte
```python
# Marcas de corte (crop marks) nos cantos
def _desenhar_marca_corte(x, y):
    canvas.create_line(x-5, y, x+5, y, width=1, fill="black")
    canvas.create_line(x, y-5, x, y+5, width=1, fill="black")

# Nos 4 cantos de cada seção
_desenhar_marca_corte(30, 30)      # Superior esquerdo
_desenhar_marca_corte(180, 30)     # Superior direito
_desenhar_marca_corte(30, 80)      # Inferior esquerdo
_desenhar_marca_corte(180, 80)     # Inferior direito
```

---

## Implementação Sugerida

### Estrutura de Código

```python
def gerar_etiquetas(self):
    """Gera etiquetas 10x15cm com 3 picotes"""
    
    # ... código anterior ...
    
    # Canvas A4 retrato (210x297mm)
    self.canvas_etiq = tk.Canvas(
        self.janela_etiq,
        width=210 * 4,    # pixels (aproximado)
        height=297 * 4,
        bg="white"
    )
    
    # ... resto do método ...

def desenhar_pagina_etiquetas_vigas_FASE4(self):
    """NOVA: Desenha 3 seções de 10x15cm com picotes"""
    
    self.canvas_etiq.delete("all")
    
    LARGURA_ETIQ = 150  # mm convertidos para pixels
    ALTURA_SECAO = 50
    MARGEM = 30
    
    # Para cada etiqueta:
    inicio = self.pagina_atual * 1  # 1 etiqueta por página agora
    fim = min(inicio + 1, len(self.dados_processados))
    
    for idx in range(inicio, fim):
        dado = self.dados_processados[idx]
        
        # Desenhar 3 seções idênticas
        for secao in range(3):
            y_secao = MARGEM + (secao * (ALTURA_SECAO + 5))
            
            # Moldura da seção
            self._desenhar_moldura_etiqueta(MARGEM, y_secao, LARGURA_ETIQ, ALTURA_SECAO)
            
            # Conteúdo da etiqueta
            self._desenhar_conteudo_etiqueta(
                MARGEM + 5, y_secao + 5,
                dado, is_mini=True
            )
            
            # Picotes entre seções
            if secao < 2:
                y_picote = y_secao + ALTURA_SECAO + 2
                self._desenhar_picote(MARGEM, y_picote, LARGURA_ETIQ)

def _desenhar_moldura_etiqueta(self, x, y, w, h):
    """Desenha moldura com marcas de corte"""
    # Moldura principal
    self.canvas_etiq.create_rectangle(x, y, x+w, y+h, outline="#ff6f00", width=2)
    
    # Marcas de corte
    tamanho_marca = 5
    # Cantos
    for px, py in [(x, y), (x+w, y), (x, y+h), (x+w, y+h)]:
        self.canvas_etiq.create_line(px-tamanho_marca, py, px+tamanho_marca, py, width=1)
        self.canvas_etiq.create_line(px, py-tamanho_marca, px, py+tamanho_marca, width=1)

def _desenhar_picote(self, x, y, w):
    """Desenha linha de picote tracejada"""
    self.canvas_etiq.create_line(x, y, x+w, y, dash=(5, 5), fill="red", width=1)
    self.canvas_etiq.create_text(
        x + w//2, y - 8,
        text="✄ PICOTE",
        font=("Arial", 6),
        fill="red"
    )
```

---

## Testes para Validar

### Teste 1: Dimensões
```
□ Cada seção mede ~50mm de altura
□ Largura total 100mm
□ 3 seções com espaço entre elas
□ Cabe em página A4
```

### Teste 2: Conteúdo
```
□ Cada seção tem código de barras
□ Cada seção tem PNG técnico
□ Cada seção tem dados da barra
□ Conteúdo não sobrepõe
```

### Teste 3: Impressão
```
□ Margem de 5mm em todos os lados
□ Linhas de corte visíveis
□ Picotes bem espaçados
□ Pode imprimir sem problemas
```

### Teste 4: Usabilidade
```
□ Fácil de cortar nas linhas tracejadas
□ Cada seção é independente
□ Código de barras legível após corte
□ PNG técnico legível após corte
```

---

## Estimativa de Esforço

| Tarefa | Tempo |
|--------|-------|
| Criar estrutura de 3 seções | 1h |
| Redimensionar elementos (barcode, PNG) | 1h |
| Adicionar picotes e marcas de corte | 30min |
| Testes de layout e impressão | 1h |
| Documentação e refinamento | 30min |
| **Total** | **4 horas** |

---

## Modificações Necessárias

### Em `vigas_app.py`:

1. **Método `gerar_etiquetas()`**
   - Mudar `etiquetas_por_pagina` de 4 para 1
   - Ajustar dimensões do canvas

2. **Método `desenhar_pagina_etiquetas_vigas()`**
   - Refatorar para desenhar 3 seções
   - Ajustar posicionamento

3. **Funções auxiliares novas**
   - `_desenhar_moldura_etiqueta()`
   - `_desenhar_conteudo_etiqueta()`
   - `_desenhar_picote()`
   - `_desenhar_marca_corte()`

### Linhas estimadas
```
Código novo: ~150 linhas
Código refatorado: ~100 linhas
Total: ~250 linhas
```

---

## Checklist de Implementação

- [ ] Estrutura de 3 seções criada
- [ ] Molduras com marcas de corte
- [ ] Linhas de picote adicionadas
- [ ] Código de barras redimensionado
- [ ] PNG técnico redimensionado
- [ ] Textos ajustados para tamanho menor
- [ ] Testes de dimensões validados
- [ ] Testes de impressão validados
- [ ] Documentação atualizada
- [ ] Sem quebra de código anterior

---

## Próximas Etapas

### Após FASE 4 estar pronta:

✅ Validar com impressão real
✅ Ajustar margens se necessário
✅ Testar corte manual
✅ Verificar código de barras em scanner
✅ Passar para FASE 5 (PDF)

---

## Pronto para Começar?

Quando quiser iniciar a implementação da FASE 4, avise!

**Estimativa**: 4 horas para conclusão completa

Desenvolvido com ❤️ | Status: 📋 Ready to Implement
