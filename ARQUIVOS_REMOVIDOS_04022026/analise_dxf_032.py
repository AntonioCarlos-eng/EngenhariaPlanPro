import ezdxf

try:
    doc = ezdxf.readfile('pilares-032.DXF')
except:
    try:
        from ezdxf.recover import readfile as recover_readfile
        doc, auditor = recover_readfile('pilares-032.DXF')
    except:
        import sys
        print("Erro ao ler arquivo")
        sys.exit(1)

textos = []
for entity in doc.entities:
    if entity.dxftype() in ['TEXT', 'MTEXT', 'ATTRIB']:
        try:
            txt = entity.dxf.text if entity.dxftype() != 'MTEXT' else entity.plain_text()
            x = entity.dxf.insert.x if hasattr(entity.dxf, 'insert') else 0
            y = entity.dxf.insert.y if hasattr(entity.dxf, 'insert') else 0
            if txt.strip():
                textos.append((txt, round(x, 1), round(y, 1)))
        except:
            pass

# Mostrar resumo
print(f'Total de textos: {len(textos)}')
print(f'\nTextos em diferentes X:')
x_ranges = {}
for txt, x, y in textos:
    x_range = int(x // 10) * 10
    if x_range not in x_ranges:
        x_ranges[x_range] = 0
    x_ranges[x_range] += 1

for x_range in sorted(x_ranges.keys()):
    print(f'  X={x_range:3d}-{x_range+9} : {x_ranges[x_range]:4d} textos')

# Mostrar primeiros textos
textos_sort = sorted(textos, key=lambda t: (-t[2], t[1]))
print(f'\nPrimeiros 30 textos:')
for i, (txt, x, y) in enumerate(textos_sort[:30]):
    print(f'{i+1:2d}. Y={y:6.1f} X={x:6.1f} | {txt[:60]}')
