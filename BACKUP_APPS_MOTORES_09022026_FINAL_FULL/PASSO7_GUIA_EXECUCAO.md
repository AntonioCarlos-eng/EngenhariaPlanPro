# PASSO 7: GUIA DE EXECUÇÃO DOS TESTES

## 🚀 Como Executar os Testes Finais

### 1️⃣ Prepare o Ambiente

```bash
# Navegar para o diretório principal
cd c:\EngenhariaPlanPro

# Verificar que a versão Python é 3.8+
python --version

# Verificar que os pacotes estão instalados
pip list | grep -E "Pillow|reportlab"
```

### 2️⃣ Execute o Script de Testes

```bash
# Executar a suite completa de testes
python PASSO7_TESTES_FINAIS.py
```

**Saída esperada:**
```
================================================================================
PASSO 7: TESTES FINAIS E VALIDAÇÃO
================================================================================

▶ TESTES DE DIMENSÃO:
────────────────────────────────────────────────────────────────────────────
✅ PASSOU | Dimensões da Etiqueta (100x150mm @ 300 DPI)
       Esperado: 1181x1772px, Calculado: 1181x1772px
✅ PASSOU | Margem da Impressora (Argox OS-214)
       Esperado: 2.0mm, Atual: 2.0mm

▶ TESTES DE ESPAÇAMENTO:
────────────────────────────────────────────────────────────────────────────
✅ PASSOU | Espaçamento do Cabeçalho (8mm entre linhas)
       Espaçamento: 8mm = 94px
✅ PASSOU | Dimensão da Caixa OS
       Altura OS: 30mm = 354px

▶ TESTES DE DPI:
────────────────────────────────────────────────────────────────────────────
✅ PASSOU | DPI Padronizado (fixo em 300)
       DPI Padrão: 300 (esperado: 300)
✅ PASSOU | Função mm_to_px() - Conversão Correta
       ✓ 8mm=94px (esperado ~94px); ✓ 20mm=236px (esperado ~236px); ✓ 30mm=354px (esperado ~354px)

▶ TESTES DE GERAÇÃO DE IMAGENS:
────────────────────────────────────────────────────────────────────────────
✅ PASSOU | Geração de PNG com Dimensões Corretas
       Dimensões: 1181x1772px (esperado ~1181x1772px)
✅ PASSOU | Geração de PDF
       PDF: ETIQUETAS_OBRA.001_1_etiq.pdf

================================================================================
✅ Relatório salvo em: PASSO7_RELATORIO_VALIDACAO.txt

... [CHECKLIST VISUAL] ...

✅ Checklist salvo em: PASSO7_CHECKLIST_VISUAL.txt

================================================================================
RESUMO DO PASSO 7
================================================================================

📊 Resultados: 8/8 testes passaram

📄 PNG de teste gerado: ETIQUETAS_OBRA.001_1_etiq.png
📄 PDF de teste gerado: ETIQUETAS_OBRA.001_1_etiq.pdf

✅ PRÓXIMOS PASSOS:
1. Revisar o arquivo 'PASSO7_RELATORIO_VALIDACAO.txt'
2. Imprimir etiquetas de teste usando 'PASSO7_CHECKLIST_VISUAL.txt'
3. Validar dimensões com régua/paquímetro
4. Testar leitura de código de barras
5. Fazer commit das alterações com tag de versão

================================================================================
```

### 3️⃣ Revise os Relatórios Gerados

```bash
# Abrir relatório de validação
notepad PASSO7_RELATORIO_VALIDACAO.txt

# Abrir checklist visual
notepad PASSO7_CHECKLIST_VISUAL.txt
```

### 4️⃣ Imprima Etiquetas de Teste

#### Opção A: PNG (Recomendado para visualização)
```bash
# PNG foi gerado em:
# output/etiquetas/ETIQUETAS_OBRA.001_1_etiq.png

# Abrir com visualizador
explorer output\etiquetas\ETIQUETAS_OBRA.001_1_etiq.png
```

**Validações visuais:**
- [ ] Dimensões: 100mm × 150mm
- [ ] Cabeçalho alinhado (8mm entre linhas)
- [ ] Caixa OS centralizada
- [ ] Tabela legível
- [ ] Código de barras nítido
- [ ] Faixa laranja com texto visível

#### Opção B: PDF (Para impressão)
```bash
# PDF foi gerado em:
# output/etiquetas/ETIQUETAS_OBRA.001_1_etiq.pdf

# Abrir com leitor PDF
explorer output\etiquetas\ETIQUETAS_OBRA.001_1_etiq.pdf
```

### 5️⃣ Teste Físico na Impressora

#### Pré-requisitos
- Etiquetas em branco Argox (100×150mm)
- Impressora Argox OS-214 Plus conectada
- Papel de teste já inserido

#### Procedimento
```bash
# Opção 1: Usar interface gráfica
# Abra vigas_app.py e navegue até "Gerar e Imprimir"

# Opção 2: Linha de comando
python -c "
from core.impressao_etiquetas import ImpressaoProfissionalEtiquetas
dados = [{'viga': 'V8', 'pos': 'N1', 'bitola': 10.0, 'comp': 5.50, 'peso': 12.34, 'qtde': 8}]
impressora = ImpressaoProfissionalEtiquetas('OBRA.001', 'LAJE', dados)
impressora.imprimir_direto_gdi('Argox OS-214')
"
```

### 6️⃣ Validação Física

**Usando o checklist:**

Abra o arquivo `PASSO7_CHECKLIST_VISUAL.txt` e valide cada item:

```
PASSO 2: Alinhamento e Fonte dos Textos
────────────────────────────────────────
□ Cabeçalho (Sigla/Obra, Desenho, Pavimento, Elemento):
  □ Linhas estão alinhadas verticalmente (sem desvios)
  □ Espaçamento entre linhas é consistente (8mm)
  □ Textos não se sobrepõem
  □ Fonte está legível

... e mais 40 items
```

### 7️⃣ Fazer Commit Final

```bash
# Adicionar todos os arquivos modificados
git add -A

# Fazer commit com mensagem descritiva
git commit -m "PASSO 7: Testes finais - 7 passos de correção completos

- PASSO 1: DPI=300 fixo
- PASSO 2: Espaçamento 8mm
- PASSO 3: Caixa OS multi-linha
- PASSO 4: Imagens com LANCZOS
- PASSO 5: Tabela com larguras variáveis
- PASSO 6: Barcode centralizado
- PASSO 7: Suite de testes e validação

Todos os testes passaram. Pronto para produção."

# Criar tag de versão
git tag -a v2.1-PASSO7 -m "7-step thermal printer optimization complete"

# Enviar para repositório
git push origin main
git push --tags
```

---

## 📊 Interpretando os Resultados

### ✅ Se Todos os Testes Passarem

```
📊 Resultados: 8/8 testes passaram
```

**Próximos passos:**
1. Validar impressão física
2. Medir dimensões com régua (tolerância ±0.5mm)
3. Testar código de barras com scanner
4. Confirmar alinhamento de textos
5. Liberado para produção ✅

### ❌ Se Algum Teste Falhar

Exemplo de falha:
```
❌ FALHOU | Dimensões da Etiqueta (100x150mm @ 300 DPI)
       Esperado: 1181x1772px, Calculado: 1200x1800px
```

**Ações de correção:**
1. Revisar o arquivo mencionado na saída
2. Consultar `PASSO7_CONTROLE_VERSAO.md` para localização exata
3. Usar `git diff` para ver mudanças
4. Verificar se DPI_PADRAO está em 300
5. Se necessário, restaurar arquivo: `git restore <arquivo>`

---

## 🔍 Troubleshooting

### Erro: "ImportError: No module named 'PIL'"
```bash
pip install Pillow
```

### Erro: "ImportError: No module named 'reportlab'"
```bash
pip install reportlab
```

### Erro: Arquivo PNG não encontrado
```bash
# Verificar pasta de saída
ls output/etiquetas/
dir output\etiquetas

# Se não existir, criar:
mkdir -p output/etiquetas
```

### Erro: Impressora não encontrada
```bash
# Windows: Verificar se a impressora está instalada
# Painel de Controle > Dispositivos e Impressoras

# Verificar que o driver Argox está instalado
# Se não, instalar from https://www.argox.com.tw/download.php
```

### PNG com dimensões incorretas
```python
# Debug: Verificar conversão
from core.etiquetas_layout_config import mm_to_px

print(f"100mm = {mm_to_px(100)}px (esperado 1181px)")
print(f"150mm = {mm_to_px(150)}px (esperado 1772px)")

# Se diferente, verificar DPI_PADRAO
from core.etiquetas_layout_config import DPI_PADRAO
print(f"DPI_PADRAO = {DPI_PADRAO} (deve ser 300)")
```

---

## 📈 Métricas de Sucesso

| Métrica | Esperado | Obtido | Status |
|---------|----------|--------|--------|
| Dimensões PNG | 1181×1772px | ? | ? |
| Dimensões Física | 100±0.5mm | ? | ? |
| Margem | 2mm | ? | ? |
| Espaçamento | 8mm | ? | ? |
| DPI | 300 | ? | ? |
| Barcode Legível | Sim | ? | ? |
| Textos Alinhados | Sim | ? | ? |
| Cores Corretas | Sim | ? | ? |

---

## 📞 Suporte

### Se Precisar de Ajuda

1. **Revisar documentação:**
   - `PASSO7_CONTROLE_VERSAO.md` - Técnico
   - `PASSO7_SUMARIO_EXECUTIVO.md` - Alto nível

2. **Executar teste verbose:**
   ```python
   # Adicionar print() em core/etiquetas_layout_config.py
   print(f"[DEBUG] DPI_PADRAO = {DPI_PADRAO}")
   print(f"[DEBUG] mm_to_px(100) = {mm_to_px(100)}")
   ```

3. **Restaurar versão anterior:**
   ```bash
   git log --oneline
   git checkout <commit_anterior>
   ```

---

## ✨ Conclusão

Você acabou de completar os **7 PASSOS** de correção de impressão térmica!

**Próximo:** Validar com impressão física e liberar para produção. 🚀

---

*Documento: PASSO7_GUIA_EXECUCAO.md*  
*Data: 28 de janeiro de 2026*
