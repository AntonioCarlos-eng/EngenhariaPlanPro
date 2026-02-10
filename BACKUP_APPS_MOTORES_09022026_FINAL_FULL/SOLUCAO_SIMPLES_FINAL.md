# 🎯 SOLUÇÃO SIMPLES E DIRETA

## Problema
Preview carrega PNGs com cache antigo, não mostra edições.

## Solução Mais Simples
Ao invés de tentar substituir todo o método (muito complexo), vou adicionar **UMA LINHA** que força recarga dos PNGs:

### Adicionar ANTES de carregar cada PNG:

```python
# Forçar recarga do arquivo (limpar cache do PIL)
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
```

E modificar o carregamento para:

```python
# Ao invés de:
img = Image.open(caminho_png)

# Usar:
img = Image.open(caminho_png)
img.load()  # Forçar carregamento imediato
img = img.copy()  # Criar cópia nova (sem cache)
```

## Implementação Rápida

Vou criar um script que adiciona essas 2 linhas no lugar certo.

---

**OU AINDA MAIS SIMPLES:**

Adicionar `import gc` e `gc.collect()` logo APÓS regerar os PNGs e ANTES de coletar os caminhos para o preview.

Isso força o Python a limpar o cache de memória.
