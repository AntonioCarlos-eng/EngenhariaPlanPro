# 🔧 REFERÊNCIA TÉCNICA - NOMENCLATURA EXPANDIDA

## 📌 Localização do Código

### Arquivo Principal
- **Caminho**: `c:\EngenhariaPlanPro\core\pilares_motor_dual.py`

### Funções Modificadas/Adicionadas

#### 1. `_expandir_titulos_pilares()` ⭐ NOVA
- **Linhas**: 133-185
- **Tipo**: Função auxiliar
- **Retorna**: `list[str]` (lista de nomes de pilares)
- **Entrada**: `str` (nome do pilar com possível nomenclatura expandida)

**Assinatura:**
```python
def _expandir_titulos_pilares(titulo_texto: str) -> list[str]:
    """
    Expande nomenclaturas compostas de pilares.
    
    Entrada:
        titulo_texto (str): ex "P14-P32", "P32(X2)", "P14;P32"
    
    Saída:
        list[str]: ["P14", "P15", ..., "P32"] ou ["P14"] para simples
    """
```

**Lógica Interna:**
```
Input: "P14-P32(X2)"
  ↓
Remove (X2) → "P14-P32"
  ↓
Detecta "-" (intervalo)
  ↓
Extrai números: 14, 32
  ↓
Gera range: 14, 15, 16, ..., 32
  ↓
Formata: ["P14", "P15", ..., "P32"]
  ↓
Output: 19 elementos
```

**Padrões Suportados:**
```python
# Padrão 1: Intervalo
if '-' in titulo:
    # P14-P32 → [P14, P15, ..., P32]
    
# Padrão 2: Separado
elif ';' in titulo or '/' in titulo:
    # P14;P32 → [P14, P32]
    # P14/P32 → [P14, P32]
    
# Padrão 3: Simples
else:
    # P1 → [P1]
    # P10 → [P10]
```

#### 2. `_motor_completo_tabelas()` ⭐ MODIFICADA
- **Linhas**: 185-380
- **O que mudou**: Adicionado bloco de expansão (linhas 370-380)

**Mudanças Específicas:**

```python
# ANTES (linhas anteriores):
for idx, title in enumerate(titles_sorted):
    # ... processar título uma vez
    entries.append(entry)

# DEPOIS (novo bloco nas linhas 370-380):
# NOVO: Expandir títulos com nomenclatura especial
titulos_expandidos = _expandir_titulos_pilares(title["nome"])

if len(titulos_expandidos) > 1:
    # Replicar dados para cada pilar expandido
    for titulo_expandido in titulos_expandidos:
        for entrada_original in linhas_por_posicao.values():
            # ... replica com titulo_expandido
            entries.append((titulo_expandido, ...))
else:
    # Nomenclatura simples, adiciona normalmente
    for entry in linhas_por_posicao.values():
        entries.append(entry)
```

**Fluxo Completo:**
```
_motor_completo_tabelas(raw_tokens, table_titles)
    ↓
for each title in table_titles:
    ↓
    [Detectar colunas: POS, BIT, QUANT, COMP]
    ↓
    [Processar linhas da seção]
    ↓
    linhas_por_posicao = {...}
    ↓
    ✨ NEW: titulos_expandidos = _expandir_titulos_pilares(title["nome"])
    ↓
    if len(titulos_expandidos) > 1:  # Houve expansão
        for each pilar_expandido in titulos_expandidos:
            for each linha in linhas_por_posicao:
                entries.append((pilar_expandido, dados_linha))
    else:  # Nomenclatura simples
        for each linha in linhas_por_posicao:
            entries.append(linha)
    ↓
return entries
```

## 🧬 Estrutura de Dados

### Input para `_expandir_titulos_pilares()`
```python
titulo_texto: str = "P14-P32(X2)"
# ou
titulo_texto: str = "P1"
# ou
titulo_texto: str = "P14;P32"
```

### Output de `_expandir_titulos_pilares()`
```python
resultado: list[str] = ["P14", "P15", "P16", ..., "P32"]
# ou
resultado: list[str] = ["P1"]
# ou
resultado: list[str] = ["P14", "P32"]
```

### Entry gerada em `_motor_completo_tabelas()`
```python
# Antes (sem expansão):
entry = (
    nome: str,           # "P1"
    pos_key: str,        # "N1"
    bitola: float,       # 8.0
    quantidade: int,     # 12
    comprimento: float,  # 3.20
    peso: float,         # 1.92
    formato: str,        # "ESTRIBO (12)"
    medidas: list        # [0.25, 0.40]
)

# Depois (com expansão):
# Mesma estrutura, mas nome pode ser P14, P15, ..., P32
# Cada um é uma entrada SEPARADA na tabela de romaneio
```

## 🎯 Regras de Processamento

### Regra 1: Remover Sufixos
```python
"P14-P32(X2)" → "P14-P32"  # Remove tudo após (
"P32(X3)" → "P32"           # Remove multiplicador
"P14-P32" → "P14-P32"       # Sem sufixo, mantém igual
```

### Regra 2: Detectar Padrão
```python
if '-' found:
    TIPO = "INTERVALO"
elif ';' or '/' found:
    TIPO = "SEPARADO"
else:
    TIPO = "SIMPLES"
```

### Regra 3: Expandir
```python
INTERVALO:    P14-P32 → range(14, 33) → [P14, P15, ..., P32]
SEPARADO:     P14;P32 → split(';') → [P14, P32]
SEPARADO:     P14/P32 → split('/') → [P14, P32]
SIMPLES:      P14 → [P14]
```

## 🔐 Validações Preservadas

A função `_motor_completo_tabelas()` mantém TODAS as validações:

```python
# Validação 1: Bitola válida
if not _eh_bitola_valida(bit):
    continue

# Validação 2: Comprimento razoável
if not (10 <= comp_cm <= 5000):
    continue

# Validação 3: Posição e quantidade
if not (1 <= pos <= 100 and qty > 0 and qty <= 2000):
    continue
```

**As validações ocorrem ANTES da expansão**, portanto:
- ✅ Dados inválidos são rejeitados (original)
- ✅ Dados válidos são expandidos para múltiplos pilares
- ✅ Sem comprometer integridade

## 🚨 Edge Cases Tratados

| Caso | Entrada | Saída | Behavior |
|------|---------|-------|----------|
| Intervalo simples | P14-P32 | 19 pilares | ✅ Expande |
| Intervalo + Mult | P14-P32(X2) | 19 pilares | ✅ Ignora (X2) |
| Multiplicador único | P32(X2) | 1 pilar | ✅ Remove sufixo |
| Separado ponto-vírgula | P14;P32 | 2 pilares | ✅ Separa |
| Separado barra | P14/P32 | 2 pilares | ✅ Separa |
| Simples | P1 | 1 pilar | ✅ Retorna igual |
| Vazio | "" | [] | ✅ Lista vazia |
| Mal formatado | "X14-X32" | [] | ✅ Sem P, lista vazia |
| Intervalo invertido | P32-P14 | 19 pilares | ✅ Detecção de min/max |

## 📊 Complexidade Algorítmica

### Time Complexity
- **Simples (P1)**: O(1)
- **Intervalo (P14-P32)**: O(n) onde n = número de pilares
- **Separado (P14;P32)**: O(n) onde n = número de partes
- **Pior caso**: O(100) para P1-P100

### Space Complexity
- **Simples**: O(1)
- **Intervalo (P14-P32)**: O(n) para lista de saída
- **Separado**: O(n) para lista de saída

## 🔗 Integração com Resto do Motor

```
processar_pilares()
    ↓
[DXF parsing com ezdxf]
    ↓
_motor_completo_tabelas()  ← MODIFICADO
    ↓
[Retorna lista de entries com nomes expandidos]
    ↓
AnalisadorGeometricoPilares()
    ↓
Romaneio na GUI
```

**Observação:** Expansão ocorre no nível de `_motor_completo_tabelas()`, ANTES de chegar ao analisador geométrico, garantindo que cada pilar é processado como entrada independente.

## 📝 Exemplos de Saída

### Exemplo 1: P1-P5 (intervalo simples)
```
Input:  P1-P5 (nomeclatura)
        8 barras ø10 com 3.20m (dados da tabela)

Output:
  P1: N1, 8 barras ø10, 3.20m → romaneio
  P2: N1, 8 barras ø10, 3.20m → romaneio
  P3: N1, 8 barras ø10, 3.20m → romaneio
  P4: N1, 8 barras ø10, 3.20m → romaneio
  P5: N1, 8 barras ø10, 3.20m → romaneio
  
Total: 5 linhas no romaneio
```

### Exemplo 2: P14-P32(X2) (intervalo com multiplicador)
```
Input:  P14-P32(X2) (nomenclatura)
        4 barras ø12.5 com 2.80m (dados da tabela)

Output:
  P14: N1, 4 barras ø12.5, 2.80m → romaneio
  P15: N1, 4 barras ø12.5, 2.80m → romaneio
  ...
  P32: N1, 4 barras ø12.5, 2.80m → romaneio
  
Total: 19 linhas no romaneio
```

### Exemplo 3: P14;P32 (separado)
```
Input:  P14;P32 (nomenclatura)
        6 barras ø8 com 1.50m (dados da tabela)

Output:
  P14: N1, 6 barras ø8, 1.50m → romaneio
  P32: N1, 6 barras ø8, 1.50m → romaneio
  
Total: 2 linhas no romaneio
```

## 🧪 Testes Unitários

### Arquivo: `test_nomenclatura_expandida.py`
- **Localização**: `c:\EngenhariaPlanPro\`
- **Testes**: 9 casos
- **Status**: ✅ 9/9 PASSANDO

### Casos Testados
```python
("P1", ["P1"]),
("P2", ["P2"]),
("P14-P32", [f"P{i}" for i in range(14, 33)]),
("P14-P32(X2)", [f"P{i}" for i in range(14, 33)]),
("P32(X2)", ["P32"]),
("P14;P32", ["P14", "P32"]),
("P14/P32", ["P14", "P32"]),
("P1-P5", [f"P{i}" for i in range(1, 6)]),
("P10", ["P10"]),
```

## 🎬 Demonstração

### Arquivo: `demo_nomenclatura_expandida.py`
- **Localização**: `c:\EngenhariaPlanPro\`
- **Propósito**: Mostrar processamento end-to-end
- **Execução**: `python demo_nomenclatura_expandida.py`

---

**Versão**: pilares_motor_dual.py v2.1
**Data**: 2024
**Status**: ✅ PRONTO PARA PRODUÇÃO
