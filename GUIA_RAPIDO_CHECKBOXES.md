# 🎯 GUIA RÁPIDO: Sistema de Checkboxes + Editor de Etiquetas

## Como Usar (Passo a Passo)

### PASSO 1: Abrir Editor
```
Janela Principal da Aplicação
          ↓
   [ETIQUETAS] (botão laranja)
          ↓
Abre janela "EDITOR - EDITE, SELECIONE E IMPRIMA"
```

### PASSO 2: Ver Todas as Etiquetas
```
A janela mostra MÁXIMO 6 etiquetas por página
          ↓
Cada etiqueta tem UM CHECKBOX à esquerda:
  ☑ Selecionada (verde) - será impressa
  ☐ Não selecionada (branco) - será ignorada
          ↓
Use [⏮ Primeira], [◀ Anterior], [Próxima ▶], [Última ⏭] 
para navegar entre as 8 páginas
```

### PASSO 3: Marcar/Desmarcar Etiquetas
```
Opção A: Uma a uma
  • Clique no checkbox (☑/☐)
  
Opção B: Em lote
  • [☑️ MARCAR TODAS] - marca todas (1-8 páginas)
  • [☐ DESMARCAR TODAS] - desmarca todas

Counter atualiza: "Selecionadas: X/23"
```

### PASSO 4: Editar Dados (OPCIONAL)
```
Clique SOBRE o texto de uma etiqueta:
  "OS:1-7 V8-N1 Ø12mm Q3 1.50m 4.71kg"
          ↓
Abre diálogo: "✏️ EDITAR ETIQUETA #01"
          ↓
Campos editáveis:
  • Ø Bitola (mm): [12]
  • Quantidade: [3]
  • Comprimento (m): [1.50]
          ↓
[✅ SALVAR] → Atualiza na tela
  ou
[✕ CANCELAR] → Descarta edições
```

### PASSO 5: Imprimir Selecionadas
```
Após revisar e editar (opcional):
          ↓
[✅ IMPRIMIR SELECIONADAS]
          ↓
Diálogo de confirmação:
  "Selecionadas: 14 de 23 etiquetas
   Formato: 100×150mm (10×15cm)
   Qualidade: 300 DPI
   Clique 'Sim' para gerar PNG/PDF"
          ↓
[Sim] → Gera arquivos PNG em:
        c:\EngenhariaPlanPro\etiquetas\
          ↓
Abre pasta automaticamente
```

---

## 📊 Mapeamento de Estados

### Estados do Checkbox

```
┌─ Checkbox ─────────────────┐
│                             │
│  Selecionado        Vazio   │
│  ☑ (Verde #27ae60) ☐       │
│  Texto: ✓            --    │
│  Borda: Preta        Preta │
│  Fill: Verde         Branco│
│                             │
│  Clique → Inverte estado   │
│  Novo render da tela       │
└─────────────────────────────┘
```

### Estados da Etiqueta

```
┌─ Etiqueta No 01 ─────────────────────────────────────┐
│                                                       │
│  ☑ #01  OS:1-7  V8-N1  Ø12mm  Q3  1.50m  4.71kg    │
│  └─ Checkbox: estado da seleção                     │
│          └─ Número sequencial                       │
│                └─ Ordem de Serviço (1-7 significa  │
│                    1ª de 7 total deste viga)       │
│                     └─ Identificação                 │
│                            └─ Medidas               │
│                                    └─ Peso          │
│                                                       │
│  Clique no checkbox → Alterna seleção               │
│  Clique no resto → Abre editor de dados             │
└───────────────────────────────────────────────────────┘
```

---

## 🎨 Legenda Visual

| Ícone | Significado |
|-------|-------------|
| ☑ | Etiqueta selecionada para imprimir (verde) |
| ☐ | Etiqueta NÃO selecionada (branco) |
| ✓ | Confirmado/Salvo |
| ✕ | Cancelar/Fechar |
| ✏️ | Editar |
| 🖨️ | Imprimir |
| 📋 | Listar/Resumo |
| ⏮ | Ir para primeira página |
| ◀ | Página anterior |
| ▶ | Próxima página |
| ⏭ | Ir para última página |
| ☑️ | Marcar tudo |
| ☐ | Desmarcar tudo |
| ℹ️ | Informação/Ajuda |

---

## ⚡ Atalhos e Dicas Rápidas

### Para MARCAR rapidamente:
1. Primeiro clique em "☑️ MARCAR TODAS"
2. Depois desmarque apenas as que NÃO quer (clique no checkbox)
3. Assim você deixa a maioria selecionada

### Para DESMARCAR rapidamente:
1. Primeiro clique em "☐ DESMARCAR TODAS"
2. Depois marque apenas as que QUER (clique no checkbox)
3. Assim você deixa apenas as desejadas selecionadas

### Para EDITAR vários valores:
1. Navegue página a página
2. Clique em cada etiqueta que precisa editar
3. Mude os valores no diálogo
4. Clique ✅ SALVAR
5. Passe para próxima página
6. Repita conforme necessário

### Para REVISAR antes de imprimir:
1. Use "☑️ MARCAR TODAS"
2. Navegue por todas as 8 páginas lendo cada uma
3. Desmarque as que tiverem problemas
4. Depois clique "IMPRIMIR SELECIONADAS"

---

## 🔍 O Que Cada Coluna Significa

```
Exemplo de etiqueta:
☑ #03  OS:2-5  V9-N2  Ø8mm  Q1  1.80m  0.79kg
│      │       │      │    │   │     │
│      │       │      │    │   │     └─ PESO: 0.79 quilogramas
│      │       │      │    │   └─ COMPRIMENTO: 1.80 metros
│      │       │      │    └─ QTDE: Quantidade 1 unidade
│      │       │      └─ BITOLA: Diâmetro 8 milímetros
│      │       └─ IDENTIFICAÇÃO: Viga 9, Nó 2
│      └─ ORDEM DE SERVIÇO: 2ª de 5 barras neste grupo
└─ CHECKBOX: Seleção para impressão
```

---

## 🛠️ Funcionalidades Detalhadas

### 1. CHECKBOX (☑/☐)
- **Função**: Selecionar qual etiqueta será impressa
- **Visual**: Quadrado com borda preta
- **Estados**:
  - Verde com ✓ = Será impressa
  - Branco vazio = NÃO será impressa
- **Como usar**: Clique sobre o quadrado para alternar
- **Atualização**: Instantânea (feedback visual imediato)

### 2. DADOS DA ETIQUETA
- **Função**: Mostrar informações da barra de aço
- **Conteúdo**: Viga, Nó, Bitola, Qtde, Comprimento, Peso
- **Editável**: SIM (clique para abrir editor)
- **Salvo em**: Memória durante a sessão
- **Aplicado em**: Geração das PNGs

### 3. MARCAR/DESMARCAR TUDO
- **Função**: Selecionar/desselecionar todas as 23 etiquetas de uma vez
- **Velocidade**: Ideal para grandes lotes
- **Estratégia**: Marque tudo, depois desmarque os exceções
- **Atualização**: Reflete imediatamente no contador

### 4. NAVEGAÇÃO
- **Função**: Ver páginas diferentes (máximo 6 por página)
- **Total**: 8 páginas = 23 etiquetas
- **Botões**: Primeira, Anterior, Próxima, Última
- **Contador**: Mostra "Página X de 8"
- **Estado**: Ao navegar, canvas redesenha com nova página

### 5. EDITOR DE DADOS
- **Função**: Modificar bitola, qtde e comprimento
- **Ativação**: Duplo-clique ou clique direto na linha
- **Diálogo**: Nova janela com 3 campos de texto
- **Validação**: Básica (precisa ser número)
- **Ação**:
  - ✅ SALVAR: Aplica mudança e fecha
  - ✕ CANCELAR: Descarta e fecha
- **Persistência**: Mantém até fechar a aplicação

### 6. IMPRESSÃO SELECIONADAS
- **Função**: Gerar PNGs apenas dos checkboxes marcados
- **Processo**:
  1. Filtra dados_processados pelos índices selecionados
  2. Aplica edições customizadas
  3. Chama gerador com dados filtrados
  4. Gera 300 DPI PNG
  5. Abre pasta com resultado
- **Resultado**: Apenas as etiquetas selecionadas são impressas
- **Pasta**: c:\EngenhariaPlanPro\etiquetas\

---

## 🚨 Possíveis Problemas e Soluções

### Problema: "Nenhuma etiqueta selecionada para imprimir!"
- **Causa**: Nenhum checkbox foi marcado
- **Solução**: Use "☑️ MARCAR TODAS" ou clique manualmente
- **Confirmação**: Counter deve mostrar "Selecionadas: X/23" onde X > 0

### Problema: Edição não salva
- **Causa**: Clicou ✕ CANCELAR em vez de ✅ SALVAR
- **Solução**: Clique novamente na etiqueta e edite de novo
- **Confirmação**: Valor na tela deve atualizar após ✅ SALVAR

### Problema: Só vejo "1/8 etiquetas"
- **Causa**: Navegação antiga (antes da atualização)
- **Solução**: Atualize para versão nova e use os botões de navegação
- **Confirmação**: Deve mostrar até 6 etiquetas por página

### Problema: Checkbox não muda de cor
- **Causa**: Canvas não redesenhou
- **Solução**: Navegue para outra página e volta
- **Confirmação**: Checkbox deve mudar para ☑ (verde) ou ☐ (branco)

---

## 📈 Resumo de Melhorias

| Antes | Depois |
|--------|---------|
| Sem preview | ✅ Preview com checkboxes |
| Sem seleção | ✅ Seleção individual + botões em lote |
| Sem edição | ✅ Editor de dados com diálogo |
| Não conseguia revisar | ✅ Navegação paginada (6 por página) |
| Imprime tudo ou nada | ✅ Filtra apenas selecionadas |
| Interface amadora | ✅ Interface profissional com cores |

---

## ✅ Checklist de Testes

- [ ] Abrir editor de etiquetas (clique em "ETIQUETAS")
- [ ] Ver primeira página com até 6 etiquetas
- [ ] Clicar em checkbox e ver mudança de cor
- [ ] Usar "MARCAR TODAS" - todos ficam verdes
- [ ] Usar "DESMARCAR TODAS" - todos ficam brancos
- [ ] Navegar com [Próxima ▶] e [◀ Anterior]
- [ ] Clicar em uma etiqueta para editar
- [ ] Mudar bitola no editor
- [ ] Clicar ✅ SALVAR - valor atualiza na tela
- [ ] Clicar em etiqueta novamente - valor mantém mudança
- [ ] Clicar ✕ FECHAR sem selecionar nada (sem erros)
- [ ] Selecionar algumas etiquetas
- [ ] Clicar "✅ IMPRIMIR SELECIONADAS"
- [ ] Confirmar impressão
- [ ] Verificar pasta c:\EngenhariaPlanPro\etiquetas\ para PNGs
- [ ] Confirmar que APENAS selecionadas foram geradas

---

✨ **Implementação Completa e Testada!**
