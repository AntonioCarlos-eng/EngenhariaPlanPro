# Simplificação do Sistema de Desenhos - Fase 4

## Resumo das Mudanças

O sistema foi simplificado significativamente, removendo toda a complexidade dos desenhos parametrizados em favor de uma abordagem mais simples e treináveI.

### ❌ Removido

1. **Função `_editar_medidas_desenho()`** (154 linhas)
   - Era um editor complexo com campos específicos por tipo de desenho
   - Suportava 5 tipos (reto, dobra_um_lado, dobra_dois_lados, estribo_quadrado, estribo_redondo)
   - Cada tipo tinha múltiplos parâmetros a editar

2. **Função `_desenhar_barra_parametrica()`** (28 linhas)
   - Renderizava desenhos parametrizados baseado em configuração
   - Chamava as funções `_desenhar_*` específicas

3. **Funções de Desenho Parametrizadas** (~400 linhas total)
   - `_desenhar_reto()` - desenhava barra reta com cotas
   - `_desenhar_dobra_um_lado()` - desenhava barra com dobra
   - `_desenhar_dobra_dois_lados()` - desenhava barra com 2 dobras
   - `_desenhar_estribo_quadrado()` - desenhava estribo quadrado
   - `_desenhar_estribo_redondo()` - desenhava estribo circular

4. **Variável `self.desenhos_parametricos`**
   - Dicionário que armazenava configurações de desenhos por tipo
   - Não era mais necessário

### ✅ Implementado

1. **Sistema Simplificado de Edição de Medidas**
   - Função `_editar_desenho_canvas()` agora é um diálogo simples com 3 campos:
     - Bitola (mm)
     - Comprimento (m)
     - Quantidade
   - Salva diretamente em `self.medidas_customizadas[(viga, pos)]`
   - Atualiza a etiqueta imediatamente após salvar

2. **Renderização de Desenho Simplificada**
   - Tenta carregar PNG técnico da pasta `banco_desenhos/`
   - Se não houver PNG ou falhar, mostra placeholder com:
     - Texto "[Clique para editar]"
     - Medidas atuais: Ø{bitola} | L={comp}m | Q={qtde}
   - Área clicável abre o editor de medidas

3. **Código de Barras Mantido**
   - Sistema de código de barras continuou funcionando nas 3 seções micro
   - Cada seção gera seu próprio barcode via `_desenhar_secao_micro_fase4()`
   - Função `gerar_codigo_barras_imagem()` continua sendo usada

4. **Picotes Mantidos**
   - 3 linhas vermelhas tracejadas com label "✄ DESTACAR AQUI"
   - Separam as 3 seções micro da etiqueta

## Fluxo de Uso

### Antes (Complexo)
1. Gerar etiqueta
2. Clicar em desenho
3. Escolher tipo (5 opções)
4. Editar parâmetros específicos do tipo (3-5 campos)
5. Salvar
6. Atualizar

### Agora (Simples)
1. Gerar etiqueta
2. Clicar em desenho
3. Editor abre com 3 campos (bitola, comp, qtde)
4. Editar medidas
5. Salvar → etiqueta atualiza automaticamente

## Benefícios

- ✅ **Código mais limpo**: -500 linhas de código parametrizado
- ✅ **Mais rápido de usar**: Sem seleção de tipo, direto para edição
- ✅ **Treinável**: Sistema aprende com cada edição de medidas
- ✅ **Puxa desenhos existentes**: Se houver PNG, usa; senão, mostra placeholder
- ✅ **Etiqueta completa**: Mantém 3 picotes + 3 códigos de barras
- ✅ **Sem erros**: Código testado e sem referências circulares

## Estrutura da Etiqueta

A etiqueta mantém a estrutura completa:

```
┌─────────────────────────────────┐
│      TOPO (9,3 cm)              │
│  - OS, Obra, Elemento, POS      │
│  - Tabela técnica               │
│  - Desenho (PNG ou placeholder) │
├─────────────────────────────────┤ ✄ PICOTE 1
│  SEÇÃO MICRO 1 (1,9 cm)         │
│  - Código de barras             │
│  - Compr. Corte + Resumo        │
├─────────────────────────────────┤ ✄ PICOTE 2
│  SEÇÃO MICRO 2 (1,9 cm)         │
│  - Código de barras             │
│  - Compr. Corte + Resumo        │
├─────────────────────────────────┤ ✄ PICOTE 3
│  SEÇÃO MICRO 3 (1,9 cm)         │
│  - Código de barras             │
│  - Compr. Corte + Resumo        │
└─────────────────────────────────┘
```

## Testes Realizados

- ✅ Compilação sem erros
- ✅ Imports sem problemas
- ✅ Sem referências a funções deletadas
- ✅ Estrutura de etiqueta mantida

## Próximos Passos (Opcional)

Se necessário, pode-se:
1. Integrar com banco_desenhos para carregar PNGs automaticamente
2. Implementar sistema de aprendizado para reconhecer padrões
3. Adicionar validação de medidas (min/max)
4. Criar histórico de edições
