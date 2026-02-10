# 🎯 GUIA VISUAL: Etiquetas Funcionando

## Fluxo Normal (Correto)

```
┌─────────────────────────────────────────────────────────┐
│                  VIGAS APP                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Selecionar Arquivos  📁 ──→ DXF/DWG carregados ✅  │
│                                                         │
│  2. PROCESSAR  ⚙️  ──→ Tabela preenchida ✅           │
│     (vê dados na tabela: V1, V2, V3...)                │
│                                                         │
│  3. Etiquetas  🏷️  ──→ Janela abre ✅                 │
│                                                         │
│  4. Prévia  👁️  ──→ Imagem com dados aparece ✅      │
│     (mostra OBRA, VIGA, BITOLA, QTDE, COMP, PESO)     │
│                                                         │
│  5. Imprimir 🖨️  ──→ Etiquetas saem impressas ✅     │
│     (com todos os dados preenchidos)                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Etiqueta Correta (Esperado)

```
┌───────────────────────────────────────────┐
│ ┌──────────┐                              │
│ │OBRA 001  │  OS 1-10                    │  ← Cabeçalho
│ │PAV TÉRREO│                              │
│ └──────────┘                              │
├───────────────────────────────────────────┤
│                                           │
│  VIGA: V1                                 │
│  POS: 4                                   │
│  BITOLA: 12.5 mm                         │
│  QTDE: 2 un                              │
│  COMP: 2.80 m                            │
│  PESO: 0.617 kg                          │
│                                           │ ← Dados
│  ┌─────────────────────────────────────┐ │
│  │  [Desenho técnico da barra]         │ │
│  │  ███████████████████████            │ │
│  └─────────────────────────────────────┘ │
│                                           │
│  ┌─────────────────────────────────────┐ │
│  │ ║║║║║║║║║║║║║║║║║║║║║║║║║║║║║║║║║  │ ← Código de barras
│  │ SAGA001-V301-001-01-12.5-250        │ │
│  └─────────────────────────────────────┘ │
│                                           │
└───────────────────────────────────────────┘
   (Tamanho real: 10cm x 15cm)
```

## Etiqueta com Erro (O Que Evitar Agora)

### Antes (❌ Antes da Correção)
```
┌───────────────────────────────────────────┐
│                                           │
│                                           │
│                                           │  ← COMPLETAMENTE VAZIA!
│                                           │
│                                           │
│                                           │
└───────────────────────────────────────────┘
```

### Depois (✅ Depois da Correção)
```
┌───────────────────────────────────────────┐
│ ┌──────────┐                              │
│ │OBRA 001  │  OS 1-10                    │
│ │PAV TÉRREO│                              │
│ └──────────┘                              │
├───────────────────────────────────────────┤
│                                           │
│  ERRO: Dados incompletos                 │ ← Mensagem em VERMELHO
│  Etiqueta 1                              │
│                                           │
│  (Se vê isso → Refaça o processamento)   │
│                                           │
└───────────────────────────────────────────┘
```

## Passos com Output Esperado

### Passo 1: Selecionar Arquivos

```
┌────────────────────────────────────────┐
│ EngenhariaPlanPro - VIGAS              │
├────────────────────────────────────────┤
│  📁 Selecionar Arquivos                │  ← Clica aqui
└────────────────────────────────────────┘

[Abre diálogo]
  projeto_vigas.dxf  (selecionado ✅)
  detalhes.dxf       (selecionado ✅)

Status: ✅ 2 arquivo(s) carregado(s)
```

### Passo 2: Processar

```
┌────────────────────────────────────────┐
│ ⚙️ PROCESSAR                            │  ← Clica aqui
└────────────────────────────────────────┘

[Processando...]
[DEBUG] Total de etiquetas: 5
[DEBUG] Primeira etiqueta: (V1, 4, 12.5, 2, 2.80, 0.617)

Resultado:
┌───────────────────────────────────────┐
│ VIGA  │ POS │ BITOLA │ QTD │ COMP │ PESO
├───────────────────────────────────────┤
│  V1   │  4  │ 12.5   │ 2   │ 2.80 │ 0.617
│  V1   │  1  │ 10.0   │ 4   │ 3.50 │ 0.494
│  V2   │  2  │  8.0   │ 3   │ 4.00 │ 0.237
│  ...  │ ... │  ...   │ ... │ ...  │ ...
└───────────────────────────────────────┘

Status: ✅ Total: 5 barras | 2.348 kg
```

### Passo 3: Etiquetas

```
┌────────────────────────────────────────┐
│ 🏷️ Etiquetas                            │  ← Clica aqui
└────────────────────────────────────────┘

[Abre janela]
Total de Etiquetas: 5 | Formato: 10x15cm

🏞️ PREVIEW DA PÁGINA 1

┌──────────────────────┐
│ [ETIQUETA 1]         │  ← Etiqueta com dados
│ V1, POS 4, Ø12.5    │
│ [...]                │
└──────────────────────┘

Página 1 de 1
```

### Passo 4: Prévia

```
[Clica "Prévia" 👁️]

[Abre arquivo PNG]

✅ Mostra etiqueta com todos os dados
   - OBRA 001
   - VIGA V1
   - POS 4
   - BITOLA 12.5mm
   - QTDE 2
   - COMP 2.80m
   - PESO 0.617kg
   - Código de barras
```

### Passo 5: Imprimir

```
[Clica "Imprimir" 🖨️]

[Diálogo de impressão]
  Impressora: [HP LaserJet] ▼
  Páginas: 1 até 1
  Escala: 100%
  
  [Imprimir]

[Impressora inicia]

[DEBUG] Etiqueta 1 impressa com sucesso
[DEBUG] Etiqueta 2 impressa com sucesso
[DEBUG] Etiqueta 3 impressa com sucesso
[DEBUG] Etiqueta 4 impressa com sucesso
[DEBUG] Etiqueta 5 impressa com sucesso

✅ Impressão concluída!
```

## Diagnóstico: Verificar Logs

### Console Esperado (✅ Correto)

```
[DEBUG] imprimir_etiquetas() iniciado
[DEBUG] Total de etiquetas a imprimir: 5
[DEBUG] Primeira etiqueta: ('V1', '4', 12.5, 2, 2.80, 0.617)
[DEBUG] _imprimir_etiquetas_exec iniciado
[DEBUG] Total de dados: 5
[DEBUG] Páginas: 1 até 1
[DEBUG] Primeiro dado: ('V1', '4', 12.5, 2, 2.80, 0.617)
[DEBUG] Etiqueta 1 impressa com sucesso
[DEBUG] Etiqueta 2 impressa com sucesso
[DEBUG] Etiqueta 3 impressa com sucesso
[DEBUG] Etiqueta 4 impressa com sucesso
[DEBUG] Etiqueta 5 impressa com sucesso

✅ Tudo OK!
```

### Console com Problema (❌ Incorreto)

```
[DEBUG] imprimir_etiquetas() iniciado
[DEBUG] Total de etiquetas a imprimir: 0
[DEBUG] Primeira etiqueta: VAZIA

[AVISO] dados_processados está VAZIO!

❌ Nenhuma etiqueta para imprimir!
Processe os arquivos primeiro.

Solução: Clique "PROCESSAR" na tela principal
```

### Console com Dados Inválidos (⚠️ Aviso)

```
[DEBUG] Total de etiquetas a imprimir: 5
[DEBUG] Primeira etiqueta: ('V1', '4', None, 2, 2.80)  ← FALTA BITOLA!

[WARN] Dado inválido no índice 0: (...)
[ERRO] Falha ao converter BITOLA: could not convert string to float: None

✅ Etiqueta 1 mostrará "ERRO: Dados incompletos"

Solução: Tente o outro motor de processamento
```

## Estrutura de Dados Esperada

```
self.dados_processados = [
    # (viga, pos, bitola, qtde, comp, peso)
    ('V1', '4', 12.5, 2, 2.80, 0.617),      ✅ Correto
    ('V1', '1', 10.0, 4, 3.50, 0.494),
    ('V2', '2', 8.0, 3, 4.00, 0.237),
    # ...
]

TIPOS ESPERADOS:
  viga  → str   (exemplo: "V1", "V2")
  pos   → str   (exemplo: "1", "4", "N1")
  bitola → float (exemplo: 8.0, 10.0, 12.5)
  qtde  → int   (exemplo: 2, 3, 4)
  comp  → float (exemplo: 2.80, 3.50)
  peso  → float (exemplo: 0.617, 0.494)
```

## Estrutura Inválida (❌ Evitar)

```
❌ Falta de elementos:
    ('V1', '4', 12.5, 2)  ← Faltam comp e peso
    → Resultado: "ERRO: Dados incompletos"

❌ Tipos errados:
    ('V1', 4, '12.5', '2', 2.80, 0.617)  ← pos é int, bitola é str
    → Resultado: Conversão com erro

❌ Valores None:
    ('V1', '4', None, 2, 2.80, 0.617)  ← bitola é None
    → Resultado: Erro ao converter float

❌ Vazio:
    ()  ← Sem dados
    → Resultado: "ERRO: Dados incompletos"
```

## Fluxo de Correção Visual

```
ANTES (Problema)
────────────────────────────────────────────
  Arquivo DXF
    ↓ (processa)
  Lista de dados
    ↓ (tenta imprimir)
  ❌ ETIQUETA VAZIA
    ↓ (nenhuma mensagem)
  😞 Usuário confuso


DEPOIS (Corrigido)
────────────────────────────────────────────
  Arquivo DXF
    ↓ (processa)
  Lista de dados
    ↓ (valida estrutura)
    ├─ ✅ Dados válidos? SIM → Imprime etiqueta cheia
    │
    └─ ❌ Dados inválidos? → Mostra "ERRO" em VERMELHO
    
  ✅ Usuário sabe o que fazer
     (processa novamente ou tenta outro motor)
```

---

**Visualizações criadas**: 16 de janeiro de 2026
**Versão**: 1.0 com exemplos ASCII
