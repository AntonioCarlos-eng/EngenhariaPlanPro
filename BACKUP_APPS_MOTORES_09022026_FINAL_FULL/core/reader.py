# core/reader.py - Leitor DXF estável (retorna apenas lista de textos)

import re
import ezdxf


def limpar_mtexto(texto: str) -> str:
    """Remove códigos de formatação do MTEXT e compacta em uma linha."""
    if not texto:
        return ""

    # Remove comandos tipo \A1; \C255; etc
    texto = re.sub(r'\\[A-Za-z0-9]+;', ' ', texto)
    # Quebra de linha do DXF (\P) vira espaço
    texto = texto.replace("\\P", " ")
    # Remove chaves usadas em blocos de formatação
    texto = texto.replace("{", "").replace("}", "")
    # Compacta espaços
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def _extrair_textos_do_bloco(bloco, coletor):
    """Lê TEXT/MTEXT/ATTRIB/ATTDEF dentro de um bloco (recursivo)."""
    for e in bloco:
        tipo = e.dxftype()

        if tipo == "TEXT":
            t = e.dxf.text.strip()
            if t:
                coletor.append(t)

        elif tipo == "MTEXT":
            limpo = limpar_mtexto(e.text)
            if limpo:
                coletor.append(limpo)

        elif tipo in ("ATTRIB", "ATTDEF"):
            t = e.dxf.text.strip()
            if t:
                coletor.append(t)

        elif tipo == "INSERT":
            try:
                sub = bloco.doc.blocks.get(e.dxf.name)
                _extrair_textos_do_bloco(sub, coletor)
            except Exception:
                pass


def ler_dxf(caminho):
    """Lê DXF e retorna SOMENTE lista de strings (como antes)."""
    textos = []

    try:
        doc = ezdxf.readfile(caminho)
        msp = doc.modelspace()
    except Exception as e:
        print(f"[READER] Erro ao ler DXF: {e}")
        return []

    for e in msp:
        tipo = e.dxftype()

        if tipo == "TEXT":
            t = e.dxf.text.strip()
            if t:
                textos.append(t)

        elif tipo == "MTEXT":
            limpo = limpar_mtexto(e.text)
            if limpo:
                textos.append(limpo)

        elif tipo in ("ATTRIB", "ATTDEF"):
            t = e.dxf.text.strip()
            if t:
                textos.append(t)

        elif tipo == "INSERT":
            try:
                bloco = doc.blocks.get(e.dxf.name)
                _extrair_textos_do_bloco(bloco, textos)
            except Exception:
                pass

    print(f"[READER] Total de textos extraídos: {len(textos)}")
    return textos


def ler_dwg(caminho):
    """Por enquanto, DWG não implementado."""
    print("[READER] Leitura de DWG não implementada")
    return []
