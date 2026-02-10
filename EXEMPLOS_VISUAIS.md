# 🎨 EXEMPLOS VISUAIS - Sistema de Checkboxes v2.0

## Interface do Editor - Visualização Completa

### Cenário 1: Primeira Página (Padrão)

```
╔═════════════════════════════════════════════════════════════╗
║     ✏️ EDITOR - EDITE, SELECIONE E IMPRIMA (Laranja)      ║
╠═════════════════════════════════════════════════════════════╣
║                                                             ║
║  ☑ #01  OS:1-7  V8-N1   Ø12mm  Q3  1.50m  4.71kg          ║
║  ☑ #02  OS:1-5  V9-N1   Ø10mm  Q2  2.00m  3.14kg          ║
║  ☐ #03  OS:2-5  V9-N2   Ø8mm   Q1  1.80m  0.79kg          ║
║  ☑ #04  OS:3-5  V9-N3   Ø8mm   Q1  1.80m  0.79kg          ║
║  ☑ #05  OS:4-5  V9-N4   Ø8mm   Q2  1.80m  1.58kg          ║
║  ☐ #06  OS:5-5  V9-N5   Ø8mm   Q1  1.80m  0.79kg          ║
║                                                             ║
║  [Canvas com scrollbar para mais etiquetas...]            ║
║                                                             ║
╠═════════════════════════════════════════════════════════════╣
║                 Página 1 de 4  🔘🔘🔘🔘                     ║
║    [⏮ Primeira]  [◀ Anterior]  [Próxima ▶]  [Última ⏭] ║
╠═════════════════════════════════════════════════════════════╣
║  🔘 Seleção:                                                ║
║     [☑️ MARCAR TODAS]  [☐ DESMARCAR TODAS]                 ║
║                                      Selecionadas: 4/6     ║
╠═════════════════════════════════════════════════════════════╣
║  📋 Total: 23 etiquetas | 💡 Clique para editar            ║
║         [ℹ️ COMO] [✅ IMPRIMIR SELECIONADAS] [✕ FECHAR]   ║
╚═════════════════════════════════════════════════════════════╝
```

---

## Estados Visuais dos Checkboxes

### Checkbox Marcado (Será Impresso)
```
┌─────────────┐
│ ☑ Verde    │
│ #27ae60    │  
│ Com ✓      │
│ Selecionado│
└─────────────┘
```

**Código:**
```python
canvas.create_rectangle(30, 15, 50, 35, fill="#27ae60", outline="black", width=2)
canvas.create_text(40, 25, text="✓", font=("Arial", 12), fill="white")
```

### Checkbox Desmarcado (NÃO Será Impresso)
```
┌─────────────┐
│ ☐ Branco   │
│ #ffffff    │
│ Vazio      │
│ Não marcado│
└─────────────┘
```

**Código:**
```python
canvas.create_rectangle(30, 15, 50, 35, outline="black", width=2, fill="white")
```

---

## Interações do Usuário

### 1. Clicar em Checkbox Individual

```
ANTES:
☑ #01  OS:1-7  V8-N1  Ø12mm  Q3  1.50m  4.71kg
                      (marcado para impressão)

↓ Usuário clica no checkbox ↓

DEPOIS:
☐ #01  OS:1-7  V8-N1  Ø12mm  Q3  1.50m  4.71kg
                   (desmarcado, não será impresso)

Canvas atualiza em tempo real (~50ms)
Counter muda: "Selecionadas: 4/6" → "Selecionadas: 3/6"
```

### 2. Clicar "MARCAR TODAS"

```
ANTES:
☑ #01  ...
☐ #02  ...
☑ #03  ...
☐ #04  ...
☐ #05  ...  Selecionadas: 2/5

↓ Usuário clica [☑️ MARCAR TODAS] ↓

DEPOIS:
☑ #01  ...
☑ #02  ...  ← Agora marcado
☑ #03  ...
☑ #04  ...  ← Agora marcado
☑ #05  ...  ← Agora marcado
Selecionadas: 5/5

Canvas redesenha com todos verdes
```

### 3. Clicar em Etiqueta para Editar

```
Tela Principal:
☑ #01  OS:1-7  V8-N1  Ø12mm  Q3  1.50m  4.71kg

↓ Usuário clica sobre a linha ↓

Diálogo Pop-up:
┌───────────────────────────────────┐
│  ✏️ EDITAR ETIQUETA #01           │
├───────────────────────────────────┤
│  Ø Bitola (mm):   [12]            │
│  Quantidade:      [3]             │
│  Comprimento (m): [1.50]          │
│                                   │
│  [✅ SALVAR]  [✕ CANCELAR]       │
└───────────────────────────────────┘

↓ Usuário edita e clica SALVAR ↓

Volta à tela principal:
☑ #01  OS:1-7  V8-N1  Ø14mm  Q3  1.50m  4.71kg
                                   ↑ Valor atualizado!
```

---

## Navegação Entre Páginas

### Exemplo: Navegando para Página 2

```
ANTES (Página 1):
☑ #01  OS:1-7  V8-N1   ...
☑ #02  OS:1-5  V9-N1   ...
☐ #03  OS:2-5  V9-N2   ...
☑ #04  OS:3-5  V9-N3   ...
☑ #05  OS:4-5  V9-N4   ...
☐ #06  OS:5-5  V9-N5   ...

Página 1 de 4

↓ Usuário clica [Próxima ▶] ↓

DEPOIS (Página 2):
☑ #07  OS:6-5  V9-N6   ...
☐ #08  OS:7-5  V9-N7   ...
☑ #09  OS:1-4  V10-N1  ...
☑ #10  OS:2-4  V10-N2  ...
☐ #11  OS:3-4  V10-N3  ...
☐ #12  OS:4-4  V10-N4  ...

Página 2 de 4

Label atualizado
Canvas redesenhado
Seleções mantidas (o que foi marcado na página 1 permanece)
```

---

## Processo Completo: Do Início ao Fim

### Passo 1: Abrir Editor
```
Janela Principal
      ↓
[ETIQUETAS] ← Usuário clica
      ↓
Abre tk.Toplevel com editor
```

### Passo 2: Ver Página 1 (6 etiquetas)
```
Editor renderiza:
- Checkbox para cada uma
- Dados da etiqueta
- 4 estão marcadas (verde ✓)
- 2 não estão (branco ☐)
- Counter: "Selecionadas: 4/6"
```

### Passo 3: Editar Uma (Opcional)
```
[Clica na #03 que está branca]
      ↓
Diálogo abre
Usuário muda: Ø10 → Ø12
      ↓
[✅ SALVAR]
      ↓
Retorna ao editor
#03 agora mostra "Ø12"
```

### Passo 4: Marcar/Desmarcar Selecionadas
```
[☑️ MARCAR TODAS]
      ↓
Todos os checkboxes ficam verdes
Contador: "Selecionadas: 6/6"
      ↓
[Clica em #02 para desmarcar]
      ↓
#02 fica branco ☐
Contador: "Selecionadas: 5/6"
```

### Passo 5: Navegar para Próxima Página
```
[Próxima ▶]
      ↓
Canvas redesenha com próximas 6 etiquetas
"Página 2 de 4"
Seleções anteriores mantidas na memória
```

### Passo 6: Confirmar Impressão
```
[✅ IMPRIMIR SELECIONADAS]
      ↓
Diálogo:
"Você tem certeza que deseja imprimir?

Selecionadas: 14 de 23 etiquetas
Formato: 100×150mm
Qualidade: 300 DPI

Clique 'Sim' para gerar"
      ↓
[Sim]
      ↓
Gerador filtra dados
Cria PNG apenas das 14 selecionadas
Abre pasta com resultado
```

---

## Exemplo de Dado Processado

### Antes da Edição
```
Índice: 0
Dados: ('V8', 'N1', 12, 3, 1.50, 4.71)
            │    │  │  │   │    │
            │    │  │  │   │    └─ Peso (kg)
            │    │  │  │   └───── Comprimento (m)
            │    │  │  └───────── Quantidade
            │    │  └─────────── Bitola (mm)
            │    └───────────── Posição (nó)
            └─────────────── Viga

Estado: etiquetas_selecionadas[0] = True (selecionada)
```

### Após Edição
```
Usuário edita: Bitola 12 → 14, Qtde 3 → 4

Dados atualizados: ('V8', 'N1', 14, 4, 1.50, 6.28)

Customizado em: medidas_customizadas[('V8', 'N1')] = {
    'bitola': 14.0,
    'qtde': 4,
    'comp': 1.50
}

Estado: Mantido (ainda selecionada)
```

---

## Filtro na Impressão

### Dados Originais (23 etiquetas)
```
[0] ('V8', 'N1', 12, 3, 1.50, ...)  → Selecionada ✓
[1] ('V8', 'N2', 10, 2, 2.00, ...)  → Selecionada ✓
[2] ('V9', 'N1', 8, 1, 1.80, ...)   → NÃO selecionada ✗
[3] ('V9', 'N2', 8, 1, 1.80, ...)   → Selecionada ✓
...
[22] ('VM2', 'N5', 6, 2, 0.90, ...) → Selecionada ✓
```

### Filtro Aplicado
```python
selecionadas_indices = [i for i, v in etiquetas_selecionadas.items() if v]
# Resultado: [0, 1, 3, 4, 5, 7, 8, 9, 10, 12, 15, 17, 19, 22]
# Total: 14 de 23

dados_filtrados = [dados_processados[i] for i in selecionadas_indices]
# Resultado: Lista com apenas 14 etiquetas
```

### Geração de PNGs
```
Gerador recebe dados_filtrados (14 etiquetas)
      ↓
Itera apenas sobre esses 14
      ↓
Gera 14 arquivos PNG no diretório
      ↓
Pasta abre mostrando:
  etiqueta_001.png
  etiqueta_002.png  (skip #003 porque não foi selecionada)
  etiqueta_004.png
  ...
  etiqueta_023.png
```

---

## Estados de Botões

### Botão "MARCAR TODAS"
```
Cor: #27ae60 (Verde)
Ação: Set all etiquetas_selecionadas[i] = True
Efeito: Canvas redesenha com todos os checkboxes verdes
Result: Counter atualiza para "Selecionadas: 23/23"
```

### Botão "DESMARCAR TODAS"
```
Cor: #e74c3c (Vermelho)
Ação: Set all etiquetas_selecionadas[i] = False
Efeito: Canvas redesenha com todos os checkboxes brancos
Result: Counter atualiza para "Selecionadas: 0/23"
Aviso: Se tentar imprimir sem nada selecionado, mostra alerta
```

### Botão "IMPRIMIR SELECIONADAS"
```
Cor: #27ae60 (Verde)
Tamanho: Grande (destaque)
Ação: Filtrar e gerar
Validação: Se 0 selecionadas, mostra warning
Confirmação: Diálogo simples "Tem certeza?"
Feedback: Mostra resultado "✓ 14 etiquetas criadas!"
```

---

## Mensagens de Usuário

### Alerta: Nenhuma Seleção
```
┌──────────────────────────────────┐
│  ⚠️ NENHUMA SELEÇÃO             │
├──────────────────────────────────┤
│  Você não marcou nenhuma etiqueta│
│  para imprimir!                  │
│                                  │
│  Use os botões MARCAR TODAS ou   │
│  clique nos checkboxes individuais│
│                                  │
│            [OK]                  │
└──────────────────────────────────┘
```

### Confirmação: Impressão
```
┌──────────────────────────────────┐
│  🖨️ CONFIRMAR IMPRESSÃO         │
├──────────────────────────────────┤
│  Você tem certeza que deseja     │
│  imprimir?                       │
│                                  │
│  Selecionadas: 14 de 23          │
│  Formato: 100×150mm              │
│  Qualidade: 300 DPI              │
│                                  │
│          [Sim]  [Não]            │
└──────────────────────────────────┘
```

### Sucesso: Etiquetas Geradas
```
┌──────────────────────────────────┐
│  ✅ ETIQUETAS GERADAS           │
├──────────────────────────────────┤
│  ✓ 14 etiquetas criadas!         │
│                                  │
│  📁 Localização:                 │
│  c:\EngenhariaPlanPro\etiquetas\ │
│                                  │
│  📋 Formato: PNG 300 DPI         │
│  🖨️ Pronto para impressora      │
│                                  │
│  Abra a pasta para visualizar!   │
│            [OK]                  │
└──────────────────────────────────┘
```

---

## Cores e Paleta Visual

```
┌─────────────────────────────────┐
│ Elemento          │ Cor    │ HEX   │
├─────────────────────────────────┤
│ Checkbox marcado  │ Verde  │#27ae60│
│ Checkbox branco   │ Branco │#ffffff│
│ Borda checkbox    │ Preto  │#000000│
│ Título editor     │ Laranja│#ff6f00│
│ Canvas fundo      │ Branco │#ffffff│
│ Frame seleção     │ Verde  │#1a3d2e│
│ Frame navegação   │ Cinza  │#34495e│
│ Texto normal      │ Preto  │#000000│
│ Texto claro       │ Branco │#ffffff│
│ Botão positivo    │ Verde  │#27ae60│
│ Botão negativo    │ Vermho │#e74c3c│
│ Botão info        │ Azul   │#3498db│
└─────────────────────────────────┘
```

---

## Timeline Completo da Sessão

```
T=0:00    Usuário processa DXF
          ↓
T=0:05    Clica em "ETIQUETAS"
          ↓ (500ms para abrir)
T=0:01    Editor abre com Página 1
          ├─ Renderiza 6 etiquetas
          ├─ Carrega checkboxes
          └─ Counter mostra selecionadas
          ↓
T=0:30    Usuário navega (pode revisar todas)
          ├─ Página 1 → 2 → 3 → 4
          └─ Marca/desmarca conforme revisa
          ↓
T=0:15    Usuário edita 2 etiquetas
          ├─ #03: Bitola 8→10
          ├─ #07: Comp 1.80→2.00
          └─ Ambas salvam
          ↓
T=0:20    Usuário faz seleção final
          ├─ Marca as 14 que vai imprimir
          └─ Counter: "14/23"
          ↓
T=0:05    Clica "IMPRIMIR SELECIONADAS"
          ├─ Confirmação aparece
          └─ Usuário clica "Sim"
          ↓ (2s para processar)
T=0:02    Gerador processa (1.5s)
          ├─ Filtra 14 etiquetas
          ├─ Aplica customizações
          ├─ Gera 300 DPI PNGs
          └─ Pasta abre
          ↓
T=0:00    Sucesso! Arquivos prontos para impressora

Total:    ~1 minuto 17 segundos (workflow completo)
```

---

✨ **Exemplos Visuais Completos!**
