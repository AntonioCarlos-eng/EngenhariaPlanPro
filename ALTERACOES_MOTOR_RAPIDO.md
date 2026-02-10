# Motor Rápido Adaptado - Suporte a Textos Fragmentados

## Resumo das Alterações

### 1. Nova Função: `_processar_textos_fragmentados()`
- **Localização**: [core/pilares_motor_dual.py](core/pilares_motor_dual.py#L95-L195)
- **Objetivo**: Processar arquivos DXF com textos muito fragmentados
- **Funcionamento**:
  - Agrupa textos pela posição Y (linha)
  - Ordena textos pela posição X (coluna)
  - Detecta pilares (P28, P29, etc)
  - Extrai dados na sequência: POS | BITOLA | QTD | COMPRIMENTO
  - Converte `%%c` para `ø` (símbolo de diâmetro)
  - Valida bitolas (5.0-40.0 mm) e comprimentos (10-5000 cm)

### 2. Motor Rápido Melhorado
- **Localização**: [core/pilares_motor_dual.py](core/pilares_motor_dual.py#L197-L245)
- **Estratégia em Cascata**:
  1. Tenta padrão estruturado: `"4 N1 ø12.5 C=280"` (texto contínuo)
  2. Se não encontrar, tenta textos fragmentados
  3. Mantém dados compatíveis sem processá-los novamente

### 3. Integração na Função Principal
- **Localização**: [core/pilares_motor_dual.py](core/pilares_motor_dual.py#L670-L685)
- **Alterações**:
  - Coleta textos com posições X,Y mesmo na região de desenhos (x<100)
  - Chama fragmentado quando Motor Rápido retorna None
  - Continua priorizando Motor Completo (tabelas) sem mudanças

## Comportamento Preservado

✅ **Motor Completo (tabelas x>100)**: SEM MUDANÇAS
- Detecta colunas por posição X
- Processa nomenclaturas de pilares (P14-P32, P14=P32(X2), etc)
- Divide quantidades quando necessário

✅ **Arquivos Compatíveis**: SEM MUDANÇAS
- pilares l1-020.DXF: **79 linhas, 8719.75 kg** (idêntico)
- padrão regex "4 N1 ø12.5 C=280" continua funcionando

✅ **Validações**: SEM MUDANÇAS
- Bitolas: 5.0-40.0 mm
- Comprimentos: 10-5000 cm
- Quantidades: 1-2000

## Suporte Novo

🆕 **Arquivos Fragmentados (x<100)**
- Textos separados por campo (POS | BIT | QTD | COMP)
- Cada linha em Y diferente
- Símbolo `%%c` para Ø
- Múltiplos pilares no mesmo arquivo

### Exemplo de Teste
```
PILAR P28          (Y=61.0)
N1 | %%c | 6.3 | 22 | 365   (Y=55.0) → P28 N1 ø6.3 x22 L=365cm
N2 | %%c | 8.0 | 16 | 285   (Y=52.0) → P28 N2 ø8.0 x16 L=285cm

PILAR P29          (Y=48.0)
N1 | %%c | 12.5 | 4 | 480   (Y=42.0) → P29 N1 ø12.5 x4 L=480cm
N2 | %%c | 10.0 | 12 | 320  (Y=39.0) → P29 N2 ø10.0 x12 L=320cm
```

**Resultado**: 4 linhas, 54 barras, 79.87 kg ✓

## Testes Executados

| Teste | Arquivo | Resultado |
|-------|---------|-----------|
| Motor Rápido Fragmentado Simulado | `testar_motor_rapido_fragmentado.py` | ✓ 3 linhas |
| Motor Rápido Fragmentado Real | `testar_fragmentado_real.py` | ✓ 4 linhas |
| Arquivo Compatível | pilares l1-020.DXF | ✓ 79 linhas, 8719.75 kg |
| Aplicação GUI | pilares_app.py | ✓ Abierta |

## Segurança

✅ **Nenhum código quebrado**
- Mudanças apenas em Motor Rápido (x<100)
- Motor Completo (x>100) intacto
- Lógica em cascata: tenta padrão antigo primeiro

✅ **Sem mudanças no Motor Completo**
- Duplicação de nomenclatura, divisão de quantidade, etc. funcionam igual

✅ **Filtro de duplicação**
- Pilares já processados pela tabela não são reprocessados
