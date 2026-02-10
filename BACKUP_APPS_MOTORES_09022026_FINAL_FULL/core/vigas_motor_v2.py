import os, re
from typing import List, Tuple

DX_WINDOW = 15.0
DY_WINDOW = 8.0
MAX_DX = 2.0
MAX_DY = 1.5
MAX_QTY = 30
MAX_POS_NUM = 50

PESOS_NOMINAIS = {
    4.2: 0.109, 5.0: 0.154, 6.0: 0.222, 6.3: 0.245, 8.0: 0.395,
    8.3: 0.425, 10.0: 0.617, 12.5: 0.963, 16.0: 1.578, 20.0: 2.466,
    25.0: 3.853, 32.0: 6.313,
}
BITOLAS_VALIDAS = set(PESOS_NOMINAIS.keys())

RE_VIGA_STRICT = re.compile(r'^(V[NTPB]?\d[\w\-]*)$', re.IGNORECASE)
RE_VIGA_LOOSE = re.compile(r'\bV[A-Z]?\d[\w\-]*\b', re.IGNORECASE)
RE_VIGA_FALLBACK = re.compile(r'(?:^|\s)(VIGA|V|VM|VC|VB|VP|VT)\s*-?\s*([A-Z]?\d[\w\-]*)', re.IGNORECASE)

REGEX_BARRA_FULL = re.compile(
    r"""(?:(\d+)x)?      # mult opcional
        (\d+)            # qty
        \s*N(\d+)        # posição
        \s*[Øø∅]?\s*
        (\d+(?:[.,][\d]+)?) # bitola
        \s*C\s*=?\s*
        (\d+(?:[.,][\d]+)?) # comp
    """, re.IGNORECASE | re.VERBOSE
)

def _clean_letters(txt: str, allowed: str) -> bool:
    return re.fullmatch(rf"[{allowed}0-9\s\.,=]+", txt.upper()) is not None

def _parse_qty(txt: str):
    """Parse quantidade: '18', '2x13', '10X2', etc."""
    t = txt.upper().strip()
    if len(t) > 10:
        return None
    # Formato: '2x13' ou '10X2'
    m = re.fullmatch(r"(\d+)\s*[xX]\s*(\d+)", t)
    if m:
        return int(m.group(1)) * int(m.group(2))
    # Formato simples: '18'
    m = re.fullmatch(r"(\d+)", t)
    if m:
        q = int(m.group(1))
        if 1 <= q <= MAX_QTY * 5:  # Permitir até 150 para qty
            return q
    return None

def _parse_pos(txt: str):
    t = txt.upper().strip()
    if len(t) > 4:
        return None
    m = re.fullmatch(r"N\s*(\d{1,3})", t)
    if m:
        num = int(m.group(1))
        if 1 <= num <= MAX_POS_NUM:
            return f"N{num}"
    return None

def _parse_bitola(txt: str):
    t = txt.upper().replace("%%C", "Ø").replace("Φ", "O").strip()
    if ("Ø" not in t) and ("O" not in t) and ("MM" not in t):
        return None
    if "C=" in t:
        return None
    if len(t) > 11:
        return None
    if not _clean_letters(t, allowed="ØOMX"):
        return None
    m = (re.search(r"Ø\s*([0-9]+(?:[.,][0-9]+)?)", t)
         or re.search(r"O\s*([0-9]+(?:[.,][0-9]+)?)", t)
         or re.search(r"([0-9]+(?:[.,][0-9]+)?)\s*MM", t))
    if m:
        try:
            b = float(m.group(1).replace(",", "."))
            return b if b in BITOLAS_VALIDAS else None
        except:
            return None
    return None

def _norm_comp(val: float):
    if val is None:
        return None
    if val > 20:
        val = val / 100.0
    return val if 0.6 <= val <= 12.0 else None

def _parse_comp(txt: str):
    t = txt.upper().strip()
    if not _clean_letters(t, allowed="CMOX"):
        return None
    val = None
    if "C=" in t:
        m = re.search(r"C\s*=\s*([\d\.,]+)", t)
        if m:
            try: val = float(m.group(1).replace(",", "."))
            except: val = None
    if val is None:
        m3 = re.search(r"C\s*([\d\.,]+)", t)
        if m3:
            try: val = float(m3.group(1).replace(",", "."))
            except: val = None
    if val is None:
        m2 = re.search(r"([\d\.,]+)\s*M\b", t)
        if m2:
            try: val = float(m2.group(1).replace(",", "."))
            except: val = None
    return _norm_comp(val)

def _parse_full_token(txt: str):
    m = REGEX_BARRA_FULL.search(txt)
    if not m:
        return None
    mult = m.group(1)
    qty = int(m.group(2))
    pos = f"N{m.group(3)}"
    try:
        bit = float(m.group(4).replace(",", "."))
        comp_raw = float(m.group(5).replace(",", "."))
    except:
        return None
    if bit not in BITOLAS_VALIDAS:
        return None
    if mult:
        qty *= int(mult)
    comp = _norm_comp(comp_raw)
    if not comp:
        return None
    qty = min(qty, MAX_QTY)
    peso = PESOS_NOMINAIS.get(bit, 0.0) * comp * qty
    return pos, bit, qty, comp, peso

def calcula_peso(bitola: float, comp_m: float, qty: int) -> float:
    return PESOS_NOMINAIS.get(bitola, 0.0) * comp_m * qty

def _nearest_xy(target, candidates):
    best, best_d = None, None
    for c in candidates:
        dx = abs(target["x"] - c["x"])
        dy = abs(target["y"] - c["y"])
        if dx <= MAX_DX and dy <= MAX_DY:
            d = dx + dy
            if best is None or d < best_d:
                best, best_d = c, d
    return best


def _parse_table_rows(raw, table_titles):
    """Extrai linhas da tabela lateral utilizando cabeçalho POS/BIT/QUANT/COMP.

    Estratégia:
    - Detecta colunas pelo cabeçalho (POS, BIT, QUANT, COMP) na região x>65.
    - Agrupa tokens por linha (Y próximo) e mapeia cada número para a coluna mais próxima.
    - Exige todas as 4 colunas numéricas presentes; converte COMP de cm para m.
    """
    entries = []
    if not table_titles:
        return entries

    # Detectar cabeçalhos de coluna
    header_keywords = {"POS", "BIT", "QUANT", "COMP", "COMPRIMENTO"}
    header_tokens = [t for t in raw if t["x"] > 65.0 and t["text"].upper().replace(" ", "") in header_keywords]
    if not header_tokens:
        return entries

    # Mapear colunas por x mediano de cada keyword
    col_x = {}
    for kw in header_keywords:
        xs = [t["x"] for t in header_tokens if t["text"].upper().replace(" ", "") == kw]
        if xs:
            col_x[kw] = sum(xs) / len(xs)
    # Permite COMPRIMENTO substituir COMP
    if "COMP" not in col_x and "COMPRIMENTO" in col_x:
        col_x["COMP"] = col_x["COMPRIMENTO"]
    # Precisamos das quatro chaves principais
    needed = ["POS", "BIT", "QUANT", "COMP"]
    if not all(k in col_x for k in needed):
        return entries

    # Margem para ignorar coluna de aço (AÇO) à esquerda
    pos_x_min = col_x["POS"] - 2.0

    # Ordena títulos de tabela de cima para baixo
    titles_sorted = sorted(table_titles, key=lambda t: -t["y"])
    for idx, title in enumerate(titles_sorted):
        y_top = title["y"]
        y_bottom = titles_sorted[idx + 1]["y"] if idx + 1 < len(titles_sorted) else -1e9

        bloco = [t for t in raw if (t["y"] < y_top and t["y"] > y_bottom and t["x"] > 65.0)]
        if not bloco:
            continue

        # Agrupa por linha (Y próximo)
        bloco_sorted = sorted(bloco, key=lambda t: -t["y"])
        linhas = []
        current = []
        current_y = None
        for t in bloco_sorted:
            if current_y is None or abs(t["y"] - current_y) <= 0.2:
                current.append(t); current_y = t["y"] if current_y is None else current_y
            else:
                linhas.append(current); current = [t]; current_y = t["y"]
        if current:
            linhas.append(current)

        for linha in linhas:
            cols = {k: None for k in needed}
            for t in sorted(linha, key=lambda tt: tt["x"]):
                if t["x"] < pos_x_min:
                    continue
                txt = t["text"].replace(" ", "")
                mnum = re.fullmatch(r"[\d\.,]+", txt)
                if not mnum:
                    continue
                try:
                    val = float(mnum.group(0).replace(",", "."))
                except:
                    continue
                # Atribui à coluna cujo x é mais próximo
                nearest_col = min(needed, key=lambda k: abs(t["x"] - col_x[k]))
                cols[nearest_col] = val if cols[nearest_col] is None else cols[nearest_col]
            if any(cols[k] is None for k in needed):
                continue

            try:
                pos = int(cols["POS"])
                bit = float(cols["BIT"])
                qty = int(cols["QUANT"])
                comp_cm = float(cols["COMP"])
            except:
                continue

            if bit not in BITOLAS_VALIDAS:
                continue
            if not (50 <= comp_cm <= 2000):
                continue
            comp_m = _norm_comp(comp_cm)
            if comp_m is None:
                continue
            if not (1 <= pos < MAX_POS_NUM and qty > 0 and qty <= MAX_QTY * 5):
                continue

            peso = calcula_peso(bit, comp_m, qty)
            entries.append((title["nome"], f"N{pos}", bit, qty, comp_m, peso))

    return entries

def processar_vigas(arquivos: List[str]) -> Tuple[List[Tuple], float, int]:
    try:
        import ezdxf
    except ImportError as e:
        print(f"[ERRO] ezdxf não encontrado: {e}")
        return [], 0.0, 0

    dados = []
    for arq in arquivos:
        if not os.path.exists(arq):
            print(f"[ERRO] Arquivo não existe: {arq}")
            continue
        try:
            doc = ezdxf.readfile(arq)
            msp = doc.modelspace()
        except Exception as e:
            print(f"[ERRO] Falha lendo {arq}: {e}")
            continue

        raw = []
        for e in msp.query("TEXT MTEXT ATTRIB"):
            try:
                txt = e.dxf.text if e.dxftype() == 'TEXT' else e.plain_text()
            except Exception:
                txt = getattr(e, "text", "")
            if not txt:
                continue
            x, y = float(e.dxf.insert[0]), float(e.dxf.insert[1])
            raw.append({"text": txt.strip(), "x": x, "y": y})

        if not raw:
            continue

        # Detecta títulos em todos os textos
        titles_dict = {}
        for t in raw:
            txt = t["text"]
            t_nospace = txt.replace(" ", "")
            nome = None
            if RE_VIGA_STRICT.match(t_nospace):
                nome = t_nospace.upper()
            else:
                m = RE_VIGA_FALLBACK.search(txt) or RE_VIGA_LOOSE.search(txt)
                if m:
                    nome = m.group(0) if len(m.groups()) == 0 else f"{m.group(1)}{m.group(2)}"
                    nome = nome.replace("VIGA", "V").replace("-", "").upper()
            if nome:
                # Mantém apenas o título com menor X (mais à esquerda) para cada nome único
                if nome not in titles_dict or t["x"] < titles_dict[nome]["x"]:
                    titles_dict[nome] = {"nome": nome, "x": t["x"], "y": t["y"]}
        titles = list(titles_dict.values())

        # Títulos que aparecem na tabela (lado direito) para leitura de linhas
        table_titles = []
        table_title_counts = {}
        viga_equivalencias = {}  # Mapeamento: viga -> viga_principal (primeira do grupo)
        viga_multiplicidade = {}  # Multiplicidade da anotação (X4) para cada viga principal
        vigas_processadas_equiv = set()  # Para evitar processar a mesma equivalência multiplas vezes
        
        # PASSO 1: Detectar equivalências e multiplicidades
        for t in raw:
            txt = t["text"]
            # Checar se há padrão V###=V###...
            # Ignorar rodapés/anotações (Y < 30) e linhas com "/" que são resumos
            if "=" in txt and ("V" in txt.upper()) and t["y"] > 30.0 and "/" not in txt and t["x"] > 65.0:
                # Extrair multiplicidade (X4), (4X), etc - deve estar em parênteses ou ter X adjacente
                import re as re_module
                mult_match = re_module.search(r'\(\s*[xX]?\s*(\d+)\s*[xX]?\s*\)|[xX]\s*(\d+)|(\d+)\s*[xX]', txt)
                if mult_match:
                    # Pegar o primeiro grupo não-nulo
                    multiplicidade = int(mult_match.group(1) or mult_match.group(2) or mult_match.group(3))
                else:
                    multiplicidade = 1
                
                # Extrair todas as vigas V### da string
                viga_pattern = re_module.compile(r'V\s*(\d{3})', re_module.IGNORECASE)
                matches = viga_pattern.findall(txt.upper())
                vigas_equivalentes = [f"V{m}" for m in matches]
                
                # Criar mapeamento: todas as vigas equivalem à primeira
                if len(vigas_equivalentes) > 1:
                    viga_principal = vigas_equivalentes[0]
                    grupo_key = tuple(sorted(vigas_equivalentes))
                    
                    # Só processar se ainda não processamos este grupo
                    if grupo_key not in vigas_processadas_equiv:
                        vigas_processadas_equiv.add(grupo_key)
                        
                        for viga in vigas_equivalentes[1:]:
                            viga_equivalencias[viga] = viga_principal
                        
                        # Guardar multiplicidade da anotação
                        viga_multiplicidade[viga_principal] = multiplicidade
                        
                        # Adicionar a viga principal como título de tabela
                        table_titles.append({"nome": viga_principal, "x": t["x"], "y": t["y"]})
        
        # PASSO 2: Detectar títulos normalmente
        for t in raw:
            txt = t["text"]
            t_nospace = txt.replace(" ", "")
            nome = None
            
            # Só processar se está na região da tabela e Y > 30 (evitar rodapé)
            if t["x"] > 65.0 and t["y"] > 30.0:
                if RE_VIGA_STRICT.match(t_nospace):
                    nome = t_nospace.upper()
                else:
                    # Evitar linhas com "=" (já foram processadas) ou "/" (resumos)
                    if "=" not in txt and "/" not in txt:
                        m = RE_VIGA_FALLBACK.search(txt) or RE_VIGA_LOOSE.search(txt)
                        if m:
                            nome = m.group(0) if len(m.groups()) == 0 else f"{m.group(1)}{m.group(2)}"
                            nome = nome.replace("VIGA", "V").replace("-", "").upper()
                
                if nome:
                    # Se é viga principal de grupo, adicionar apenas ela (evita duplicações)
                    # Se é viga equivalente, mapear para principal
                    if nome in viga_equivalencias:
                        continue  # Pular vigas equivalentes, usaremos apenas a principal
                    
                    # Se já foi adicionada no passo 1 (equivalência), não duplicar
                    if nome in viga_multiplicidade:
                        continue
                    
                    table_titles.append({"nome": nome, "x": t["x"], "y": t["y"]})
                    table_title_counts[nome] = table_title_counts.get(nome, 0) + 1

        # Debug: títulos detectados na tabela
        if table_titles:
            nomes_table = {}
            for tt in table_titles:
                nomes_table.setdefault(tt["nome"], 0)
                nomes_table[tt["nome"]] += 1
            print(f"[TABLE TITLES] {os.path.basename(arq)} -> {nomes_table}")

        viga_atual = None
        full_hits = []
        leftovers = []

        # viga_atual + regex completa
        for t in raw:
            txt = t["text"]
            t_nospace = txt.replace(" ", "")
            if RE_VIGA_STRICT.match(t_nospace):
                viga_atual = t_nospace.upper()
                continue
            full = _parse_full_token(txt)
            if full:
                pos, bit, qty, comp, peso = full
                alvo = viga_atual or None
                full_hits.append((alvo, pos, bit, qty, comp, peso, t["x"], t["y"]))
            else:
                leftovers.append({"text": txt, "x": t["x"], "y": t["y"], "viga": viga_atual})

        if not titles:
            if viga_atual:
                titles.append({"nome": viga_atual, "x": 0.0, "y": 1e9})
            else:
                titles.append({"nome": "V_GERAL", "x": 0.0, "y": 1e9})

        bruto = []
        # full_hits -> título mais próximo (dx+|dy|)
        for v_guess, pos, bit, qty, comp, peso, x, y in full_hits:
            alvo = v_guess
            if alvo is None and titles:
                best, best_d = None, None
                for tt in titles:
                    dx = abs(tt["x"] - x)
                    dy = abs(tt["y"] - y)
                    d = dx + dy
                    if best is None or d < best_d:
                        best, best_d = tt, d
                alvo = best["nome"] if best else "V_GERAL"
            bruto.append((alvo or "V_GERAL", pos, bit, qty, comp, peso))

        # Fallback com alinhamento rígido - detectar qty+pos+bit+comp
        for title in titles:
            janela = [
                t for t in leftovers
                if abs(t["y"] - title["y"]) <= DY_WINDOW
                and abs(t["x"] - title["x"]) <= DX_WINDOW
            ]

            if not janela:
                continue

            qty_tokens, pos_tokens, bit_tokens, comp_tokens = [], [], [], []
            for t in janela:
                q = _parse_qty(t["text"])
                # Não detectar pos em textos com Ø ou C=
                if any(ch in t["text"].upper() for ch in ("Ø", "%%C", "C=")):
                    p = None
                else:
                    p = _parse_pos(t["text"])
                b = _parse_bitola(t["text"])
                c = _parse_comp(t["text"])
                
                if q is not None: tt = dict(t); tt["qty"] = q; qty_tokens.append(tt)
                if p: tt = dict(t); tt["pos"] = p; pos_tokens.append(tt)
                if b is not None: tt = dict(t); tt["bit"] = b; bit_tokens.append(tt)
                if c is not None: tt = dict(t); tt["comp"] = c; comp_tokens.append(tt)

            for p in pos_tokens:
                b = _nearest_xy(p, bit_tokens)
                c = _nearest_xy(p, comp_tokens)
                if b and c:
                    if (abs(p["y"] - b["y"]) <= MAX_DY and
                        abs(p["y"] - c["y"]) <= MAX_DY and
                        abs(b["y"] - c["y"]) <= MAX_DY and
                        abs(p["x"] - b["x"]) <= MAX_DX and
                        abs(p["x"] - c["x"]) <= MAX_DX and
                        abs(b["x"] - c["x"]) <= MAX_DX):
                        # Buscar qty próxima à esquerda da posição
                        q_cand = [qt for qt in qty_tokens if abs(qt["y"] - p["y"]) <= MAX_DY]
                        if q_cand:
                            # Escolher qty mais próxima à esquerda (menor X)
                            q_cand.sort(key=lambda qt: (abs(qt["y"] - p["y"]), abs(qt["x"] - p["x"])))
                            q = min(q_cand[0]["qty"], MAX_QTY)
                        else:
                            q = 1
                        peso = calcula_peso(b["bit"], c["comp"], q)
                        bruto.append((title["nome"], p["pos"], b["bit"], q, c["comp"], peso))

        # Linhas da tabela lateral (captura POS/BIT/QTY/COMP cm)
        table_entries = _parse_table_rows(raw, table_titles)
        if table_entries:
            # Em vez de duplicar dados, vamos adicionar os nomes equivalentes ao título
            # Ex: V307 vira "V307=V311=V333=V336"
            viga_grupos = {}  # viga_principal -> [lista de todas as vigas do grupo]
            for viga_eq, viga_principal in viga_equivalencias.items():
                if viga_principal not in viga_grupos:
                    viga_grupos[viga_principal] = [viga_principal]
                viga_grupos[viga_principal].append(viga_eq)
            
            # Renomear vigas principais para incluir equivalentes
            entries_renomeadas = []
            for (v, p, b, q, c, peso) in table_entries:
                # Se esta viga tem equivalentes, mostrar todas
                if v in viga_grupos:
                    grupo_nomes = "=".join(sorted(viga_grupos[v]))
                    # Usar multiplicidade da anotação (X4), não do count de table_title_counts
                    multiplicidade = viga_multiplicidade.get(v, 1)
                    if multiplicidade > 1:
                        v_final = f"{grupo_nomes} (x{multiplicidade})"
                    else:
                        v_final = grupo_nomes
                elif table_title_counts.get(v, 1) > 1:
                    v_final = f"{v}(x{table_title_counts[v]})"
                else:
                    v_final = v
                
                entries_renomeadas.append((v_final, p, b, q, c, peso))
            
            # Quando há tabela, descarta TODO o desenho (evita pegar referências)
            bruto = entries_renomeadas

        # Dedup agressivo por (viga, pos, bit): escolhe comp mais frequente (ou menor) e soma qty
        dedup = {}
        for viga, pos, bit, qty, comp, peso in bruto:
            key = (viga, pos, bit)
            if key not in dedup:
                dedup[key] = {"comp_counts": {}, "qty": 0}
            comp_r = round(comp, 2)
            dedup[key]["comp_counts"][comp_r] = dedup[key]["comp_counts"].get(comp_r, 0) + qty
            dedup[key]["qty"] = min(dedup[key]["qty"] + qty, MAX_QTY * 5)

        for (viga, pos, bit), info in dedup.items():
            # escolhe comp mais frequente; se empate, menor comp
            comp_freq = sorted(info["comp_counts"].items(), key=lambda x: (-x[1], x[0]))
            comp = comp_freq[0][0]
            qty = info["qty"]
            peso = calcula_peso(bit, comp, qty)
            dados.append((viga, pos, bit, qty, round(comp, 2), round(peso, 3)))

    total_kg = round(sum(d[5] for d in dados), 2)
    total_barras = sum(d[3] for d in dados)

    def extrair_ordem_viga(nome_viga: str):
        nome_upper = nome_viga.upper()
        if nome_upper.startswith('VN'):
            tipo, resto = 1, nome_upper[2:]
        elif nome_upper.startswith('VT'):
            tipo, resto = 2, nome_upper[2:]
        elif nome_upper.startswith('VP'):
            tipo, resto = 3, nome_upper[2:]
        elif nome_upper.startswith('VB'):
            tipo, resto = 4, nome_upper[2:]
        elif nome_upper.startswith('V'):
            tipo, resto = 0, nome_upper[1:]
        else:
            tipo, resto = 99, nome_upper
        m = re.match(r'(\d+)', resto)
        if m:
            n1 = int(m.group(1)); sufixo = resto[len(m.group(1)):]
        else:
            n1, sufixo = 9999, resto
        n2, letra = 9999, ''
        if '-' in sufixo:
            partes = sufixo.split('-', 1)
            m2 = re.match(r'(\d+)([A-Z]*)', partes[1])
            if m2:
                n2 = int(m2.group(1)); letra = m2.group(2)
        return (tipo, n1, n2, letra)

    def ordem_final(item):
        viga, pos, bit, qty, comp, peso = item
        v_ord = extrair_ordem_viga(viga)
        try:
            pos_num = int(pos[1:])
        except:
            pos_num = 9999
        # Inclui nome da viga na chave para evitar intercalar vigas com mesmo "tipo"
        return (v_ord, viga, pos_num, bit, comp)

    dados.sort(key=ordem_final)
    return dados, total_kg, total_barras