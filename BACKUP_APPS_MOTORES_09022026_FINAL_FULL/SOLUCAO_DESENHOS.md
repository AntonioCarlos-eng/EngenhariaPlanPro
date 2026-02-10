# SOLUÇÃO DEFINITIVA PARA DESENHOS DAS VIGAS

## Problema
A extração automática do DXF continua capturando partes grandes do projeto ao invés do detalhe específico de cada viga.

## Solução Implementada
Sistema de captura manual guiada que permite:

1. **Renderização completa do DXF** em alta resolução
2. **Interface interativa** para marcar a região de cada viga
3. **Geração automática de PNGs** individuais
4. **Mapeamento persistente** em JSON

## Como Usar

### Passo 1: Executar o gerador
```bash
python gerar_desenhos_vigas.py
```

### Passo 2: Interface
- **Esquerda**: Lista de vigas (❌ não mapeado, ✅ mapeado)
- **Direita**: DXF renderizado completo

### Passo 3: Capturar cada viga
1. Selecione uma viga na lista
2. Arraste um retângulo sobre o desenho dessa viga
3. Clique em "📌 Capturar Região"
4. Repita para todas as vigas

### Passo 4: Gerar PNGs
Clique em "🖼️ Gerar Todos os PNGs"

Os arquivos serão salvos em: `export/desenhos_vigas/{viga}_desenho.png`

## Configuração

Edite `gerar_desenhos_vigas.py` linha 322:
```python
lista_vigas = ['V8', 'V9', 'V10', 'VM1', 'VM2', ...]  # Adicionar todas do projeto
```

## Resultado

O sistema de etiquetas agora buscará automaticamente:
1. `export/desenhos_vigas/{viga}_desenho.png` (prioritário)
2. PNG legado específico (fallback)

## Vantagens
- ✅ 100% preciso - você escolhe exatamente o que mostrar
- ✅ Rápido - uma vez mapeado, gera todos instantaneamente
- ✅ Reutilizável - salva mapeamento em JSON
- ✅ Visual - vê exatamente o que está selecionando
