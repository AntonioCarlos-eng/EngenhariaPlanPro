# core/extractor.py
import ezdxf

def extrair_textos(arquivo):
    try:
        doc = ezdxf.readfile(arquivo)
    except Exception as e:
        return [], f"Erro ao abrir DXF: {e}"

    msp = doc.modelspace()
    textos = []

    for e in msp:
        if e.dxftype() in ("TEXT", "MTEXT"):
            try:
                if e.dxftype() == "TEXT":
                    textos.append(e.text.strip())
                else:
                    textos.append(e.text.strip())
            except:
                pass

    return textos, "OK"
