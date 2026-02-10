import os
import ezdxf

arquivo = r'C:\Users\orqui\OneDrive\Área de Trabalho\projetos\#ES-007-R2 - Copia. DXF'

try:
    doc = ezdxf.readfile(arquivo)
    msp = doc.modelspace()
    
    print("="*80)
    print("TEXTOS ENCONTRADOS NO DXF:")
    print("="*80)
    
    for i, entity in enumerate(msp.query('TEXT')):
        try:
            texto = entity.  dxf.  text.  strip()
            if texto:
                print(f"{i}: '{texto}'")
        except:
            pass
    
    print("\n" + "="*80)
    print("MTEXTS ENCONTRADOS:")
    print("="*80)
    
    for i, entity in enumerate(msp.query('MTEXT')):
        try:
            texto = entity. text. strip()
            if texto:
                print(f"{i}: '{texto}'")
        except:
            pass

except Exception as e:
    print(f"Erro: {e}")