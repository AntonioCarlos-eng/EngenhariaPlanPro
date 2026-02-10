# ✅ CORREÇÃO: Impressão Direta e Etiquetas em Branco

**Data:** 24/01/2026
**Versão:** 2.5.1

---

## 🔧 Problemas Corrigidos

### 1. ❌ Etiquetas saindo em branco
**Causa:** O método `gerar_e_imprimir_direto()` não estava inserindo a imagem do desenho técnico
**Solução:** Adicionado código para:
- Carregar PNG localizado (se existir)
- Extrair desenho do DXF dinamicamente
- Centralizar e redimensionar corretamente

### 2. ❌ Continua abrindo janelas após impressão
**Causa:** `messagebox.showinfo()` estava sendo chamado após cada impressão
**Solução:** 
- Removido messagebox de confirmação
- Editor fecha automaticamente antes de imprimir
- Apenas mostra erro se falhar

### 3. ❌ Não imprime direto após selecionar impressora
**Causa:** Fluxo interrompido por diálogos desnecessários
**Solução:**
- Fecha editor antes de abrir diálogo de impressora
- Após selecionar impressora → imprime direto
- Sem confirmações adicionais

---

## 🎯 Fluxo Corrigido

```
1. Usuário clica "Imprimir Etiquetas"
   ↓
2. Abre editor com preview
   ↓
3. Marca etiquetas com checkboxes
   ↓
4. Clica "Gerar Selecionadas"
   ↓
5. FECHA editor
   ↓
6. Abre diálogo de impressora
   ↓
7. Escolhe impressora → Confirma
   ↓
8. IMPRIME DIRETO (sem janelas)
   ✅ Etiquetas com desenhos completos
```

---

## 📝 Arquivos Modificados

### `core/etiquetas_generator.py`
- ✅ Linha ~603: Adicionado código para inserir desenho técnico
- ✅ Carrega PNG ou extrai do DXF
- ✅ Centraliza e redimensiona automaticamente

### `vigas_app.py`
- ✅ Linha ~4158: Remove fechamento duplicado do editor
- ✅ Linha ~4307: Fecha editor ANTES de imprimir
- ✅ Linha ~4315: Remove messagebox de confirmação
- ✅ Linha ~4289: Melhora obtenção de arquivos DXF

---

## ✅ Resultado

**Antes:**
- ❌ Etiqueta em branco (sem desenho)
- ❌ Várias janelas se abrindo
- ❌ Fluxo confuso

**Depois:**
- ✅ Etiqueta completa com desenho
- ✅ Apenas 1 diálogo (escolher impressora)
- ✅ Imprime direto após confirmar
- ✅ Fluxo limpo e profissional

---

## 🧪 Testar

Execute o app e:
1. Processe vigas
2. Clique "Imprimir Etiquetas"
3. Marque algumas etiquetas
4. Clique "Gerar Selecionadas"
5. Escolha impressora
6. ✅ Deve imprimir direto sem mais janelas

---

**Status:** ✅ CORRIGIDO
