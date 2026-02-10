#!/usr/bin/env python3
# core/extract_tokens.py
# Extrai todos os textos do DXF com coordenadas (quando disponíveis)
# Saída: <dxf_filename>_tokens.json contendo:
# { "filename": "...", "tokens": [ { "text": "...", "x": float|null, "y": float|null, "type": "TEXT/MTEXT/ATTRIB", "index": int }, ... ] }
#
# Uso:
#   python core/extract_tokens.py "caminho/para/arquivo.dxf"
#
import os
import sys
import json
import math

try:
    import ezdxf
except Exception:
    print("ezdxf não instalado. Instale com: pip install ezdxf")
    sys.exit(1)

def round_maybe(v):
    try:
        return round(float(v), 6)
    except Exception:
        return None

def extract(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    doc = ezdxf.readfile(path)
    items = []
    idx = 0

    def push(text, x, y, etype):
        nonlocal idx
        if text is None:
            return
        s = str(text).strip()
        if not s:
            return
        items.append({
            "index": idx,
            "text": s,
            "x": round_maybe(x),
            "y": round_maybe(y),
            "type": etype
        })
        idx += 1

    # modelspace
    msp = doc.modelspace()
    for e in msp:
        try:
            ttype = e.dxftype()
            if ttype == "TEXT":
                ins = getattr(e.dxf, "insert", None)
                x = ins[0] if ins else None
                y = ins[1] if ins else None
                push(e.dxf.text, x, y, "TEXT")
            elif ttype == "MTEXT":
                # MTEXT position can be .insert or .get_insert_location
                try:
                    ins = getattr(e, "insert", None)
                except Exception:
                    ins = None
                x = ins[0] if ins else None
                y = ins[1] if ins else None
                push(e.plain_text(), x, y, "MTEXT")
            elif ttype == "ATTRIB":
                ins = getattr(e.dxf, "insert", None)
                x = ins[0] if ins else None
                y = ins[1] if ins else None
                push(e.dxf.text, x, y, "ATTRIB")
            elif ttype == "INSERT" and hasattr(e, "attribs") and e.attribs:
                # push each attrib (position not always available)
                for att in e.attribs:
                    try:
                        ins = getattr(att.dxf, "insert", None)
                    except Exception:
                        ins = None
                    x = ins[0] if ins else None
                    y = ins[1] if ins else None
                    push(att.dxf.text, x, y, "ATTRIB")
        except Exception:
            continue

    # layouts (paperspace) and blocks
    try:
        for ln in doc.layouts.names():
            try:
                layout = doc.layouts.get(ln)
                for e in layout.query("TEXT MTEXT ATTRIB INSERT"):
                    try:
                        ttype = e.dxftype()
                        if ttype == "TEXT":
                            ins = getattr(e.dxf, "insert", None)
                            x = ins[0] if ins else None
                            y = ins[1] if ins else None
                            push(e.dxf.text, x, y, "TEXT")
                        elif ttype == "MTEXT":
                            ins = getattr(e, "insert", None) if hasattr(e, "insert") else None
                            x = ins[0] if ins else None
                            y = ins[1] if ins else None
                            push(e.plain_text(), x, y, "MTEXT")
                        elif ttype == "ATTRIB":
                            ins = getattr(e.dxf, "insert", None)
                            x = ins[0] if ins else None
                            y = ins[1] if ins else None
                            push(e.dxf.text, x, y, "ATTRIB")
                        elif ttype == "INSERT" and hasattr(e, "attribs") and e.attribs:
                            for att in e.attribs:
                                ins = getattr(att.dxf, "insert", None)
                                x = ins[0] if ins else None
                                y = ins[1] if ins else None
                                push(att.dxf.text, x, y, "ATTRIB")
                    except Exception:
                        continue
            except Exception:
                continue
    except Exception:
        pass

    # blocks (best-effort)
    try:
        for bn in doc.blocks.names():
            try:
                block = doc.blocks.get(bn)
                for e in block:
                    try:
                        ttype = e.dxftype()
                        if ttype == "TEXT":
                            push(e.dxf.text, None, None, "BLOCK_TEXT")
                        elif ttype == "MTEXT":
                            push(e.plain_text(), None, None, "BLOCK_MTEXT")
                        elif ttype == "ATTRIB":
                            push(e.dxf.text, None, None, "BLOCK_ATTRIB")
                    except Exception:
                        continue
            except Exception:
                continue
    except Exception:
        pass

    return items

def main():
    if len(sys.argv) < 2:
        print("Uso: python core/extract_tokens.py arquivo.dxf")
        sys.exit(1)
    path = sys.argv[1]
    outname = os.path.splitext(os.path.basename(path))[0] + "_tokens.json"
    try:
        items = extract(path)
    except Exception as e:
        print("Erro ao extrair:", e)
        sys.exit(1)
    payload = {"source": os.path.basename(path), "count": len(items), "tokens": items}
    with open(outname, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Tokens salvos em: {outname} (count={len(items)})")

if __name__ == "__main__":
    main()