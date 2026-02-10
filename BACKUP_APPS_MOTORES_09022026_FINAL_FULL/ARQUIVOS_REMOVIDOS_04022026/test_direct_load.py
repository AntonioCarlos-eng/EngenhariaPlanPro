"""
Test Direct: Simula carregamento de PNG idêntico ao vigas_app.py
"""
import os
from PIL import Image

# Simular dados_processados[0] do vigas_app
dado = ('V8', 'N1', 10.00, 2, 2.950)  # Baseado na etiqueta mostrada

print("=" * 80)
print("TEST DIRECT: Simulando _gerar_imagem_etiqueta")
print("=" * 80)

# Extrair dados
viga = str(dado[0]).strip()
pos = str(dado[1]).strip()
bitola = float(dado[2])
qtde = int(dado[3])
comp_m = float(dado[4])

print(f"\n1. Dados extraídos:")
print(f"   Viga: '{viga}' (len={len(viga)})")
print(f"   Pos: '{pos}' (len={len(pos)})")
print(f"   Bitola: {bitola}")
print(f"   Qtde: {qtde}")
print(f"   Comp_m: {comp_m}")

# Calcular padrão
comp_cm = int(round(comp_m * 100))
bitola_str = f"{bitola:.1f}"
target_pattern = f"_{viga}_{pos}_b{bitola_str}_q{qtde}_c{comp_cm}cm_"

print(f"\n2. Padrão calculado:")
print(f"   comp_cm: {comp_cm}")
print(f"   bitola_str: '{bitola_str}'")
print(f"   target_pattern: '{target_pattern}'")

# Verificar pasta
pasta_etiq = r"c:\EngenhariaPlanPro\etiquetas"
print(f"\n3. Verificando pasta:")
print(f"   Caminho: {pasta_etiq}")
print(f"   Existe: {os.path.exists(pasta_etiq)}")

if os.path.exists(pasta_etiq):
    todos_pngs = [f for f in os.listdir(pasta_etiq) if f.endswith('.png')]
    print(f"   Total PNGs: {len(todos_pngs)}")
    
    # Arquivos com viga/pos
    matching = [f for f in todos_pngs if viga in f and pos in f]
    print(f"\n4. Arquivos com '{viga}' e '{pos}': {len(matching)}")
    for m in matching[:5]:
        print(f"   - {m}")
        if target_pattern in m:
            print(f"     ✅ CONTÉM O PADRÃO EXATO!")
        else:
            print(f"     ❌ NÃO contém padrão exato")
    
    # Buscar padrão exato
    print(f"\n5. Buscando padrão exato: '{target_pattern}'")
    encontrado = None
    for arq in todos_pngs:
        if target_pattern in arq:
            encontrado = os.path.join(pasta_etiq, arq)
            print(f"   ✅ ENCONTRADO: {os.path.basename(encontrado)}")
            break
    
    if encontrado:
        print(f"\n6. Carregando imagem:")
        print(f"   Arquivo: {os.path.basename(encontrado)}")
        print(f"   Tamanho: {os.path.getsize(encontrado)} bytes")
        
        try:
            img = Image.open(encontrado)
            print(f"   Dimensões: {img.size}")
            print(f"   Modo: {img.mode}")
            print(f"   ✅ IMAGEM CARREGADA COM SUCESSO!")
        except Exception as e:
            print(f"   ❌ ERRO ao carregar: {e}")
    else:
        print(f"   ❌ NÃO ENCONTRADO com padrão exato")
        
        # Busca genérica
        pattern_generico = f"_{viga}_{pos}_"
        print(f"\n6. Tentando padrão genérico: '{pattern_generico}'")
        for arq in todos_pngs:
            if pattern_generico in arq:
                print(f"   ✅ Encontrado (genérico): {arq}")
                break
        else:
            print(f"   ❌ Nem com padrão genérico encontrou")

print("\n" + "=" * 80)
