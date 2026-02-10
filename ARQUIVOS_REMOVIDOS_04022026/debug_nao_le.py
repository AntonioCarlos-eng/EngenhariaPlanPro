import ezdxf
from collections import Counter

arquivo = r"C:\Users\orqui\OneDrive\Área de Trabalho\projetos\pilares\novos pilares.DWG"

try:
    doc = ezdxf.readfile(arquivo)
    msp = doc.modelspace()
    
    # Coletar textos
    textos = []
    for entity in msp:
        if entity.dxftype() == 'TEXT':
            try:
                txt = entity.dxf.text.strip()
                x = entity.dxf.insert.x
                y = entity.dxf.insert.y
                textos.append((txt, x, y))
            except:
                pass
        elif entity.dxftype() == 'MTEXT':
            try:
                txt = entity.text.strip()
                x = entity.dxf.insert.x
                y = entity.dxf.insert.y
                textos.append((txt, x, y))
            except:
                pass
    
    with open('analise_nao_le.txt', 'w', encoding='utf-8') as f:
        f.write(f"Total de textos: {len(textos)}\n")
        f.write("=" * 80 + "\n\n")
        
        # Buscar cabeçalhos
        cabecalhos = [t for t in textos if any(p in t[0].upper() for p in ['POS', 'BIT', 'QUANT', 'COMP'])]
        f.write(f"Cabeçalhos encontrados: {len(cabecalhos)}\n\n")
        
        for txt, x, y in sorted(cabecalhos, key=lambda t: -t[2])[:20]:
            f.write(f"X={x:8.2f} Y={y:8.2f} '{txt}'\n")
        
        # Coordenadas X mais comuns
        f.write("\n" + "=" * 80 + "\n")
        f.write("Coordenadas X mais comuns:\n\n")
        x_coords = Counter([round(x, 1) for _, x, _ in textos])
        for x, count in x_coords.most_common(15):
            f.write(f"X={x:8.1f}: {count:4d} ocorrências\n")
        
        # Textos na região X > 65
        f.write("\n" + "=" * 80 + "\n")
        f.write("Textos com X > 65 (região de tabelas):\n\n")
        textos_tabela = [t for t in textos if t[1] > 65.0]
        f.write(f"Total: {len(textos_tabela)}\n\n")
        
        for txt, x, y in sorted(textos_tabela, key=lambda t: -t[2])[:40]:
            f.write(f"X={x:8.2f} Y={y:8.2f} '{txt}'\n")
    
    print("Análise salva em: analise_nao_le.txt")
    
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()
