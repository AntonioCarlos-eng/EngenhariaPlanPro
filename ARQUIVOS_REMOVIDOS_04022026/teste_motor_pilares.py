# teste_motor_pilares.py
from core.motor_pilares import processar_pilares

# 👉 Lista de arquivos DXF para testar
arquivos = [
    r"C:\Users\orqui\OneDrive\Área de Trabalho\projetos\ENV P 1 COTACAO BLOCO ARRAQUE E PILARES - Copia.dxf"
]

# 👉 Executa o processamento
dados, peso_total, total_barras = processar_pilares(arquivos)

print("\n============================================")
print("              RESULTADO FINAL")
print("============================================\n")

if total_barras == 0:
    print("⚠️ NENHUMA BARRA ENCONTRADA – FORMATO DO CAD É DIFERENTE\n")
else:
    print(f"TOTAL BARRAS: {total_barras}")
    print(f"PESO TOTAL: {peso_total:.2f} kg\n")

print("============================================\n")
