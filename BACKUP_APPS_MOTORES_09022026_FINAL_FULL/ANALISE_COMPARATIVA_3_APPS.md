# ANÁLISE COMPARATIVA: VIGAS_APP vs PILARES_APP vs LAJES_APP

## 📊 RESUMO EXECUTIVO

| Aspecto | VIGAS | PILARES | LAJES |
|---------|-------|---------|-------|
| **Tamanho** | 5,705 linhas | 5,730 linhas | 2,412 linhas |
| **Classe Principal** | `VigasApp(tk.Tk)` | `PilaresApp(tk.Tk)` | `LajesApp(tk.Tk)` |
| **Analisador Geométrico** | `AnalisadorGeometricoVigas` | `AnalisadorGeometricoPilares` | `AnalisadorGeometricoLajes` |
| **Motor/Core** | `core.vigas_motor_v2` | `core.pilares_motor_dual` + fallback | `core.lajes_motor` |
| **Status** | ✅ COMPLETO | ✅ COMPLETO | ⚠️ SIMPLIFICADO |
| **Data Última Modificação** | 01/02/2026 | 03/02/2026 | 24/11/2025 |

---

## 🏗️ ESTRUTURA DE CLASSES

### 1. VIGAS_APP
```
AnalisadorGeometricoVigas
├─ identificar_tipo_viga(pos, bitola, comp)
├─ calcular_medidas_estribo_viga()
├─ calcular_medidas_negativo()
├─ calcular_medidas_positivo()
├─ calcular_medidas_dobra_duas_pontas()
├─ calcular_medidas_dobra_uma_ponta()
├─ calcular_medidas_barra_u()
├─ calcular_medidas_barra_z()
├─ calcular_medidas_cavalete()
├─ calcular_medidas_grampo()
└─ calcular_medidas_tres_segmentos()

VigasApp(tk.Tk)
├─ __init__()
├─ _criar_interface()
├─ selecionar_arquivos()
├─ processar() / processar_v2()
├─ gerar_romaneio()
├─ gerar_romaneio_conferencia()
├─ imprimir_etiquetas()
├─ desenhar_etiquetas_com_selecao()
├─ _marcar_todas_etiquetas()
├─ _desmarcar_todas_etiquetas()
└─ ... [130+ métodos]
```

### 2. PILARES_APP
```
AnalisadorGeometricoPilares
├─ identificar_tipo_pilar(pos, bitola, comp)
├─ calcular_medidas_estribo_pilar()
├─ calcular_medidas_negativo()
├─ calcular_medidas_positivo()
├─ calcular_medidas_dobra_duas_pontas()
├─ calcular_medidas_dobra_uma_ponta()
├─ calcular_medidas_barra_u()
├─ calcular_medidas_barra_z()
├─ calcular_medidas_tres_segmentos()
├─ calcular_medidas_cavalete()
└─ calcular_medidas_grampo()

PilaresApp(tk.Tk)
├─ __init__()
├─ _criar_interface()
├─ selecionar_arquivos()
├─ processar() / processar_v2()
├─ gerar_romaneio()
├─ gerar_romaneio_conferencia()
├─ imprimir_etiquetas()
├─ desenhar_etiquetas_com_selecao()
├─ _marcar_todas_etiquetas()
├─ _desmarcar_todas_etiquetas()
└─ ... [130+ métodos]
```

### 3. LAJES_APP
```
AnalisadorGeometricoLajes
├─ identificar_tipo_laje(pos, bitola, comp, formato_dobra)
└─ [MÍNIMO - apenas fallback]

LajesApp(tk.Tk)
├─ __init__()
├─ _criar_interface()
├─ selecionar_arquivos()
├─ processar()
├─ gerenciar_producao()
├─ gerar_romaneio()
├─ gerar_romaneio_conferencia()
├─ imprimir_etiquetas()
├─ salvar_planilhamento()
├─ carregar_planilhamento()
└─ ... [50+ métodos]
```

---

## 📥 IMPORTAÇÕES DE CORE

### VIGAS
```python
try:
    from core.vigas_motor_v2 import processar_vigas
except Exception:
    pass

try:
    from core.etiquetas_generator import GeradorEtiquetasDinamico
except Exception:
    pass

try:
    from core.etiquetas_helper import (
        gerar_codigo_identificador,
        gerar_codigo_barras_imagem,
        localizar_desenho_barra,
        carregar_desenho_redimensionado,
        formatar_os_numero,
    )
except Exception:
    pass

try:
    from core.etiquetas_layout_config import (
        PX_MM, MARGEM_EXTERNA_MM, TOPO_ALTURA_MM, ...
    )
except Exception:
    pass
```

### PILARES
```python
try:
    from core.pilares_motor_dual import processar_pilares
except Exception:
    try:
        from core.pilares_motor import processar_pilares
    except Exception:
        pass
# ... (mesmo padrão de etiquetas_generator, etiquetas_helper, etc)
```

### LAJES
```python
from core.lajes_motor import processar_lajes, analisar_barra_geometricamente, BITOLAS_VALIDAS

try:
    from core.etiquetas_generator import GeradorEtiquetasDinamico
except Exception:
    GeradorEtiquetasDinamico = None
```

---

## 🎨 INTERFACE GRÁFICA

### Semelhanças
- ✅ Mesmo design verde/laranja
- ✅ Estrutura Tkinter com Frame/Label/Button/Treeview
- ✅ Botões: Selecionar, Processar, Romaneio, Check List, Etiquetas, Exportar Excel, Limpar
- ✅ Status bar na base com informações

### Diferenças
| VIGAS | PILARES | LAJES |
|-------|---------|-------|
| Botão duplo: "Processar" + "Processar 2.0" | Botão duplo: "Processar" + "Processar 2.0" | Botão simples: "Processar" |
| 6 botões de ação | 6 botões de ação | 7 botões (+ "Gerenciar Produção") |
| TreeView 9 colunas | TreeView 9 colunas | TreeView 9 colunas |
| - | - | 💾 Salvar/Carregar Planilha (persistência) |

---

## 📋 DADOS E ESTRUTURAS

### VIGAS & PILARES
```python
# Padrão (6 campos vistos na árvore)
(elemento, pos, bitola, qtde, comp_m, peso, formato, desenho, estribo_lados)
```

### LAJES
```python
# Padrão com 9 campos (compatível com vigas/pilares)
(elemento, pos, bitola, qtde_area, comp_m, largura_m, peso_kg, formato_dobra, medidas_m)
```

**Diferença Chave**: LAJES tem campo `largura_m` que pode ser:
- `float` (número em metros) = NORMAL
- `string` (texto "VARIÁVEL", "TELA", etc) = VARIÁVEL

---

## ⚙️ PROCESSAMENTO (MOTOR)

### VIGAS
- **Rápido**: `processar_vigas()` - extração básica
- **Completo**: `processar_v2()` - análise geométrica expandida
- Motor: `core.vigas_motor_v2`

### PILARES
- **Dual Mode**: Tenta `pilares_motor_dual` (Rápido + Completo) → fallback `pilares_motor`
- Mesmo padrão de interface (Processar + Processar 2.0)
- Motor: `core.pilares_motor_dual` (preferência) ou `core.pilares_motor`

### LAJES
- **Simples**: Um único `processar()` 
- Usa `core.lajes_motor.processar_lajes()`
- ⚠️ Não tem modo "Completo" (V2)
- **Novo**: Gerenciar Produção (filtro de lajes ativas)
- **Novo**: Persistência (JSON) - salva/carrega planilhamento

---

## 🏷️ ETIQUETAS & ROMANEIO

### Métodos Similares
- ✅ `imprimir_etiquetas()` - Abre editor de etiquetas
- ✅ `gerar_romaneio()` - Gera HTML/PDF com lista de barras
- ✅ `gerar_romaneio_conferencia()` - Check list interativo
- ✅ `desenhar_etiquetas_com_selecao()` - Renderização no canvas
- ✅ `_marcar_todas_etiquetas()` / `_desmarcar_todas_etiquetas()`

### Diferenças
| VIGAS | PILARES | LAJES |
|-------|---------|-------|
| Etiquetas com bloco OS | Etiquetas com bloco OS | ⚠️ (métodos existem mas podem não estar totalmente implementados) |
| Pickle de romaneio | Pickle de romaneio | JSON (nova abordagem) |
| - | - | Filtro de lajes ativas |

---

## 💾 PERSISTÊNCIA

### VIGAS & PILARES
- Padrão Pickle (`.pkl` de romaneio, `.state`)
- Checkboxes de etiquetas

### LAJES
- **JSON** para tudo:
  - `lajes_planilhamento_editado.json` - Dados processados
  - `lajes_checklist_state.json` - Estado (obra, pavimento, lajes ativas, status checklist)
- Métodos: `salvar_planilhamento()`, `carregar_planilhamento()`
- Métodos: `salvar_estado_persistencia()`, `carregar_estado_persistencia()`

---

## 🔧 FUNCIONALIDADES ÚNICAS

### VIGAS
- Análise geométrica expandida com 10+ tipos de dobras
- Motor dual (Rápido vs Completo)
- Gerador de código de barras
- Helper de etiquetas

### PILARES
- Motor dual com fallback automático
- Mesmo suporte a análise expandida que VIGAS
- Praticamente idêntico a VIGAS (mesma template)

### LAJES
- **Persistência JSON** (mais moderno que Pickle)
- **Gerenciar Produção** - Filtro de lajes ativas em checkboxes
- Compatibilidade com campo `largura_m` (NORMAL/VARIÁVEL)
- Análise simplificada (sem método completo de cálculo de medidas)
- Menos métodos auxiliares (50 vs 130+)

---

## ⚠️ PROBLEMAS IDENTIFICADOS

### LAJES
1. **Analisador geométrico minimal** - Apenas 1 método (falta calcular_medidas_*)
2. **Sem modo "Processar 2.0"** - Não tem análise completa como vigas/pilares
3. **Motor pode estar incompleto** - `core.lajes_motor` pode ter limitações
4. **Métodos de etiqueta podem estar pendentes** - Estrutura existe mas implementação pode estar vazia

### VIGAS & PILARES
1. Ainda usam Pickle (menos moderno)
2. Não têm filtro de "lajes ativas" (mais simples = menos funcionalidade)

---

## 📊 COMPARAÇÃO DE LINHAS DE CÓDIGO

```
VIGAS:    5,705 linhas (100%)
PILARES:  5,730 linhas (100%)  ← Ligeiramente maior
LAJES:    2,412 linhas (42%)   ← Menos da metade (pode estar incompleto)
```

**Conclusão**: LAJES é bastante mais simples/menor. Pode estar em estado anterior de desenvolvimento.

---

## ✅ RECOMENDAÇÕES

1. **Expandir LAJES para ter** os mesmos métodos de `AnalisadorGeometricoLajes` que VIGAS/PILARES
2. **Adicionar modo "Processar 2.0"** se o motor `lajes_motor` suportar
3. **Considerar usar JSON** também em VIGAS/PILARES (modernizar)
4. **Testar métodos de etiqueta** em LAJES para garantir que funcionam
5. **Manter coerência**: Se VIGAS=PILARES em padrão, LAJES deve ser também

---

**Análise Data**: 04/02/2026
**Arquivo Analisado**: vigas_app.py, pilares_app.py, lajes_app.py
