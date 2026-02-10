import ezdxf

try:
    doc = ezdxf.readfile('pilares-028.DXF')
except:
    from ezdxf.recover import readfile as recover_readfile
    try:
        doc, auditor = recover_readfile('pilares-028.DXF')
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

textos_sort = sorted(textos, key=lambda t: (-t[2], t[1]))
print(f'Total de textos: {len(textos_sort)}\n')
for i, (txt, x, y) in enumerate(textos_sort[:50]):
    print(f'{i+1:2d}. Y={y:6.1f} X={x:6.1f} | {txt[:60]}')
