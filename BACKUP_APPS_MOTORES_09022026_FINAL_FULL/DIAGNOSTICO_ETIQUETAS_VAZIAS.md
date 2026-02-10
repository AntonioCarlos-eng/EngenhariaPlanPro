# Diagnóstico: Etiquetas Vazias na Impressão

## Problema Identificado
Ao imprimir etiquetas, o sistema gera etiquetas em branco/vazias sem dados.

## Causas Possíveis
1. **Dados não carregados**: `self.dados_processados` está vazio
2. **Formato de dados incompatível**: Os dados extraídos têm estrutura diferente
3. **Exceções silenciosas**: Erros não capturados que causam imagens em branco
4. **Índice fora do intervalo**: Tentativa de acessar dados inexistentes

## Correções Implementadas

### 1. Validação de Dados em `_gerar_imagem_etiqueta()`
- Adicionada verificação se `dado` está vazio ou incompleto
- Adicionada tratamento de exceções com mensagem de erro visível
- Se dados inválidos, mostra "ERRO: Dados incompletos" em vermelho na etiqueta

### 2. Validação em `imprimir_etiquetas()`
- Adicionado check se `self.dados_processados` está vazio
- Adicionado debug print do total de etiquetas e primeiro dado

### 3. Debug no Loop de Impressão
- Adicionadas verificações antes de acessar cada etiqueta
- Print de avisos se índice estiver fora do intervalo
- Print de avisos se dado estiver vazio

### 4. Melhorias em `preencher_tabela()`
- Adicionada validação de estrutura de dados
- Adicionadas mensagens de erro para dados inválidos
- Verifica se tem pelo menos 5 elementos (viga, pos, bitola, qtde, comp)

### 5. Debug Expandido em `_imprimir_etiquetas_exec()`
- Prints mostrando total de dados no início
- Prints mostrando estrutura do primeiro dado
- Aviso claro se dados_processados está VAZIO

## Como Diagnosticar o Problema

### Passo 1: Verificar se os dados foram processados
```
1. Processe os arquivos (botão "PROCESSAR" ou "PROCESSAR 2.0")
2. Verifique se a tabela na interface mostra dados
3. Abra o console/terminal e procure por:
   - "[DEBUG] Total de etiquetas a imprimir: X"
   - "[DEBUG] Primeira etiqueta: (...dados...)"
```

### Passo 2: Tentar imprimir e observar os logs
```
1. Clique em "Etiquetas" ou "Imprimir"
2. Na janela de etiquetas, clique em "Imprimir"
3. Procure por mensagens [DEBUG] mostrando:
   - Quantidade de dados
   - Índices sendo processados
   - Qualquer mensagem [WARN]
```

### Passo 3: Se vir "ERRO: Dados incompletos"
```
Significa que os dados estão com estrutura incorreta:
- Verifique se o motor de processamento está funcionando
- Tente usar o outro motor (v1 ou v2)
- Verifique o arquivo DXF/DWG
```

## Se Ainda Tiver Problemas

1. **Dados vazios completamente**: 
   - Certifique-se de ter processado os arquivos
   - Verifique se a tabela principal mostra dados

2. **Etiquetas com "ERRO: Dados incompletos"**:
   - Significa que os dados têm estrutura errada
   - Tente o outro motor de processamento
   - Verifique a formatação do arquivo DXF/DWG

3. **Página em branco na impressão**:
   - Verifique se a prévia mostra dados
   - Tente aumentar a escala (120-130%)
   - Ajuste as margens

## Teste Rápido
Execute: `python test_etiquetas_debug.py`
Isso gera 3 imagens de teste para verificar se PIL está funcionando.

## Melhorias Futuras Recomendadas
- [ ] Adicionar mais validação do formato dos dados
- [ ] Criar interface de debug integrada
- [ ] Adicionar log permanente em arquivo
- [ ] Criar wizard de diagnóstico automático
