# FIX: Medidas não aparecem após editar estribos

## Problema
Quando o usuário editava um estribo e salvava as medidas (lado1, lado2, lado3, lado4), as medidas NÃO apareciam visualmente no desenho da etiqueta.

## Root Cause
Na função `_desenhar_forma_simplificada()`, o tipo 'estribo' não tinha implementação para desenhar as medidas dos lados. 

O código tinha suporte para:
- `dobra` - com `medida_dobra` ✓
- `dobra_dupla` - com `medida_dobra` (tupla) ✓  
- `gancho` - com `medidas_gancho` ✓
- `estribo` - SEM suporte a medidas ❌

## Solução Implementada

### 1. Atualizar função `_desenhar_forma_simplificada()`
- Adicionado parâmetro `estribo_lados=None`
- Implementado desenho das medidas dos 4 lados do estribo (A, B, C, D)
- Medidas desenhadas usando `canvas.create_text()` em cada lado

### 2. Armazenar lados do estribo durante salvamento
Na função `desenhar_etiquetas_com_selecao()`, adicionado:
```python
if forma == 'estribo':
    self.estribo_lados[(viga, pos)] = (lado1, lado2, lado3, lado4)
```

### 3. Passar `estribo_lados` para função de desenho
Atualizado call para `_desenhar_forma_simplificada()`:
```python
estribo_lados = None
if forma == 'estribo' and hasattr(self, 'estribo_lados') and chave in self.estribo_lados:
    estribo_lados = self.estribo_lados[chave]

self._desenhar_forma_simplificada(self.canvas_etiq, dx, dy, dw, dh, forma, 
                                   medida_dobra, medidas_gancho, estribo_lados)
```

### 4. Inicializar `self.estribo_lados` no `__init__`
```python
self.estribo_lados = {}  # {(viga, pos): (lado_a, lado_b, lado_c, lado_d)}
```

### 5. Suporte na impressão
- Passar `estribo_lados` para o gerador na impressão
- Incluir no fallback JSON

## Arquivos Modificados
- `vigas_app.py` (linhas 352, 2481-2510, 2390-2404, 4155-4159, 4206-4210)

## Resultado Esperado
Agora quando o usuário edita um estribo e preenche lado1=10, lado2=15, lado3=20, lado4=25:
- Medidas são salvas em `self.medidas_customizadas[(viga, pos)]`
- Lados são armazenados em `self.estribo_lados[(viga, pos)]`
- Ao re-renderizar, as medidas aparecem no desenho:
  - "A=10cm" (topo)
  - "B=15cm" (direita)
  - "C=20cm" (base)
  - "D=25cm" (esquerda)
