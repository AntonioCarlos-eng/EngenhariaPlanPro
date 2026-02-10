#!/usr/bin/env python3
# core/debug_textos_v2.py
# Depuração: extrai textos do DXF com coordenadas e imprime janelas por viga.
# Uso:
#   python core/debug_textos_v2.py "caminho/para/arquivo.dxf" --viga V10 --max 200
#   ou sem --viga para todo o arquivo
import os
import sys
import re
import argparse
try:
    import ezdxf
except Exception:
    print("Erro: ezdxf não instalado. Execute: pip install ezdxf")
    sys.exit(1)

RE_VIGA = re.compile(r'^[Vv][A-Za-z0-9]*\d+$')
RE_POS = re.compile(r'\bN(\d{1,4})\b', re.IGNORECASE)
RE_BIT = re.compile(r'(?:Ø|⌀|%+C)?\s*0*([0-9]{1,2}(?:[.,][0-9]+)?)', re.IGNORECASE)
RE_X_QTY = re.compile(r'[x×]\s*(\d{1,6})', re.IGNORECASE)
RE_N_PAREN = re.compile(r'\bN\d{1,4}\b\s*\(\s*(\d{1,6})\s*\)')
RE_C_EQ = re.compile(r'C\s*=\s*([0-9]{1,4}(?:[.,][0-9]+)?)', re.IGNORECASE)
RE_CA = re.compile(r'\bCA[-\s]?(50|60)\b', re.IGNORECASE)
RE_DISTRIB = re.compile(r'\bC[\/\\]\s*\d+\b', re.IGNORECASE)

def extract_texts_with_coords(path):
    items = []
    doc = ezdxf.readfile(path)
    # modelspace
    try:
        msp = doc.modelspace()
        for e in msp:
            try:
                t = None
                if e.dxftype() == "TEXT":
                    t = e.dxf.text
                    ins = getattr(e.dxf, "insert", None)
                    x,y = (round(float(ins[0]),3), round(float(ins[1]),3)) if ins else (None,None)
                elif e.dxftype() == "MTEXT":
                    t = e.plain_text()
                    ins = getattr(e, "insert", None) if hasattr(e, "insert") else None
                    x,y = (round(float(ins[0]),3), round(float(ins[1]),3)) if ins else (None,None)
                elif e.dxftype() == "ATTRIB":
                    t = e.dxf.text
                    ins = getattr(e.dxf, "insert", None)
                    x,y = (round(float(ins[0]),3), round(float(ins[1]),3)) if ins else (None,None)
                elif e.dxftype() == "INSERT" and hasattr(e, "attribs") and e.attribs:
                    for att in e.attribs:
                        ta = att.dxf.text if hasattr(att.dxf, "text") else None
                        pos = None
                        try:
                            pos_attr = getattr(att.dxf, "insert", None)
                            if pos_attr:
                                px = round(float(pos_attr[0]),3); py = round(float(pos_attr[1]),3)
                            else:
                                px = py = None
                        except Exception:
                            px = py = None
                        items.append({"text": str(ta).strip() if ta else "", "x": px, "y": py, "type": "ATTRIB"})
                    continue
                else:
                    continue
                if t is None:
                    continue
                items.append({"text": str(t).strip(), "x": x, "y": y, "type": e.dxftype()})
            except Exception:
                continue
    except Exception:
        pass

    # layouts
    try:
        for ln in doc.layouts.names():
            try:
                layout = doc.layouts.get(ln)
                for e in layout.query("TEXT MTEXT ATTRIB INSERT"):
                    try:
                        if e.dxftype() == "TEXT":
                            ins = getattr(e.dxf, "insert", None)
                            x,y = (round(float(ins[0]),3), round(float(ins[1]),3)) if ins else (None,None)
                            items.append({"text": str(e.dxf.text).strip(), "x": x, "y": y, "type": "TEXT"})
                        elif e.dxftype() == "MTEXT":
                            ins = getattr(e, "insert", None) if hasattr(e, "insert") else None
                            x,y = (round(float(ins[0]),3), round(float(ins[1]),3)) if ins else (None,None)
                            items.append({"text": str(e.plain_text()).strip(), "x": x, "y": y, "type": "MTEXT"})
                        elif e.dxftype() == "ATTRIB":
                            ins = getattr(e.dxf, "insert", None)
                            x,y = (round(float(ins[0]),3), round(float(ins[1]),3)) if ins else (None,None)
                            items.append({"text": str(e.dxf.text).strip(), "x": x, "y": y, "type": "ATTRIB"})
                        elif e.dxftype() == "INSERT" and hasattr(e, "attribs") and e.attribs:
                            for att in e.attribs:
                                ta = att.dxf.text if hasattr(att.dxf, "text") else None
                                pos = None
                                try:
                                    pos_attr = getattr(att.dxf, "insert", None)
                                    if pos_attr:
                                        px = round(float(pos_attr[0]),3); py = round(float(pos_attr[1]),3)
                                    else:
                                        px = py = None
                                except Exception:
                                    px = py = None
                                items.append({"text": str(ta).strip() if ta else "", "x": px, "y": py, "type": "ATTRIB"})
                    except Exception:
                        continue
            except Exception:
                continue
    except Exception:
        pass

    # blocks
    try:
        for bn in doc.blocks.names():
            try:
                block = doc.blocks.get(bn)
                for e in block:
                    try:
                        if e.dxftype() in ("TEXT","MTEXT","ATTRIB"):
                            t = e.dxf.text if e.dxftype() != "MTEXT" else e.plain_text()
                            items.append({"text": str(t).strip(), "x": None, "y": None, "type": e.dxftype()})
                    except Exception:
                        continue
            except Exception:
                continue
    except Exception:
        pass

    return items

def filtrar_textos(items):
    return [it for it in items if it.get("text","").strip()]

def analyze(tokens, focus_viga=None, max_lines=200):
    texts = [t["text"] for t in tokens]
    viga_indices = []
    for i,t in enumerate(texts):
        if RE_VIGA.match(t):
            viga_indices.append((i,t.upper()))
    groups = []
    if not viga_indices:
        groups = [("NO_VIGA", 0, len(texts))]
    else:
        for vi in range(len(viga_indices)):
            start_idx = viga_indices[vi][0]
            vname = viga_indices[vi][1]
            end_idx = viga_indices[vi+1][0] if vi+1 < len(viga_indices) else len(texts)
            groups.append((vname, start_idx+1, end_idx))
    printed = 0
    for vname, s, e in groups:
        if focus_viga and vname != focus_viga:
            continue
        print(f"\n==== GRUPO VIGA: {vname} tokens[{s}:{e}] ====")
        for idx in range(s, e):
            if printed >= max_lines:
                print("-- max lines reached --")
                return
            tok = tokens[idx]
            txt = tok["text"]
            x = tok["x"]; y = tok["y"]
            win = tokens[idx : min(idx+8, e)]
            win_texts = [w["text"] for w in win]
            win_str = " | ".join(win_texts)
            pos = RE_POS.search(win_str)
            pos_s = pos.group(0) if pos else ""
            bit_m = RE_BIT.search(win_str)
            bit_s = bit_m.group(1) if bit_m else ""
            xqty = RE_X_QTY.search(win_str)
            xqty_s = xqty.group(1) if xqty else ""
            nparen = RE_N_PAREN.search(win_str)
            nparen_s = nparen.group(1) if nparen else ""
            c_eq = RE_C_EQ.search(win_str)
            c_eq_s = c_eq.group(1) if c_eq else ""
            ca = RE_CA.search(win_str)
            ca_s = ca.group(0) if ca else ""
            distrib = bool(RE_DISTRIB.search(win_str))
            print(f"[{idx}] ({x},{y}) '{txt}'")
            print(f"      win: '{win_str[:120]}'")
            print(f"      features: POS={pos_s} BIT={bit_s} XQTY={xqty_s} N_PAREN={nparen_s} C={c_eq_s} CA={ca_s} DISTRIB={distrib}")
            printed += 1
    if printed == 0:
        print("Nenhum grupo impresso (verifique --viga).")

def main():
    parser = argparse.ArgumentParser(description="Debug textos DXF para motor V2")
    parser.add_argument("dxf", help="arquivo DXF")
    parser.add_argument("--viga", help="filtrar por viga (ex: V10)", default=None)
    parser.add_argument("--max", type=int, help="max lines to print", default=200)
    args = parser.parse_args()
    if not os.path.exists(args.dxf):
        print("Arquivo não encontrado:", args.dxf)
        return
    items = extract_texts_with_coords(args.dxf)
    tokens = filtrar_textos(items)
    print(f"Total tokens extraídos: {len(tokens)}")
    analyze(tokens, focus_viga=(args.viga.upper() if args.viga else None), max_lines=args.max)

if __name__ == "__main__":
    main()