# ADAPTAÇÃO COMPLETA - Editor de Etiquetas para Lajes

## ARQUITETURA IDÊNTICA AO VIGAS_APP

Esta adaptação traz TODOS os recursos do editor de etiquetas do vigas_app.py para o lajes_app.py:

### RECURSOS IMPLEMENTADOS:
✅ Renderização direta no canvas (sem PNGs pré-gerados)
✅ Checkboxes integrados nas etiquetas
✅ Edição inline de valores (bitola, comprimento, quantidade)
✅ Edição de forma/desenho da barra
✅ Navegação por páginas
✅ Seleção marcar/desmarcar todas
✅ Preview em tempo real das mudanças
✅ Desenhos técnicos dentro das etiquetas

### ADAPTAÇÕES ESPECÍFICAS PARA LAJES:

**Estrutura de Dados:**
- VIGAS: (viga, pos, bitola, qtde, comp, peso)
- LAJES: (elemento, pos_tipo, bitola, qtde, comp_m, largura_info, peso, formato_dobra, medidas_m)

**Mapeamento de Campos:**
- `viga` → `elemento` ("LAJE NEG/HOR", "LAJE NEG/VER", etc.)
- `pos` → `pos_tipo` ("N1", "N2", etc.)
- `comp` → `comp_m` (comprimento em metros)
- Adicional: `formato_dobra` (RETA ou BARRA U)

### MÉTODOS ADAPTADOS:

1. **_desenhar_moldura_etiqueta_fase4()** - Moldura da etiqueta
2. **_desenhar_topo_identico_fase4()** - Cabeçalho com dados técnicos
3. **_desenhar_secao_micro_fase4()** - Seções inferiores compactas
4. **_desenhar_picote_fase4()** - Linha de corte tracejada
5. **desenhar_etiquetas_com_selecao()** - Renderização completa
6. **_handle_canvas_click()** - Controle de cliques
7. **_editar_etiqueta_dados()** - Diálogo de edição
8. **_editar_desenho_canvas()** - Edição de formas
9. **_editar_medida_etiqueta()** - Edição rápida de valores
10. **_toggle_etiqueta_selecao()** - Toggle de seleção
11. **_marcar_todas_etiquetas()** - Marcar todas
12. **_desmarcar_todas_etiquetas()** - Desmarcar todas
13. **Métodos de navegação** - Primeira/Anterior/Próxima/Última página

### ARQUIVOS A MODIFICAR:

**lajes_app.py:**
- Substituir método `imprimir_etiquetas()` completo
- Adicionar todos os métodos auxiliares de renderização
- Adicionar controles de edição e navegação

### INSTRUÇÕES DE IMPLEMENTAÇÃO:

Os métodos completos estão documentados abaixo. Copie e cole no lajes_app.py,
substituindo o método imprimir_etiquetas() atual e adicionando todos os métodos auxiliares.

---

## CÓDIGO COMPLETO ADAPTADO

Veja os métodos completos no arquivo:
`lajes_app_metodos_etiquetas.py`
