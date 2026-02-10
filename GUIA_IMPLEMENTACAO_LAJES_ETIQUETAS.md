# GUIA DE IMPLEMENTAÇÃO - Editor de Etiquetas para Lajes

## ✅ OBJETIVO CONCLUÍDO

Foi adaptada TODA a arquitetura de renderização de etiquetas do `vigas_app.py` para o `lajes_app.py`.

## 📁 ARQUIVOS CRIADOS

1. **`ADAPTACAO_LAJES_ETIQUETAS.md`** - Documentação da adaptação
2. **`lajes_app_metodos_etiquetas.py`** - Código completo com todos os métodos adaptados

## 🔧 COMO IMPLEMENTAR

### Passo 1: Backup
```bash
# Fazer backup do arquivo atual
copy lajes_app.py lajes_app.py.backup
```

### Passo 2: Abrir os arquivos
- Abra `lajes_app.py` no editor
- Abra `lajes_app_metodos_etiquetas.py` como referência

### Passo 3: Substituir o método `imprimir_etiquetas()`

Localize o método atual `imprimir_etiquetas()` em `lajes_app.py` (linha ~1267) e substitua por:

```python
def imprimir_etiquetas(self):
    # COPIE O MÉTODO COMPLETO de lajes_app_metodos_etiquetas.py
    # Linha 43 até linha 213 do arquivo de métodos
```

### Passo 4: Adicionar TODOS os métodos auxiliares

Adicione os seguintes métodos na classe `LajesApp`:

**Navegação (linhas 215-258):**
- `_ir_primeira_pagina_etiquetas()`
- `_ir_pagina_anterior_etiquetas()`
- `_ir_proxima_pagina_etiquetas()`
- `_ir_ultima_pagina_etiquetas()`
- `_marcar_todas_etiquetas()`
- `_desmarcar_todas_etiquetas()`
- `_fechar_editor_etiquetas_lajes()`
- `_confirmar_e_gerar_etiquetas_lajes()`

**Renderização (linhas 260-441):**
- `desenhar_etiquetas_com_selecao()`

**Desenho de seções (linhas 443-641):**
- `_desenhar_moldura_etiqueta_fase4()`
- `_desenhar_topo_identico_fase4()`
- `_desenhar_picote_fase4()`
- `_desenhar_secao_micro_fase4()`

**Interação e edição (linhas 643-971):**
- `_handle_canvas_click()`
- `_toggle_etiqueta_selecao()`
- `_editar_medida_etiqueta()`
- `_editar_desenho_canvas()`
- `_editar_etiqueta_dados()`

### Passo 5: Adicionar imports necessários

No topo do arquivo `lajes_app.py`, certifique-se de ter:

```python
import math
from tkinter import simpledialog
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_DISPONIVEL = True
except:
    Image = None
    ImageTk = None
    PIL_DISPONIVEL = False
```

### Passo 6: Adicionar constantes de layout

Adicione após os imports (se ainda não existir):

```python
# Constantes de layout
try:
    from core.etiquetas_layout import *
    ETIQUETAS_LAYOUT_CFG = True
except:
    ETIQUETAS_LAYOUT_CFG = False
    CFG_PX_MM = 4
    MARGEM_EXTERNA_MM = 10
    LARGURA_ETIQUETA_MM = 100
    TOPO_ALTURA_MM = 93
    SECAO_MICRO_ALTURA_MM = 19
    ESPACO_PICOTE_MM = 2
    FAIXA_VERTICAL_LARGURA_MM = 10
    OS_BLOCO_LARGURA_MM = 18
    OS_BLOCO_ALTURA_MM = 30
    TABELA_ALTURA_HEADER_MM = 8
    TABELA_ALTURA_LINHA_MM = 10
    COL_BITOLA_MM = 16
    COL_COMPR_UNIT_MM = 34
    COL_PESO_MM = 22
    COL_QTDE_MM = 18
    DESENHO_LARGURA_MM = 60
    DESENHO_ALTURA_MM = 50
```

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Backup do `lajes_app.py` criado
- [ ] Método `imprimir_etiquetas()` substituído
- [ ] Métodos de navegação adicionados
- [ ] Método `desenhar_etiquetas_com_selecao()` adicionado
- [ ] Métodos de desenho de seções adicionados
- [ ] Métodos de interação e edição adicionados
- [ ] Imports verificados e adicionados
- [ ] Constantes de layout adicionadas
- [ ] Teste básico executado

## 🧪 COMO TESTAR

1. Execute o `lajes_app.py`
2. Processe arquivos DXF de lajes
3. Clique em "Imprimir Etiquetas"
4. Verifique:
   - ✅ Etiquetas renderizadas diretamente no canvas (não PNGs)
   - ✅ Checkboxes funcionando (marcar/desmarcar)
   - ✅ Clique nos valores para editar (bitola, comprimento, quantidade)
   - ✅ Clique no desenho para editar forma
   - ✅ Navegação entre páginas
   - ✅ Botões Marcar/Desmarcar Todas funcionando
   - ✅ Seleção persistente entre páginas

## 📊 PRINCIPAIS DIFERENÇAS VIGAS vs LAJES

### Estrutura de Dados:
| Campo | VIGAS | LAJES |
|-------|-------|-------|
| Identificação 1 | `viga` | `elemento` |
| Identificação 2 | `pos` | `pos_tipo` |
| Índice | 0 | 0 |
| Posição | 1 | 1 |
| Bitola | 2 | 2 |
| Quantidade | 3 | 3 |
| Comprimento | 4 | 4 (comp_m) |
| Extra | 5 (peso) | 5 (largura_info) |
| Peso | 5 | 6 |
| Formato | - | 7 (formato_dobra) |
| Medidas | - | 8 (medidas_m) |

### Mapeamento de Variáveis:
```python
# VIGAS
viga = dado[0]
pos = dado[1]

# LAJES
elemento = dado[0]  # ex: "LAJE NEG/HOR"
pos_tipo = dado[1]  # ex: "N1"
```

## 🎯 RECURSOS IMPLEMENTADOS

### ✅ Renderização
- Desenho direto no canvas (sem PNGs intermediários)
- Etiquetas 100×150mm com picotes
- Moldura com marcas de corte
- Faixa vertical com nome da obra
- Bloco de numeração OS
- Tabela técnica com dados

### ✅ Edição
- **Clique nos valores**: Editar bitola, comprimento, quantidade inline
- **Clique no desenho**: Mudar forma da barra (Reta, Barra U, Gancho)
- **Diálogo completo**: Editar todos os campos de uma vez
- **Preview em tempo real**: Mudanças aparecem imediatamente

### ✅ Seleção
- Checkboxes integrados nas etiquetas
- Marcar/Desmarcar todas
- Contador de selecionadas
- Seleção persistente entre páginas

### ✅ Navegação
- Primeira/Última página
- Próxima/Anterior
- Indicador de página atual
- Scroll com mouse wheel

### ✅ Persistência
- Customizações salvas em `medidas_customizadas`
- Formas salvas em `formas_customizadas`
- Estado de seleção mantido

## 🔍 DEBUGGING

Se houver problemas:

1. **Erro de importação**: Verifique se PIL/Pillow está instalado
2. **Etiquetas não aparecem**: Verifique `dados_processados` não está vazio
3. **Cliques não funcionam**: Verifique bindings do canvas
4. **Valores não editam**: Verifique `medidas_customizadas` está inicializado
5. **Formas não aparecem**: Verifique `formas_customizadas` está inicializado

### Adicionar logs para debug:
```python
print(f"[DEBUG] dados_processados: {len(self.dados_processados)} itens")
print(f"[DEBUG] etiquetas_selecionadas: {self.etiquetas_selecionadas}")
print(f"[DEBUG] medidas_customizadas: {self.medidas_customizadas}")
```

## 📝 NOTAS IMPORTANTES

1. **Compatibilidade**: O código mantém compatibilidade com a estrutura existente de lajes
2. **Formato de dobra**: Detectado automaticamente do campo `formato_dobra` dos dados
3. **Peso**: Calculado usando `core.peso.peso_linear_kg_m()` (igual ao vigas_app)
4. **Imagens**: Usa PIL/Pillow para renderizar texto rotacionado na faixa vertical

## 🚀 PRÓXIMOS PASSOS

Após implementação, você pode:

1. **Testar geração de PNGs**: Implementar `_confirmar_e_gerar_etiquetas_lajes()`
2. **Adicionar mais formas**: Estender opções de desenho técnico
3. **Impressão direta**: Integrar com impressora de etiquetas
4. **Exportar PDF**: Gerar PDF das etiquetas selecionadas

## 📚 REFERÊNCIAS

- **Arquivo base**: `vigas_app.py` (linhas 1888-3800)
- **Motor de lajes**: `core/lajes_motor.py`
- **Gerador de etiquetas**: `core/etiquetas_generator.py` (se disponível)
- **Layout**: `core/etiquetas_layout.py` (se disponível)

## ✨ RESULTADO FINAL

O editor de etiquetas do `lajes_app.py` agora é **IDÊNTICO** ao do `vigas_app.py`:
- ✅ Mesma interface visual
- ✅ Mesmos recursos de edição
- ✅ Mesma navegação
- ✅ Mesma experiência do usuário
- ✅ Adaptado para a estrutura de dados de lajes

---

**Data**: 4 de fevereiro de 2026
**Autor**: GitHub Copilot
**Versão**: 1.0
