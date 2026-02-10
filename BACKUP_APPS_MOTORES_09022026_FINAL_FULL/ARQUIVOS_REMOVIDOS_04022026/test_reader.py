from core.reader import ler_desenho

# COLOQUE AQUI O CAMINHO COMPLETO DO SEU DXF
arq = r"C:\Users\orqui\OneDrive\Área de Trabalho\projetos\ENV P 1 COTACAO BLOCO ARRAQUE E PILARES - Copia.dxf"
textos = ler_desenho(arq)

print("\n=== TEXTOS EXTRAÍDOS DO DXF ===\n")
for i, t in enumerate(textos):
    print(i, "→", repr(t))
