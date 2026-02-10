# process_tokens_local_v2.py
# Versão aprimorada local: processa tokens_raw_final.csv e gera romaneio com associação automática de VIGA
#
# - Detecta títulos de viga (V..., VM..., etc.) nos tokens
# - Para cada token (e sub-tokens) tenta extrair POS (N#), BIT (Ø / %%C / número), COMP (C= or heuristic)
# - Associa cada item à VIGA mais próxima (por distância euclidiana entre token e título)
# - Gera:
#     romaneio_detalhado_final.csv
#     romaneio_final.csv
#     suspeitas_final.csv
#     failed_tokens.csv
#
# Uso:
#   1) coloque este arquivo na mesma pasta de tokens_raw_final.csv
#   2) rode: python process_tokens_local_v2.py
#
# Requisitos: Python 3.6+
#
from __future__ import annotations
import csv, re, math, os, sys
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

TOKENS_RAW = "tokens_raw_final.csv"
DETAILED_OUT = "romaneio_detalhado_final.csv"
ROMANEIO_OUT = "romaneio_final.csv"
SUSPEITAS_OUT = "suspeitas_final.csv"
FAILED_OUT = "failed_tokens.csv"

# pesos e bitolas
PESOS_ACO = {4.2:0.109,5.0:0.154,6.0:0.222,6.3:0.245,8.0:0.395,10.0:0.617,12.5:0.963,16.0:1.578,20.0:2.466,25.0:3.853,28.0:4.83,32.0:6.313}
BITOLAS = sorted(PESOS_ACO.keys())
BIT_TOL = 0.6

# regexes
RE_NUM = re.compile(r'\d+(?:[.,]\d+)?')
RE_POS_FULL = re.compile(r'^\s*N0*(\d{1,4})\s*$', re.IGNORECASE)
RE_POS_EMBED = re.compile(r'\bN0*(\d{1,4})\b', re.IGNORECASE)
RE_PAREN_POS = re.compile(r'^\s*\(\s*(\d{1,4})\s*\)\s*N0*(\d{1,4})\s*$', re.IGNORECASE)
RE_BIT_O = re.compile(r'Ø\s*([0-9]+(?:[.,][0-9]+)?)')
RE_BIT_PCT = re.compile(r'%{2}C\s*([0-9]+(?:[.,][0-9]+)?)', re.IGNORECASE)
RE_C_EQ = re.compile(r'\b[C|L]\s*=\s*(\d+(?:[.,]\d+)?)', re.IGNORECASE)
RE_VIGA = re.compile(r'\b(?:VIGA|VM|VC|VB|V-?|V)\s*([0-9A-Z]*\d[0-9A-Z]*)\b', re.IGNORECASE)
RE_SHAPE = re.compile(r'\b(\d{1,5})\s*[xX×]\s*(\d{1,5})\b', re.IGNORECASE)

INSTRUCTION_KEYWORDS = ("COLOCAR","OBS","CORTE","DO BLOCO","PINO","P/","AVISO","REVISÃO","FOLHA","ESCALA","ATENÇÃO","NOTA")

def cleanup(s: str) -> str:
    if s is None: return ''
    s2 = s.replace('%%C','Ø').replace('\\P','').replace('\\H','').replace('\\W','').replace(',', '.')
    s2 = re.sub(r'\s+', ' ', s2)
    return s2.strip()

def nearest_bitola(val: float) -> Optional[float]:
    best=None; bd=1e9
    for b in BITOLAS:
        d = abs(b - val)
        if d < bd:
            bd = d; best = b
    return best if bd <= BIT_TOL else None

def extract_qty_prefix(txt: str) -> Tuple[int,str]:
    m = re.match(r'^\s*(\d+)\s*[x×]?\s*', txt)
    if m:
        try:
            q = int(m.group(1)); return q, txt[m.end():].strip()
        except: pass
    return 1, txt

def parse_subtoken(txt: str, x: float, y: float, all_tokens: List[Dict]) -> Optional[Dict]:
    txt_raw = txt or ''
    txtc = cleanup(txt_raw)
    if not txtc: return None
    if any(k in txtc.upper() for k in INSTRUCTION_KEYWORDS): return None
    if RE_SHAPE.search(txtc): return None

    qty, rest = extract_qty_prefix(txtc)

    # POS
    pos = None
    m_paren = RE_PAREN_POS.match(rest)
    if m_paren:
        pos = f"N{m_paren.group(2)}"
    if not pos:
        m_full = RE_POS_FULL.match(rest.strip())
        if m_full:
            pos = f"N{m_full.group(1)}"
    if not pos:
        m_emb = RE_POS_EMBED.search(rest)
        if m_emb:
            pos = f"N{m_emb.group(1)}"

    # BIT
    bit = None
    m = RE_BIT_O.search(rest)
    if m:
        try:
            nb = nearest_bitola(float(m.group(1).replace(',','.')))
            if nb: bit = nb
        except: pass
    if not bit:
        m = RE_BIT_PCT.search(rest)
        if m:
            try:
                nb = nearest_bitola(float(m.group(1).replace(',','.')))
                if nb: bit = nb
            except: pass
    if not bit:
        for n in RE_NUM.findall(rest):
            try:
                nv = float(n.replace(',','.')); nb = nearest_bitola(nv)
                if nb:
                    bit = nb; break
            except: pass

    # COMP
    comp = None
    m = RE_C_EQ.search(rest)
    if m:
        try:
            v = float(m.group(1).replace(',','.')); comp = v/100.0 if v>25 else v
        except: comp=None

    # two-number heuristic (e.g., "13 1415" -> qty=13 comp=14.15)
    if comp is None:
        nums = [n.replace(',','.') for n in RE_NUM.findall(rest)]
        if len(nums) >= 2:
            try:
                a = float(nums[0]); b = float(nums[1])
                if a >= 100.0 and b <= 50.0:
                    comp = a/100.0
                    qty = int(b) if float(b).is_integer() else qty
                elif b >= 100.0 and a <= 50.0:
                    comp = b/100.0
                    qty = int(a) if float(a).is_integer() else qty
            except:
                pass
    if comp is None:
        # take largest numeric not a bitola
        nums_f = []
        for n in RE_NUM.findall(rest):
            try:
                nv = float(n.replace(',','.'))
                if nearest_bitola(nv) is None:
                    nums_f.append(nv)
            except:
                pass
        if nums_f:
            v = max(nums_f)
            comp = (v/100.0) if v>25 else v

    # neighbor borrow for bit if missing
    if pos and not bit:
        for tk in all_tokens:
            if abs(tk['y'] - y) <= 1.0 and abs(tk['x'] - x) <= 8.0:
                tn = tk['text']
                m1 = RE_BIT_O.search(tn)
                if m1:
                    try:
                        nb = nearest_bitola(float(m1.group(1).replace(',','.')))
                        if nb:
                            bit = nb; break
                    except: pass
                m2 = RE_BIT_PCT.search(tn)
                if m2:
                    try:
                        nb = nearest_bitola(float(m2.group(1).replace(',','.')))
                        if nb:
                            bit = nb; break
                    except: pass
                for nn in RE_NUM.findall(tn):
                    try:
                        nv = float(nn.replace(',','.')); nb = nearest_bitola(nv)
                        if nb:
                            bit = nb; break
                    except: pass
            if bit: break

    if not pos or not bit or comp is None:
        return None

    if comp > 25.0:
        comp = comp / 100.0
    if not (0.01 <= comp <= 30.0):
        return None

    w_unit = PESOS_ACO.get(bit, 0.0)
    return {'p': pos, 'b': bit, 'c': round(comp,3), 'qty': qty, 'w_unit': w_unit, 'x': x, 'y': y, 'txt': txt_raw}

def read_tokens(path: str) -> List[Dict]:
    toks = []
    with open(path, newline='', encoding='utf-8') as f:
        r = csv.reader(f)
        hdr = [h.strip().upper() for h in next(r)]
        try:
            ti = hdr.index('TEXT')
            xi = hdr.index('X')
            yi = hdr.index('Y')
        except ValueError:
            raise RuntimeError("Cabeçalho inválido em tokens_raw_final.csv (precisa conter TEXT,X,Y)")
        for row in r:
            text = row[ti]
            x = float(row[xi]) if row[xi] else 0.0
            y = float(row[yi]) if row[yi] else 0.0
            toks.append({'text': text.strip(), 'x': x, 'y': y})
    return toks

def find_titles(tokens: List[Dict]) -> List[Dict]:
    titles = []
    for tk in tokens:
        m = RE_VIGA.search(tk['text'] or '')
        if m:
            name = m.group(0).replace("VIGA","V").replace(" ","").upper()
            titles.append({'nome': name, 'x': tk['x'], 'y': tk['y'], 'token': tk})
    return titles

def assign_viga_by_nearest(title_list: List[Dict], x: float, y: float) -> str:
    if not title_list:
        return 'V_GERAL'
    best = min(title_list, key=lambda t: math.hypot(t['x'] - x, t['y'] - y))
    return best['nome']

def main():
    if not os.path.exists(TOKENS_RAW):
        print("Arquivo tokens_raw_final.csv não encontrado. Coloque na mesma pasta e rode novamente.")
        return
    tokens = read_tokens(TOKENS_RAW)
    titles = find_titles(tokens)
    detailed_rows = []
    failed = []
    # parse each token, split moderately (on ';' or '/') and also keep whole token
    for tk in tokens:
        parts = re.split(r'[;/\|]', tk['text']) if (';' in tk['text'] or '/' in tk['text'] or '|' in tk['text']) else [tk['text']]
        for part in parts:
            part = part.strip()
            if not part:
                continue
            info = parse_subtoken(part, tk['x'], tk['y'], tokens)
            if info:
                viga = assign_viga_by_nearest(titles, info['x'], info['y'])
                peso_total = round(info['w_unit'] * info['qty'] * info['c'], 2)
                detailed_rows.append([viga, info['p'], info['b'], info['qty'], info['c'], peso_total, part, info['x'], info['y'], 'ACCEPT'])
            else:
                # try mark REVIEW if we have pos embedded or some hint
                mpos = RE_POS_EMBED.search(part)
                pos = f"N{mpos.group(1)}" if mpos else ''
                # try bit
                bit_val = ''
                mbit = RE_BIT_O.search(part) or RE_BIT_PCT.search(part)
                if mbit:
                    try:
                        bv = float(mbit.group(1).replace(',','.')); nb = nearest_bitola(bv)
                        bit_val = nb or ''
                    except:
                        bit_val = ''
                # comp
                comp_val = ''
                mc = RE_C_EQ.search(part)
                if mc:
                    try:
                        v = float(mc.group(1).replace(',','.')); comp_val = v/100.0 if v>25 else v
                    except:
                        comp_val = ''
                viga = assign_viga_by_nearest(titles, tk['x'], tk['y'])
                detailed_rows.append([viga, pos, bit_val, 1, comp_val or '', 0.0, part, tk['x'], tk['y'], 'REVIEW'])
                failed.append([part, tk['x'], tk['y'], viga, pos, bit_val, comp_val or ''])
    # write detailed
    with open(DETAILED_OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['VIGA','POS','BIT(mm)','QTD','COMP(m)','PESO(kg)','TOKEN_TEXT','TOKEN_X','TOKEN_Y','ACTION'])
        for row in detailed_rows:
            w.writerow(row)
    # write suspects
    with open(SUSPEITAS_OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['VIGA','POS','BIT(mm)','QTD','COMP(m)','PESO(kg)','TOKEN_TEXT','TOKEN_X','TOKEN_Y','ACTION'])
        for row in detailed_rows:
            if row[9] == 'REVIEW':
                w.writerow(row)
    # aggregate accepted rows
    summary = defaultdict(lambda: {'q':0,'p':0.0})
    for row in detailed_rows:
        if row[9] != 'ACCEPT': continue
        key = (row[0], row[1], float(row[2]), float(row[4]))
        summary[key]['q'] += int(row[3])
        summary[key]['p'] += float(row[5])
    with open(ROMANEIO_OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['VIGA','POS','BIT(mm)','QTD','COMP(m)','PESO(kg)'])
        for (viga,pos,bit,comp), v in summary.items():
            w.writerow([viga,pos,bit,v['q'],comp, round(v['p'],2)])
    # failed tokens
    with open(FAILED_OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['TOKEN_TEXT','TOKEN_X','TOKEN_Y','VIGA','POS','BIT','COMP'])
        for row in failed:
            w.writerow(row)
    print("Gerado:", DETAILED_OUT, ROMANEIO_OUT, SUSPEITAS_OUT, FAILED_OUT)
    print("Linhas detalhadas:", len(detailed_rows), "falhas:", len(failed))

if __name__ == '__main__':
    main()