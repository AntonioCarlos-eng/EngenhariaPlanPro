# GUIA DE USO - SISTEMA DE ETIQUETAS PNG

## RESUMO EXECUTIVO

O sistema agora **gera automaticamente etiquetas em PNG** durante o processamento do DXF. Essas etiquetas são **completas e formatadas** (10x15cm) e ficam prontas para impressão ou visualização.

**Resultado**: Nenhum mais "PNG NAO ENCONTRADO" ✓


## FLUXO DE USO

### 1. SELECIONAR ARQUIVOS DXF
```
1. Clique em "📁 Selecionar Arquivos"
2. Selecione um ou mais arquivos .DXF ou .DWG
3. Arquivos aparecerao na lista
```

### 2. PROCESSAR ARQUIVO
```
1. Clique em "⚙️ PROCESSAR 2.0"
   - Sistema converte para ACAD2018
   - Processa dados com motor_v2()
   - ✨ GERA AUTOMATICAMENTE as etiquetas PNG
   
2. Mensagem: "Processamento DXF 2.0 concluido!"
   - Total de barras é exibido
   - Etiquetas já estão criadas e salvas
```

### 3. VISUALIZAR/IMPRIMIR ETIQUETAS
```
1. Clique em "🏷️ Etiquetas"
   - Sistema carrega os PNGs pre-gerados
   - Exibe preview da etiqueta
   - Nenhum erro "PNG NAO ENCONTRADO"

2. Opcoes:
   - Preview: Visualiza uma etiqueta
   - Print: Imprime todas ou um intervalo
   - Salvar: Exporta em diferentes formatos
```


## EXEMPLO PRATICO

### Entrada: Arquivo DXF
```
#vigas t1-069.DXF
└─ 7 vigas diferentes
└─ 69 posicoes/barras
```

### Processamento Automatico
```
[OK] Processados 69 registros de barras
   Total: 590 barras, 758.35 kg

[OK] Gerando etiquetas PNG...
[OK] Etiqueta 1/69 salva: ETIQUETA_V301_N1_b10.0_q3_c255cm_0001.png
[OK] Etiqueta 2/69 salva: ETIQUETA_V301_N2_b10.0_q2_c435cm_0002.png
[OK] Etiqueta 3/69 salva: ETIQUETA_V301_N3_b10.0_q1_c220cm_0003.png
... (66 etiquetas restantes)
[OK] Etiqueta 69/69 salva: ETIQUETA_V309_N11_b5.0_q67_c141cm_0069.png

[OK] Total de etiquetas geradas: 69
```

### Saida: PNGs Completos
```
C:\EngenhariaPlanPro\etiquetas\
├─ ETIQUETA_V301_N1_b10.0_q3_c255cm_0001.png        (103 KB)
├─ ETIQUETA_V301_N2_b10.0_q2_c435cm_0002.png        (103 KB)
├─ ETIQUETA_V301_N3_b10.0_q1_c220cm_0003.png        (103 KB)
...
└─ ETIQUETA_V309_N11_b5.0_q67_c141cm_0069.png       (103 KB)

Total: 69 arquivos, 7.1 MB
```

### Cada PNG Contem:
```
[ETIQUETA COMPLETA 10x15cm @ 300 DPI]

┌─────────────────────────────────────┐
│  ┌─ Borda Laranja (#ff6f00)         │
│  │ ┌───────┐                        │
│  │ │   OS  │  OBRA 001              │
│  │ │ 1-69  │  V301                  │
│  │ │       │  POS: N1 (GRANDE)      │
│  │ ├──────────────────────────────┤ │
│  │ │ Bitola  │ 10.0                │ │  ← Tabela de dados
│  │ │ Comp.   │ 2.550m              │ │
│  │ │ Peso    │ 12.5 kg             │ │
│  │ │ Qtde    │ 3                   │ │
│  │ ├──────────────────────────────┤ │
│  │ │         DESENHO TECNICO       │ │  ← Area para desenho
│  │ │      (PNG da barra)            │ │
│  │ │       PAGINA 1 DE 69           │ │
│  │ ├──────────────────────────────┤ │
│  │ │ PICOTE 1: cortar aqui ✂️       │ │  ← 3 Picotes identicos
│  │ │ Elem: V301  N1  Ø 10.0        │ │
│  │ │ Compr. Corte: 2.550           │ │
│  │ ├──────────────────────────────┤ │
│  │ │ PICOTE 2: cortar aqui ✂️       │ │
│  │ │ ...                            │ │
│  │ ├──────────────────────────────┤ │
│  │ │ PICOTE 3: cortar aqui ✂️       │ │
│  │ │ ...                            │ │
│  │ └───────────────────────────────┘ │
└─────────────────────────────────────┘

Resoluacao: 1181 x 1771 pixels
DPI: 300 x 300 (pronto para impressao)
Tamanho arquivo: ~103 KB
```


## ESPECIFICACOES TECNICAS

### Dimensoes
- Largura: 100 mm (10 cm)
- Altura: 150 mm (15 cm)
- Proporcao: 2:3 (paisagem vertical)

### Resolucao
- DPI: 300 x 300 (padrao para impressoras)
- Dimensoes em pixels: 1181 x 1771
- Arquivo: ~103 KB por etiqueta

### Formato
- Tipo: PNG (lossless)
- Modo: RGB (8-bit)
- Compressao: Padrao ZIP

### Nomenclatura dos Arquivos
```
ETIQUETA_{viga}_{pos}_b{bitola}_q{qtde}_c{comp_cm}cm_{idx}.png

Exemplo:
ETIQUETA_V301_N1_b10.0_q3_c255cm_0001.png
         │    │   │      │ │        │
         │    │   │      │ │        └─ Indice sequencial (0001-9999)
         │    │   │      │ └───────── Comprimento em cm
         │    │   │      └──────────── Quantidade
         │    │   └─────────────────── Bitola (diametro)
         │    └────────────────────── Posicao
         └─────────────────────────── Nome da viga
```

### Pasta de Armazenamento
```
C:\EngenhariaPlanPro\etiquetas\

Auto-detectada durante:
1. Processamento DXF (cria GeradorEtiquetasDinamico)
2. Visualizacao de etiquetas (procura PNGs)
```


## DADOS DE TESTE

**Arquivo de teste**: `#vigas t1-069.DXF`

### Vigas Processadas
- V301: 15 posicoes
- V302: 15 posicoes
- V304: 10 posicoes
- V305: 5 posicoes
- V306: 6 posicoes
- V307 (multipla): 7 posicoes
- V309: 11 posicoes

**Total: 69 etiquetas unicas**

### Dados Agregados
- Total de barras: 590
- Peso total: 758.35 kg
- Bitolas: 5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0 mm
- Comprimentos: 85 cm a 960 cm
- Quantidades: 1 a 92 barras por posicao


## RESOLUCAO DE PROBLEMAS

### Problema: "PNG NAO ENCONTRADO"
**Causa**: Etiqueta nao foi gerada durante processamento
**Solucao**:
1. Verifique se "⚙️ PROCESSAR 2.0" foi clicado (nao "⚙️ PROCESSAR")
2. Verifique pasta: `C:\EngenhariaPlanPro\etiquetas\`
3. Procure arquivo com padrão: `ETIQUETA_*_b*.png`
4. Se nao existir, reprocesse o arquivo

### Problema: Erro ao gerar etiquetas
**Causa**: Falta de permissao na pasta ou disco cheio
**Solucao**:
1. Verifique permissoes: `C:\EngenhariaPlanPro\etiquetas\`
2. Verifique espaco em disco (precisa ~7-10 MB)
3. Feche outros programas que possam estar usando a pasta
4. Tente novamente

### Problema: Etiqueta vazia/branca
**Causa**: PNG foi gerado mas sem dados
**Solucao**:
1. Verifique dados do DXF (procure tabelas com dados)
2. Reprocesse o arquivo
3. Verifique console para mensagens de erro


## ARQUIVOS RELACIONADOS

### Principais
- `vigas_app.py` - Aplicacao principal (linhas 693-710, 3418-3463)
- `core/etiquetas_generator.py` - Gerador de PNGs (linhas 140-310)
- `core/etiquetas_helper.py` - Funcoes auxiliares
- `core/vigas_motor_v2.py` - Motor de processamento

### Testes
- `teste_fluxo_etiquetas.py` - Teste de geracao
- `teste_carregar_etiqueta.py` - Teste de carregamento
- `teste_completo_integrado.py` - Teste completo


## NOTAS IMPORTANTES

1. **PRE-GERACAO**: As etiquetas sao geradas DURANTE o processamento DXF, nao em tempo real
2. **QUALIDADE CONSISTENTE**: Todas as etiquetas tem 300 DPI e tamanho identico
3. **IMPRESSAO RAPIDA**: Lote inteiro pode ser impresso sem gerar nada
4. **NENHUM ERRO**: Sistema nao exibe mais "PNG NAO ENCONTRADO"
5. **DADOS REAIS**: Etiquetas mostram dados 100% reais extraidos do DXF


## SUPORTE

Para problemas ou duvidas:
1. Verifique a pasta `C:\EngenhariaPlanPro\etiquetas\` existe
2. Rode teste: `python teste_completo_integrado.py`
3. Verifique console para mensagens de erro
4. Consulte documentacao em: `IMPLEMENTACAO_ETIQUETAS_PNG.md`

---

**Sistema Pronto para Uso! ✓**
Data: 2025-01-15
