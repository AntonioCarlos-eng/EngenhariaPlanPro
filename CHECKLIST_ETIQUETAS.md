# ✅ CHECKLIST: Etiquetas Funcionando Corretamente

## Antes de Imprimir

- [ ] Arquivos DXF/DWG selecionados ("📁 Selecionar Arquivos")
- [ ] Clicou "⚙️ PROCESSAR" ou "⚙️ PROCESSAR 2.0"
- [ ] Tabela mostra dados (pelo menos 1 linha)
- [ ] Campo "Obra" preenchido
- [ ] Campo "Pavimento" preenchido

## Teste de Prévia

- [ ] Clicou "🏷️ Etiquetas"
- [ ] Janela "Etiquetas de Vigas" abriu
- [ ] Clicou "Prévia" (na janela)
- [ ] Imagem de etiqueta abriu (png)
- [ ] Imagem mostra dados: OBRA, VIGA, POSIÇÃO, etc

## Impressão

- [ ] Escolheu impressora (dropdown)
- [ ] Definiu intervalo de páginas
- [ ] Definiu escala (geralmente 100%)
- [ ] Clicou "Imprimir"
- [ ] Impressora iniciou impressão

## Etiquetas Prontas

- [ ] Etiquetas têm borda preta
- [ ] Etiquetas têm dados visíveis
- [ ] Não há etiquetas em branco
- [ ] Números das etiquetas (1, 2, 3...) aparecem
- [ ] Código de barras está presente

---

## Se Algo Falhar

### Não consegue processar arquivos?
```
❌ Arquivo não está em formato válido (DXF/DWG)
❌ Arquivo está corrompido
❌ Motor de processamento não carregou

✅ Solução:
- Verifique se é realmente DXF ou DWG
- Tente com outro arquivo
- Se "PROCESSAR" não funciona, tente "PROCESSAR 2.0"
```

### Tabela fica vazia após processar?
```
❌ Arquivo não tem vigas no formato esperado
❌ Estrutura do arquivo diferente

✅ Solução:
- Arquivo deve ter:
  - Nome de viga: V1, V2, V3... (maiúscula V)
  - Posições: números como 1, 2, 3, 4...
  - Bitolas: 8, 10, 12.5, 16... mm
  - Quantidades: números inteiros
  - Comprimentos: números decimais (3.5, 4.8...)
```

### Prévia não funciona?
```
❌ Dados inválidos
❌ PIL não está instalado
❌ Permissão para criar arquivo temporário

✅ Solução:
- Se aparecer erro com PIL: pip install Pillow
- Se aparecer erro de permissão: Reinicie o programa
- Se aparecer "ERRO: Dados incompletos": 
  - Tente o outro motor de processamento
```

### Impressão não inicia?
```
❌ Impressora offline
❌ Impressora não está padrão
❌ Fila de impressão travada

✅ Solução:
- Verifique se impressora está ligada
- Selecione impressora manualmente no dropdown
- Reinicie gerenciador de impressão do Windows
```

### Etiquetas saem em branco?
```
❌ Dados foram perdidos entre processamento e impressão
❌ Problema ao gerar imagem

✅ Solução:
- Processe arquivos novamente
- Tente "Prévia" primeiro
- Se Prévia funciona mas impressão não, problema é na impressora
- Se nem Prévia funciona, refaça processamento
```

---

## Console de Debug

Abra PowerShell/Terminal e execute:

```powershell
cd c:\EngenhariaPlanPro
python vigas_app.py
```

Observar no console:
```
[DEBUG] Total de etiquetas a imprimir: 5  ✅ Dados carregados
[DEBUG] Primeira etiqueta: (V1, 1, 12.5, 2, 3.5, 0.617)  ✅ Dados válidos
[DEBUG] Etiqueta 1 impressa com sucesso  ✅ Impressão OK
```

Se vir erros com `[ERROR]` ou `[WARN]`, anote a mensagem e tente a solução correspondente.

---

## Scripts de Teste

### Testar gerador de imagens
```bash
python test_etiquetas_debug.py
```
Deve criar 3 arquivos: `test_etiqueta_0.png`, `test_etiqueta_1.png`, `test_etiqueta_2.png`

### Se criou os PNGs
✅ Sistema de imagens está OK
✅ Problema está nos dados ou processamento

### Se NÃO criou os PNGs
❌ PIL não está funcionando
✅ Solução: `pip install Pillow --upgrade`

---

## Contato/Suporte

Se problemas persistirem:

1. Capture os logs da console (screenshot ou cópia)
2. Teste com `test_etiquetas_debug.py`
3. Verifique arquivo DXF/DWG está correto
4. Tente com outro arquivo de teste
5. Reinicie o programa e tente novamente

---

**Última atualização**: 16/01/2026
**Versão**: 1.0 com correções de validação
