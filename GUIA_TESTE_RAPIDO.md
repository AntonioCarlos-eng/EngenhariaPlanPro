# 📖 GUIA RÁPIDO - COMO TESTAR A NOMENCLATURA EXPANDIDA

## 🎯 Objetivo
Validar que seu app romaneio agora processa corretamente arquivos DXF com:
- Nomenclatura expandida: `P14-P32`, `P14-P32(X2)`, `P32(X2)`
- Nomenclatura separada: `P14;P32`, `P14/P32`
- Nomenclatura simples: `P1`, `P10` (funcionando como antes)

## 📋 Pré-requisitos
- ✅ App pilares_app.py aberto
- ✅ Arquivo DXF com pilares para testar
- ✅ Terminal com Python disponível

## 🚀 Opção 1: Testar via App GUI (Recomendado)

### Passo 1: Abrir o App
```bash
cd c:\EngenhariaPlanPro
python pilares_app.py
```
A interface gráfica deve abrir normalmente.

### Passo 2: Carregar um DXF
1. Clique em **"Carregar Projeto"** ou **"Load Project"**
2. Selecione um arquivo DXF com pilares
3. Observar a janela de progresso

### Passo 3: Processar Pilares
1. Clique em **"Processar Pilares"** ou **"Process"**
2. Aguardar processamento
3. Verificar resultado na **tabela de romaneio**

### Passo 4: Validar Resultados

**Arquivo DXF Antigo (P1-P6):**
- Esperado: 6 linhas (P1, P2, P3, P4, P5, P6)
- Status: ✅ Deve ser IDÊNTICO a antes (zero regressões)

**Arquivo DXF Novo (P14-P32(X2)):**
- Esperado: 19 linhas (P14, P15, P16, ..., P32)
- Status: ✅ NOVO comportamento (antes geraria erro ou 1 linha)
- Dados: Cada pilar tem seus próprios valores

## 🧪 Opção 2: Testar via Terminal (Para Desenvolvedores)

### Teste 1: Validação de Expansão
```bash
python test_nomenclatura_expandida.py
```

**Esperado:**
```
====================================================================
==
RESULTADO: 9 sucessos, 0 falhas
====================================================================
==
```

### Teste 2: Demonstração Visual
```bash
python demo_nomenclatura_expandida.py
```

**Esperado:**
```
✅ Resultado: 25 entradas totais no romaneio
✅ SEM quebra de compatibilidade com arquivos antigos
✅ Pronto para usar com qualquer arquivo DXF que use nomenclatura expandida
```

## 🔍 Checklist de Validação

### Compatibilidade com Versão Anterior
- [ ] Arquivo DXF antigo processa SEM erros
- [ ] Número de linhas no romaneio é IGUAL a antes
- [ ] Valores de bitola, quantidade, comprimento IDÊNTICOS

### Suporte a Nomenclatura Expandida
- [ ] Arquivo DXF com "P14-P32" expande para 19 pilares
- [ ] Arquivo DXF com "P14-P32(X2)" expande corretamente (ignora X2)
- [ ] Arquivo DXF com "P14;P32" mostra P14 e P32 separados
- [ ] Arquivo DXF com "P32(X2)" mostra apenas P32

### Integridade de Dados
- [ ] Cada pilar expandido tem seus próprios dados
- [ ] Sem duplicação de dados
- [ ] Nenhum pilar perdido

## ❌ Se Algo Não Funcionar

### Problema 1: App mostra erro ao processar DXF novo
**Solução:**
1. Limpar cache:
   ```bash
   rm -r c:\EngenhariaPlanPro\core\__pycache__
   rm -r c:\EngenhariaPlanPro\__pycache__
   ```
2. Reiniciar app:
   ```bash
   python pilares_app.py
   ```

### Problema 2: Arquivo antigo com regressão
**Solução:**
1. Restaurar backup do arquivo antigo (se tiver)
2. Verificar se é realmente regressão:
   ```bash
   python test_nomenclatura_expandida.py
   ```
   Se testes passam, pode ser problema específico do DXF

### Problema 3: Nomenclatura não reconhecida
**Solução:**
1. Verificar padrão exato do DXF
2. Reportar padrão para implementação futura
3. Exemplo: se encontrou "P1@P5" novo:
   ```
   Padrão encontrado: P1@P5
   Função deveria suportar? Sim
   Status: Implementar em próxima versão
   ```

## 📞 Suporte

Se encontrar problemas:

1. **Teste unitário falha**
   ```bash
   python test_nomenclatura_expandida.py
   # Compartilhar output
   ```

2. **App mostra erro**
   - Abrir arquivo de log (se existir)
   - Tentar arquivo DXF diferente
   - Verificar console para exceções

3. **Resultado inesperado em romaneio**
   - Verificar se quantidade de linhas está correta
   - Comparar com versão anterior (compatibilidade)
   - Executar teste de demo

## ✅ Sucesso!

Se conseguiu:
- [ ] Testar arquivo antigo (sem regressões)
- [ ] Testar arquivo novo (com expansão)
- [ ] Todos os testes unitários passam

**Então a implementação está ✅ SUCESSO!**

---

**Próximo passo**: Compartilhar resultado dos testes (compatibilidade e expansão)
**Status esperado**: "Tudo funcionando!" / "BATEU!" / "SUCCESS!"
