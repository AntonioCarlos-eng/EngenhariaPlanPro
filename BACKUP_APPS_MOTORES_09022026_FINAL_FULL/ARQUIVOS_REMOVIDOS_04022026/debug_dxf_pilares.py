import ezdxf
from ezdxf.recover import readfile as recover_readfile
import re

arquivo = r"c:\Users\orqui\OneDrive\Área de Trabalho\projetos\pilares\###pilares l1-018 - Copia.DXF"

print(f"Analisando: {arquivo}\n")

doc, auditor = recover_readfile(arquivo)

RE_PILAR_NAME = re.compile(r'(?:PILAR\s*)?P\s*(\d+)', re.IGNORECASE)

pilares_encontrados = {}

for entity in doc.modelspace():
    if entity.dxftype() in ['TEXT', 'MTEXT']:
        try:
            if entity.dxftype() == 'MTEXT':
                texto = entity.plain_text()
            else:
                texto = entity.dxf.text
            
            # Procurar por pilares
            match = RE_PILAR_NAME.search(texto)
            if match:
                pilar_nome = f"P{match.group(1)}"
                
                if pilar_nome not in pilares_encontrados:
                    pilares_encontrados[pilar_nome] = []
                
                # Pegar posição
                x = entity.dxf.insert.x if hasattr(entity.dxf, 'insert') else 0
                y = entity.dxf.insert.y if hasattr(entity.dxf, 'insert') else 0
                
                pilares_encontrados[pilar_nome].append({
                    'texto': texto[:200],
                    'x': x,
                    'y': y,
                    'tipo': entity.dxftype()
                })
        except:
            pass

print(f"Total de pilares encontrados: {len(pilares_encontrados)}\n")

for pilar in sorted(pilares_encontrados.keys(), key=lambda p: int(re.search(r'\d+', p).group())):
    print(f"\n{'='*80}")
    print(f">>> {pilar}")
    print('='*80)
    
    # Contar quantas linhas N1, N2, etc.
    contadores = {}
    
    for item in pilares_encontrados[pilar]:
        texto = item['texto']
        
        # Procurar por N1, N2, N3, etc
        matches_n = re.findall(r'N\s*(\d+)', texto, re.IGNORECASE)
        for n in matches_n:
            pos = f"N{n}"
            if pos not in contadores:
                contadores[pos] = 0
            contadores[pos] += 1
        
        print(f"\nPosição: ({item['x']:.1f}, {item['y']:.1f})")
        print(f"Tipo: {item['tipo']}")
        print(f"Texto: {texto[:150]}")
    
    if contadores:
        print(f"\n📊 Contagem de posições:")
        for pos in sorted(contadores.keys(), key=lambda p: int(re.search(r'\d+', p).group())):
            print(f"   {pos}: {contadores[pos]} ocorrências")
