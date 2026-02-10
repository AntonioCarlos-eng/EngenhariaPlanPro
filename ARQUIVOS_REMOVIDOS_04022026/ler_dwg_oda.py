import ezdxf
from ezdxf.addons import importer
import os

arquivo_dwg = r"C:\Users\orqui\OneDrive\Área de Trabalho\projetos\pilares\novos pilares.DWG"
arquivo_dxf = r"C:\EngenhariaPlanPro\novos_pilares_temp.DXF"

print(f"Convertendo DWG para DXF via ODA...")
print(f"Entrada: {arquivo_dwg}")
print(f"Saída: {arquivo_dxf}")

try:
    # Converter DWG para DXF usando ODA
    importer.convert_dwg_to_dxf(arquivo_dwg, arquivo_dxf)
    print("Conversão concluída!")
    
    # Agora ler o arquivo DXF
    print("\nLendo arquivo DXF...")
    doc = ezdxf.readfile(arquivo_dxf)
    msp = doc.modelspace()
    
    print("Extraindo entidades...")
    textos = []
    count = 0
    
    for entity in msp:
        count += 1
        if count % 1000 == 0:
            print(f"  Processadas {count} entidades...")
        
        if entity.dxftype() == 'TEXT':
            try:
                txt = entity.dxf.text.strip()
                x = entity.dxf.insert.x
                y = entity.dxf.insert.y
                if txt:  # Apenas textos não vazios
                    textos.append((txt, x, y))
            except:
                pass
        elif entity.dxftype() == 'MTEXT':
            try:
                txt = entity.text.strip()
                x = entity.dxf.insert.x
                y = entity.dxf.insert.y
                if txt:
                    textos.append((txt, x, y))
            except:
                pass
    
    print(f"\nTotal de entidades processadas: {count}")
    print(f"Total de textos extraídos: {len(textos)}")
    
    # Buscar cabeçalhos
    print("\nBuscando cabeçalhos...")
    cabecalhos = [t for t in textos if any(p in t[0].upper() for p in ['POS', 'BIT', 'QUANT', 'COMP', 'PILAR'])]
    print(f"Cabeçalhos encontrados: {len(cabecalhos)}")
    
    if cabecalhos:
        print("\nPrimeiros 20 cabeçalhos:")
        for txt, x, y in sorted(cabecalhos, key=lambda t: -t[2])[:20]:
            print(f"  X={x:7.2f} Y={y:7.2f} '{txt}'")
    
    # Textos na região X > 65
    print("\nTextos com X > 65 (região de tabelas):")
    textos_tabela = [t for t in textos if t[1] > 65.0]
    print(f"Total: {len(textos_tabela)}")
    
    if textos_tabela:
        print("\nPrimeiros 40 (organizados por Y, descendente):")
        for txt, x, y in sorted(textos_tabela, key=lambda t: -t[2])[:40]:
            print(f"  X={x:7.2f} Y={y:7.2f} '{txt}'")
    
    print("\nConcluído!")
    
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Limpar arquivo temporário
    if os.path.exists(arquivo_dxf):
        try:
            os.remove(arquivo_dxf)
            print(f"Arquivo temporário removido.")
        except:
            pass
