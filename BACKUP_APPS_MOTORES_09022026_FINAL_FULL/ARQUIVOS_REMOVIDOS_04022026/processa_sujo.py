#!/usr/bin/env python3
# processa_sujo.py
# Script único para ler um CSV "sujo" de tokens (tokens_raw_final.csv),
# recuperar linhas, extrair POS/BIT/COMP/QTD, associar à VIGA mais próxima
# e gerar:
#  - romaneio_detalhado_final.csv
#  - romaneio_final.csv
#  - suspeitas_final.csv
#
# Uso:
#   python processa_sujo.py [tokens_raw_final.csv]
#
import csv, re, sys, os, math
from collections import defaultdict, Counter
from typing import List, Dict, Optional, Tuple

# Config simples
BITOS = {4.2:0.109,5.0:0.154,6.0:0.222,6.3:0.245,8.0:0.395,10.0:0.617,12.5:0.963,16.0:1.578,20.0:2.466,25.0:3.853,28.0:4.83,32.0:6.313}
BIT_LIST = sorted(BITOS.keys())
BIT_TOL = 0.6

RE_NUM = re.compile(r'\d+(?:[.,]\d+)?')
RE_POS = re.compile(r'\bN0*(\d{1,4})\b', re.IGNORECASE)
RE_POS_FULL = re.compile(r'^\s*N0*(\d{1,4})\s*$', re.IGNORECASE)
RE_BIT_O = re.compile(r'Ø\s*([0-9]+(?:[.,][0-9]+)?)')
RE_BIT_PCT = re.compile(r'%{2}C\s*([0-9]+(?:[.,][0-9]+)?)', re.IGNORECASE)
RE_C_EQ = re.compile(r'\b[C|L]\s*=\s*(\d+(?:[.,]\d+)?)', re.IGNORECASE)
RE_VIGA = re.compile(r'\b(?:VIGA|VM|VC|VB|V-?|V)\s*([0-9A-Z]*\d[0-9A-Z]*)\b', re.IGNORECASE)
RE_SHAPE = re.compile(r'\b\d+\s*[xX×]\s*\d+\b')

def nearest_bitola(val: float) -> Optional[float]:
    best=None; bd=1e9
    for b in BIT_LIST:
        d = abs(b - val)
        if d < bd:
            bd = d; best = b
    return best if bd <= BIT_TOL else None

def norm_text(s: str) -> str:
    if s is None: return ''
    s = s.replace('%%C','Ø').replace(',', '.').replace('\\P','').replace('\\H','')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def read_flexible(path: str) -> List[Dict]:
    """
    Tenta ler linhas de arquivo mesmo que 'sujo'.
    Para cada linha tenta extrair:
      - TEXT (string)
      - X (float) Y (float) se encontrados (usa os dois últimos números como X,Y com heurística)
      - H,LAYER,SOURCE se disponíveis (opcionais)
    Retorna lista de dicts {'text','x','y','raw'}
    """
    out=[]
    if not os.path.exists(path):
        print("Arquivo não encontrado:", path); return out
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for ln in f:
            line = ln.strip()
            if not line: continue
            # ignore common header lines repeated
            up = line.upper()
            if 'TEXT' in up and 'X' in up and 'Y' in up:
                continue
            # try CSV parse first
            try:
                row = next(csv.reader([line]))
            except Exception:
                row = [line]
            # if row looks normal (>=3 cols): try to find numeric X,Y by scanning fields
            nums=[]
            for i,c in enumerate(row):
                # find numeric tokens inside field
                for m in RE_NUM.findall(c):
                    try:
                        nums.append(float(m.replace(',','.')))
                    except:
                        pass
            x=None; y=None; text=None
            if len(nums) >= 2:
                # take last two numeric occurrences as candidate X,Y
                y = nums[-1]; x = nums[-2]
                # reconstruct text as everything before the first of those numeric fields in row (best effort)
                # locate field index of x and y by searching reversed
                idx_x = None
                idx_y = None
                # locate positions in the original row where numeric matches occur
                flat = []
                for c in row:
                    for m in RE_NUM.findall(c):
                        flat.append((c,m))
                # find indices - fallback if not found
                text_fields = []
                # Conservative approach: treat first column as TEXT unless it's a pure number
                if len(row) >= 3:
                    # guess TEXT = join of leftmost non-numeric-like fields
                    left_parts=[]
                    for c in row[:-2]:
                        left_parts.append(c)
                    text = ','.join(left_parts).strip()
                else:
                    # fallback: text is row[0] with numbers removed
                    text = re.sub(r'\d+(?:[.,]\d+)?','', row[0]).strip()
            else:
                # no numbers or insufficient; fallback: try to extract trailing coords with regex
                m = re.search(r'(-?\d+(?:[.,]\d+)?)[^\d\-]*(-?\d+(?:[.,]\d+)?)\s*$', line)
                if m:
                    try:
                        x = float(m.group(1).replace(',','.')); y = float(m.group(2).replace(',','.'))
                        text = line[:m.start()].strip().rstrip(',').strip()
                    except:
                        text = line
                else:
                    text = line
            text = norm_text(text)
            if isinstance(x, float) and isinstance(y, float):
                out.append({'text': text, 'x': float(x), 'y': float(y), 'raw': line})
            else:
                # keep even without coords (so we can try match POS or VIGA)
                out.append({'text': text, 'x': None, 'y': None, 'raw': line})
    return out

def extract_token_info(text: str, x: Optional[float], y: Optional[float], neighbors: List[Dict]) -> Optional[Dict]:
    """
    Tenta extrair POS, BIT, COMP, QTD de um texto
    Retorna dict {'p','b','c','qty','x','y'} ou None se falhar
    """
    if not text or len(text.strip())==0:
        return None
    T = text.upper()
    # ignore legends / shapes
    if any(k in T for k in ('AÇO','PESO','RESUMO','BIT(','BITOLA','COMPRIMENT','TOTAL','UNIT','TAB')):
        return None
    if RE_SHAPE.search(text):
        return None
    # normalize
    s = text
    # qty prefix
    qty = 1
    m_qty = re.match(r'^\s*(\d+)\s*[x×]?\s*(.*)$', s)
    if m_qty:
        try:
            qty = int(m_qty.group(1))
            s = m_qty.group(2).strip()
        except:
            qty = 1
    # POS
    pos = None
    m = RE_POS_FULL.match(s)
    if m:
        pos = 'N'+m.group(1)
    else:
        m2 = RE_POS.search(s)
        if m2:
            pos = 'N'+m2.group(1)
    # BIT
    bit = None
    m = RE_BIT_O.search(s)
    if m:
        try:
            nb = nearest_bitola(float(m.group(1).replace(',','.')))
            if nb: bit = nb
        except: pass
    if not bit:
        m = RE_BIT_PCT.search(s)
        if m:
            try:
                nb = nearest_bitola(float(m.group(1).replace(',','.')))
                if nb: bit = nb
            except: pass
    if not bit:
        # scan numbers and check if they match bitola list
        for n in RE_NUM.findall(s):
            try:
                nv=float(n.replace(',','.'))
                nb = nearest_bitola(nv)
                if nb:
                    bit = nb; break
            except: pass
    # COMP
    comp = None
    m = RE_C_EQ.search(s)
    if m:
        try:
            v=float(m.group(1).replace(',','.'))
            comp = v/100.0 if v>25 else v
        except: pass
    # two-number heuristic: if text has two numbers, small + large => qty+comp(mm)
    nums = [float(n.replace(',','.')) for n in RE_NUM.findall(s)]
    if comp is None and len(nums) >= 2:
        a = nums[0]; b = nums[1]
        try:
            if a <= 50 and b >= 100:
                qty = int(a) if a.is_integer() else qty
                comp = b/100.0
            elif b <= 50 and a >= 100:
                qty = int(b) if b.is_integer() else qty
                comp = a/100.0
        except:
            pass
    # fallback: largest numeric not a bitola
    if comp is None and nums:
        candidates = [n for n in nums if nearest_bitola(n) is None]
        if candidates:
            v = max(candidates)
            comp = v/100.0 if v>25 else v
    # borrow bit from neighbors (same line close y)
    if pos and bit is None and neighbors:
        for nt in neighbors:
            if nt is None: continue
            nx = nt.get('x'); ny = nt.get('y')
            if nx is None or ny is None or x is None or y is None:
                continue
            if abs(ny - y) <= 1.5 and abs(nx - x) <= 10.0:
                ttt = nt.get('text','')
                m1 = RE_BIT_O.search(ttt); m2 = RE_BIT_PCT.search(ttt)
                if m1:
                    try:
                        nb = nearest_bitola(float(m1.group(1).replace(',','.')))
                        if nb: bit = nb; break
                    except: pass
                if m2:
                    try:
                        nb = nearest_bitola(float(m2.group(1).replace(',','.')))
                        if nb: bit = nb; break
                    except: pass
                for nn in RE_NUM.findall(ttt):
                    try:
                        nv=float(nn.replace(',','.')); nb=nearest_bitola(nv)
                        if nb:
                            bit = nb; break
                    except: pass
            if bit: break
    if not pos or not bit or comp is None:
        return None
    # sanitize comp
    try:
        if comp > 25.0: comp = comp/100.0
        if not (0.01 <= comp <= 30.0):
            return None
    except:
        return None
    return {'p': pos, 'b': bit, 'c': round(comp,3), 'qty': qty, 'x': x, 'y': y, 'text': text}

def associate_viga_titles(tokens: List[Dict]) -> List[Dict]:
    """
    Detecta tokens título de VIGA (usando RE_VIGA) e associa cada token à viga mais próxima por distância.
    Retorna tokens com campo 'viga' preenchido.
    """
    titles=[]
    for t in tokens:
        txt = t.get('text','') or ''
        m = RE_VIGA.search(txt)
        if m and t.get('x') is not None and t.get('y') is not None:
            name = m.group(0).replace('VIGA','V').replace(' ','').upper()
            titles.append({'nome': name, 'x': t['x'], 'y': t['y']})
    # if no titles, leave viga as V_GERAL
    for t in tokens:
        if titles and t.get('x') is not None and t.get('y') is not None:
            best = min(titles, key=lambda tt: math.hypot(tt['x']-t['x'], tt['y']-t['y']))
            t['viga'] = best['nome']
        else:
            t['viga'] = 'V_GERAL'
    return tokens

def process_file(path_in: str):
    tokens = read_flexible(path_in)
    if not tokens:
        print("Nenhum token lido. Saindo.")
        return
    # fix missing x,y: try to interpolate from nearby tokens same line by ordering by y
    # First, assign approximate y if missing by grouping by textual line order (no coords)
    # But simplest: leave None as-is; parse_subtoken will fail if nothing enough.
    # Associate viga titles
    tokens = associate_viga_titles(tokens)
    detailed = []
    # for neighbor lookups pass whole token list (we already have coords maybe)
    for t in tokens:
        txt = t.get('text','')
        x = t.get('x'); y = t.get('y')
        # split common separators
        parts = re.split(r'[;/\|]', txt) if (';' in txt or '/' in txt or '|' in txt) else [txt]
        for p in parts:
            p = p.strip()
            if not p: continue
            info = extract_token_info(p, x, y, tokens)
            if info:
                peso_unit = BITOS.get(info['b'], 0.0)
                peso_total = round(peso_unit * info['qty'] * info['c'], 2)
                detailed.append({
                    'VIGA': t.get('viga','V_GERAL'),
                    'POS': info['p'],
                    'BIT': info['b'],
                    'QTD': info['qty'],
                    'COMP(m)': info['c'],
                    'PESO(kg)': peso_total,
                    'POS_ORIGIN': 'self',
                    'BIT_ORIGIN': 'self',
                    'COMP_ORIGIN': 'self',
                    'TOKEN_TEXT': p,
                    'TOKEN_X': x if x is not None else '',
                    'TOKEN_Y': y if y is not None else '',
                    'ACTION': 'ACCEPT'
                })
            else:
                # produce REVIEW entry; try to extract POS if present
                mpos = RE_POS.search(p)
                pos = 'N'+mpos.group(1) if mpos else ''
                detailed.append({
                    'VIGA': t.get('viga','V_GERAL'),
                    'POS': pos,
                    'BIT': '',
                    'QTD': 1,
                    'COMP(m)': '',
                    'PESO(kg)': 0.0,
                    'POS_ORIGIN': 'embedded' if pos else '',
                    'BIT_ORIGIN': '',
                    'COMP_ORIGIN': '',
                    'TOKEN_TEXT': p,
                    'TOKEN_X': x if x is not None else '',
                    'TOKEN_Y': y if y is not None else '',
                    'ACTION': 'REVIEW'
                })
    # Pós-processamento simples: preenche REVIEWs com POS mas sem BIT/COMP usando ACCEPTs in same VIGA and similar Y
    idx_accept = defaultdict(list)
    for r in detailed:
        if r['ACTION'] == 'ACCEPT':
            key = (r['VIGA'], round(float(r['TOKEN_Y']) if r['TOKEN_Y']!='' else 0.0, 2))
            idx_accept[key].append(r)
    for r in detailed:
        if r['ACTION'] != 'REVIEW': continue
        if r['POS'] and (not r['BIT'] or not r['COMP(m)']):
            key = (r['VIGA'], round(float(r['TOKEN_Y']) if r['TOKEN_Y']!='' else 0.0, 2))
            cands = idx_accept.get(key, [])
            if not r['BIT']:
                for c in cands:
                    if c.get('BIT'):
                        r['BIT'] = c['BIT']; r['BIT_ORIGIN'] = 'neighbor_fill'; break
            if not r['COMP(m)']:
                for c in cands:
                    if c.get('COMP(m)'):
                        r['COMP(m)'] = c['COMP(m)']; r['COMP_ORIGIN'] = 'neighbor_fill'; break
            if r['BIT'] and r['COMP(m)']:
                try:
                    bitf = float(r['BIT']); compf = float(r['COMP(m)']); qtd = int(r.get('QTD',1))
                    peso_u = BITOS.get(bitf, 0.0)
                    r['PESO(kg)'] = round(peso_u * qtd * compf, 2)
                    r['ACTION'] = 'ACCEPT'
                except:
                    pass
    # write detailed CSV
    det_file = 'romaneio_detalhado_final.csv'
    with open(det_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['VIGA','POS','BIT(mm)','QTD','COMP(m)','PESO(kg)','POS_ORIGIN','BIT_ORIGIN','COMP_ORIGIN','TOKEN_TEXT','TOKEN_X','TOKEN_Y','ACTION'])
        for r in detailed:
            w.writerow([r['VIGA'], r['POS'], r['BIT'], r['QTD'], r['COMP(m)'], r['PESO(kg)'], r['POS_ORIGIN'], r['BIT_ORIGIN'], r['COMP_ORIGIN'], r['TOKEN_TEXT'], r['TOKEN_X'], r['TOKEN_Y'], r['ACTION']])
    # aggregate ACCEPT rows
    summary = defaultdict(lambda: {'q':0,'p':0.0})
    for r in detailed:
        if r['ACTION'] != 'ACCEPT': continue
        try:
            key = (r['VIGA'], r['POS'], float(r['BIT']), float(r['COMP(m)']))
            summary[key]['q'] += int(r['QTD']); summary[key]['p'] += float(r['PESO(kg)'])
        except:
            continue
    rom_file = 'romaneio_final.csv'
    with open(rom_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['VIGA','POS','BIT(mm)','QTD','COMP(m)','PESO(kg)'])
        for k,v in summary.items():
            viga,pos,bit,comp = k
            w.writerow([viga,pos,bit,v['q'],comp, round(v['p'],2)])
    # suspects
    sus_file = 'suspeitas_final.csv'
    with open(sus_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['VIGA','POS','BIT(mm)','QTD','COMP(m)','PESO(kg)','POS_ORIGIN','BIT_ORIGIN','COMP_ORIGIN','TOKEN_TEXT','TOKEN_X','TOKEN_Y','ACTION'])
        for r in detailed:
            if r['ACTION'] == 'REVIEW':
                w.writerow([r['VIGA'], r['POS'], r['BIT'], r['QTD'], r['COMP(m)'], r['PESO(kg)'], r['POS_ORIGIN'], r['BIT_ORIGIN'], r['COMP_ORIGIN'], r['TOKEN_TEXT'], r['TOKEN_X'], r['TOKEN_Y'], r['ACTION']])
    print("Pronto. Arquivos gerados:")
    print(" -", det_file)
    print(" -", rom_file)
    print(" -", sus_file)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        inp = sys.argv[1]
    else:
        inp = 'tokens_raw_final.csv'
    process_file(inp)
    