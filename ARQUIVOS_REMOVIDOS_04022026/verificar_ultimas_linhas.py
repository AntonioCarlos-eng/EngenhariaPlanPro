#!/usr/bin/env python3
# Verificar se as linhas 35-57 estão sendo agrupadas

from core.lajes_motor import _agrupar_textos_por_coordenada
import ezdxf
from ezdxf.recover import readfile as recover_readfile

arquivo = r'c:\EngenhariaPlanPro\laje-neg-cob-105-original.DXF'
doc, auditor = recover_readfile(arquivo)

textos_com_coords = []
for entity in doc.entities:
    if not entity.is_alive:
        continue
    try:
        if entity.dxftype() == 'TEXT':
            txt = entity.dxf.text
            x = entity.dxf.insert[0]
            y = entity.dxf.insert[1]
            textos_com_coords.append((txt.strip(), x, y))
        elif entity.dxftype() == 'MTEXT':
            txt = entity.plain_text()
            x = entity.dxf.insert[0]
            y = entity.dxf.insert[1]
            textos_com_coords.append((txt.strip(), x, y))
    except:
        pass

linhas_agrupadas = _agrupar_textos_por_coordenada(textos_com_coords, tolerancia_y=0.25)

print(f'Total de linhas agrupadas: {len(linhas_agrupadas)}\n')

# Mostra últimas 40 linhas
print("ULTIMAS 40 LINHAS AGRUPADAS:")
for i, linha in enumerate(linhas_agrupadas[-40:]):
    tokens = [t[0] for t in linha]
    y_val = linha[0][2] if linha else 0
    linha_str = " | ".join(tokens[:6])
    print(f"{len(linhas_agrupadas)-40+i:3d}. Y={y_val:6.2f} | {linha_str}")
