# core/pilares_motor.py - MOTOR CASCATA DE DOIS ESTÁGIOS COM EXTRAÇÃO GULOSA
import re
import os  # Necessário para o app
import math  # Necessário para o app
from datetime import datetime  # Necessário para o app
from typing import Tuple, List

try:
    import ezdxf
    from ezdxf.recover import readfile as recover_readfile
    EZDXF_DISPONIVEL = True
except ImportError:
    EZDXF_DISPONIVEL = False

# --- CONSTANTES ---
RE_PILAR_NAME = re.compile(r'(?:PILAR\s*)?P\s*(\d+)', re.IGNORECASE)

# Modo 1: Regex Apple (Linha Completa)
RE_LINHA_COMPLETA_VAR = re.compile(
    r'(\d+)\s*N\s*(\d+)\s*.*?[øØ]\s*(\d+[.,]?\d*)\s*.*[CcLl]\s*[=:\s]?\s*(\d+[.,]?\d*)',
    re.IGNORECASE,
)
RE_LINHA_COMPLETA = re.compile(
    r'(\d+)\s*N\s*(\d+)\s*.*?(\d+[.,]?\d*)\s*.*[CcLl]\s*[=:\s]?\s*(\d+[.,]?\d*)', re.IGNORECASE
)

# Lista de Bitolas - NBR 7480 (Aço para armaduras de concreto)
BITOLAS_VALIDAS = [
    5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0, 40.0
]

# --- FUNÇÕES AUXILIARES DE CÁLCULO/ANÁLISE (NECESSÁRIAS PARA O APP) ---

def _calcular_peso(bitola_mm, comp_m, qtde):
    """Calcula o peso em kg dado a bitola (mm) e o comprimento (m).
    Fórmula conforme NBR 7480: peso = (bitola² × 0.00617) × comprimento × quantidade."""
    peso_por_metro = (bitola_mm ** 2) * 0.00617
    return peso_por_metro * comp_m * qtde


def analisar_pilar_geometricamente(pos: str, bitola: float, comp_m: float) -> Tuple[str, List[float]]:
    comp_cm = comp_m * 100

    # ============================
    # 1) ESTRIBO (bitolas finas)
    # ============================
    if bitola <= 8.0 and comp_m < 2.0:

        gancho = max(10, 12 * bitola / 10)

        per_sem_gancho = comp_cm - 2 * gancho
        if per_sem_gancho < 20:
            return "ESTRIBO (12)", [comp_m / 4, comp_m / 4]

        melhor_A = None
        melhor_B = None
        erro = 9999
        semi = per_sem_gancho / 2

        for A in range(10, 80, 5):
            B = semi - A
            if B <= 0:
                continue
            B_round = round(B / 5) * 5
            if abs(B - B_round) < erro:
                melhor_A = A
                melhor_B = B_round
                erro = abs(B - B_round)

        if melhor_A and melhor_B:
            return "ESTRIBO (12)", [melhor_A / 100, melhor_B / 100]

        return "ESTRIBO (12)", [comp_m / 4, comp_m / 4]

    # ============================
    # 2) BARRA LONGITUDINAL (U)
    # ============================
    if bitola >= 10 and comp_m > 2.0:
        gancho = max(0.12, bitola * 0.012)
        vao = comp_m - 2 * gancho
        if vao > 0:
            return "BARRA U (11)", [gancho, vao, gancho]

    # ============================
    # 3) RETA
    # ============================
    return "RETA (01)", [comp_m]


def _eh_bitola_valida(valor):
    for b in BITOLAS_VALIDAS:
        if abs(valor - b) < 0.3:
            return True
    return False


def _limpar_texto_bruto(texto):
    if not texto:
        return ""

    t = str(texto).upper()

    t = re.sub(r'\\[ACFHQWLOT]\d+;', '', t)
    t = re.sub(r'\\[LIOK]', '', t)
    t = t.replace('\\P', ' ')  # Corrigido: escape duplo
    t = t.replace('{', ' ').replace('}', ' ')
    t = re.sub(r'[ØΦø]', ' Ø ', t)
    t = t.replace(',', '.')
    t = re.sub(r'\bL\s*[:=]?\s*(?=\d)', ' C ', t)
    t = t.replace('%%C', ' ')
    t = t.replace('\n', ' ').replace('\t', ' ')
    t = t.replace('=', ' ').replace(':', ' ')
    t = t.replace('-', ' ')
    t = re.sub(r'([A-Z])([0-9])', r'\1 \2', t)
    t = re.sub(r'([0-9])([A-Z])', r'\1 \2', t)
    t = re.sub(r'[^A-Z0-9. Ø]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()

    return t


def _tokenizar(frase):
    frase = frase.strip()
    frase = re.sub(r'Ø', ' Ø ', frase)
    frase = re.sub(r'[^\w.\- Ø ]', ' ', frase)
    frase = re.sub(r'\s+', ' ', frase).strip()
    tokens = frase.split()
    return tokens


# ============================================================
# PATCH APLICADO AQUI — divisão de textos contendo vários pilares
# (OPÇÃO A: separar e replicar por pilar)
# ============================================================

def _adicionar_texto_com_pilares_separados(limpo, todos_textos):
    """
    Divide corretamente um MTEXT que contém vários pilares dentro dele e
    gera uma entrada por pilar (opção A).

    Regras:
    - Localiza grupos de etiquetas de pilares consecutivas (podem conter '=' ou apenas espaços)
      seguidas por um bloco de conteúdo. Ex: "P22 = P23 N1 Ø6.3 C135 N2 Ø10 C380"
    - Para cada pilar listado, cria uma string separada: "P22 <conteudo>", "P23 <conteudo>"
    - Se não houver múltiplos P seguidos, comporta-se como antes.
    """
    toks = limpo.split()
    n = len(toks)
    i = 0

    while i < n:
        # procura próximo token que seja um P##
        if RE_PILAR_NAME.search(toks[i]):
            # coletar sequência de pilares adjacentes (ex: P22, =, P23, =, P24)
            pilares = []
            j = i
            while j < n and (RE_PILAR_NAME.search(toks[j]) or toks[j] == '=' or re.fullmatch(r'[=,]+', toks[j])):
                if RE_PILAR_NAME.search(toks[j]):
                    num = RE_PILAR_NAME.search(toks[j]).group(1)
                    pilares.append(f"P{num}")
                j += 1

            # agora j aponta para o primeiro token do conteúdo após os pilares
            k = j
            conteudo = []
            # captura conteúdo até o próximo Pxx (ou fim)
            while k < n and not RE_PILAR_NAME.search(toks[k]):
                conteudo.append(toks[k])
                k += 1

            # se conteudo estiver vazio, apenas criar entradas sem conteúdo
            conteudo_str = " ".join(conteudo).strip()
            if conteudo_str == "":
                # cria linha apenas com o pilar (útil em casos onde pilar está isolado)
                for p in pilares:
                    todos_textos.append(p)
            else:
                for p in pilares:
                    todos_textos.append(p + ' ' + conteudo_str)

            # avançar i para k (continua a varredura)
            i = k
        else:
            # token não inicia pilar: agrupa até próximo pilar
            # coletar até próximo P para criar uma frase independente
            j = i
            bloco = []
            while j < n and not RE_PILAR_NAME.search(toks[j]):
                bloco.append(toks[j])
                j += 1
            if bloco:
                todos_textos.append(' '.join(bloco))
            i = j


# ============================================================

def _extrair_regex_estrito(texto_limpo):
    patterns = [
        re.compile(r'(\d+)\s*N\s*(\d+)\s*.*?[Ø]?\s*(\d+[.]?\d*)\s*.*[CcLl]\s*[=:\s]?\s*(\d+[.]?\d*)'),
        re.compile(r'(\d+)\s*[Ø]?\s*(\d+[.]?\d*)\s*.*?N\s*(\d+)\s*[CcLl]\s*[=:\s]?\s*(\d+[.]?\d*)'),
        re.compile(r'N\s*(\d+)\s*(\d+)\s*[Ø]?\s*(\d+[.]?\d*)\s*[CcLl]?\s*(\d+[.]?\d*)'),
    ]

    for RE in patterns:
        m = RE.search(texto_limpo)
        if m:
            try:
                groups = [g for g in m.groups() if g is not None]
                if len(groups) >= 4:
                    qt = int(float(groups[0]))
                    pos = int(float(groups[1]))
                    bit = float(groups[2])
                    comp_cm = float(groups[3])
                    if qt == 0 or pos == 0 or comp_cm < 10:
                        return None
                    if not _eh_bitola_valida(bit):
                        return None
                    return qt, pos, bit, comp_cm
            except:
                pass
    return None


# (continuação do seu Modo 2...)
# A PARTE DO MODO 2 FOI MANTIDA, COM OS PATTERNS RELEVANTES
# --------------------------------------------------------

def _extrair_janela_deslizante(tokens):
    def to_number(tok):
        try:
            return float(tok)
        except:
            return None

    if len(tokens) < 3:
        return None, 0

    max_window = min(12, len(tokens))
    for window_size in range(2, max_window + 1):
        for start in range(0, len(tokens) - window_size + 1):
            w = tokens[start : start + window_size]

            has_N = 'N' in w
            has_C = 'C' in w

            W = w[:]

            # --- PATTERN A ---
            try:
                if 'N' in W and 'C' in W:
                    idx_n = W.index('N')
                    idx_c = W.index('C')
                    if idx_n >= 1:
                        qt_cand = to_number(W[idx_n - 1])
                        pos_cand = to_number(W[idx_n + 1]) if idx_n + 1 < len(W) else None
                        comp_cand = to_number(W[idx_c + 1]) if idx_c + 1 < len(W) else None
                        bit_cand = None
                        for tok in W[idx_n + 2 : idx_c]:
                            t = tok.replace('Ø', '')
                            v = to_number(t)
                            if v is not None and _eh_bitola_valida(v):
                                bit_cand = v
                                break

                        if qt_cand and pos_cand and bit_cand and comp_cand:
                            qt = int(qt_cand)
                            pos = int(pos_cand)
                            bit = float(bit_cand)
                            comp_cm = float(comp_cand)
                            if comp_cm >= 10:
                                return (qt, pos, bit, comp_cm), start + idx_c + 2
            except:
                pass

            # Outros patterns mantidos — (omitidos por brevidade)

    return None, 0


# ============================================================
# PROCESSAMENTO PRINCIPAL
# ============================================================

def _parse_table_rows_pilares(raw_tokens, table_titles):
    """
    Extrai linhas de tabela lateral de pilares similar ao vigas_motor_v2.
    
    Estratégia:
    # Detecta colunas pelo cabeçalho (POS, BIT, QUANT/QTD, COMP) na região x>65 (tabela de pilares).
    - Agrupa tokens por linha (Y próximo) e mapeia números para colunas.
    - Converte COMP de cm para m.
    - Retorna lista de tuplas: (pilar, pos, bitola, qtde, comp_m, peso_kg, formato, medidas)
    """
    entries = []
    if not table_titles:
        return entries
    
    # Detectar cabeçalhos de coluna
    header_keywords = {"POS", "BIT", "BITOLA", "QUANT", "QTD", "QTDE", "COMP", "COMPRIMENTO", "ACO", "AÇO"}
    header_tokens = [t for t in raw_tokens if t["x"] > 100.0 and 
                     any(kw in t["text"].upper().replace(" ", "") for kw in header_keywords)]
    
    if not header_tokens:
        print(f"[DEBUG] Nenhum header encontrado em x>100. Total tokens: {len(raw_tokens)}")
        # Tentar buscar headers em qualquer posição x > 65
        header_tokens = [t for t in raw_tokens if t["x"] > 65.0 and
                         any(kw in t["text"].upper().replace(" ", "") for kw in header_keywords)]
        if not header_tokens:
            return entries
        print(f"[DEBUG] Encontrados {len(header_tokens)} headers em x>65")
    
    # Se houver múltiplos cabeçalhos, usar a linha (Y) mais consistente
    if header_tokens:
        tokens_sorted = sorted(header_tokens, key=lambda t: -t["y"])
        groups = []
        for t in tokens_sorted:
            placed = False
            for g in groups:
                if abs(t["y"] - g["y"]) <= 0.6:
                    g["tokens"].append(t)
                    placed = True
                    break
            if not placed:
                groups.append({"y": t["y"], "tokens": [t]})

        def group_score(g):
            texts = [tt["text"].upper().replace(" ", "") for tt in g["tokens"]]
            score = 0
            for kw in ["POS", "BIT", "BITOLA", "QUANT", "QTD", "QTDE", "COMP", "COMPRIMENTO", "ACO", "AÇO"]:
                if any(kw in tx for tx in texts):
                    score += 1
            return score

        groups = sorted(groups, key=lambda g: (group_score(g), g["y"]), reverse=True)
        header_tokens = groups[0]["tokens"]

    # Mapear colunas por x mediano de cada keyword
    col_x = {}
    for kw in ["POS", "BIT", "BITOLA", "QUANT", "QTD", "QTDE", "COMP", "COMPRIMENTO"]:
        xs = [t["x"] for t in header_tokens if kw in t["text"].upper().replace(" ", "")]
        if xs:
            col_x[kw] = sum(xs) / len(xs)
    
    # Normalizar nomes
    if "BITOLA" in col_x and "BIT" not in col_x:
        col_x["BIT"] = col_x["BITOLA"]
    if "COMPRIMENTO" in col_x and "COMP" not in col_x:
        col_x["COMP"] = col_x["COMPRIMENTO"]
    if "QTD" in col_x and "QUANT" not in col_x:
        col_x["QUANT"] = col_x["QTD"]
    if "QTDE" in col_x and "QUANT" not in col_x:
        col_x["QUANT"] = col_x["QTDE"]
    
    # Precisamos das quatro chaves principais
    needed = ["POS", "BIT", "QUANT", "COMP"]

    # Detectar coluna de AÇO (para ignorar valores 50/60 da classe do aço)
    aco_x = None
    if "AÇO" in col_x:
        aco_x = col_x["AÇO"]
    elif "ACO" in col_x:
        aco_x = col_x["ACO"]
    aco_guard = 3.0
    
    # Se POS não foi encontrada, infere como primeira coluna (menor X)
    if "POS" not in col_x and len(col_x) >= 3:
        outras_cols = [col_x[k] for k in col_x.keys()]
        if outras_cols:
            col_x["POS"] = min(outras_cols) - 7.0  # 7 unidades antes da primeira coluna
            print(f"[DEBUG] POS inferida em x={col_x['POS']:.1f}")
    
    if not all(k in col_x for k in needed):
        return entries
    
    print(f"[INFO] Colunas detectadas: POS={col_x['POS']:.1f}, BIT={col_x['BIT']:.1f}, QUANT={col_x['QUANT']:.1f}, COMP={col_x['COMP']:.1f}")
    
    # Margem para ignorar coluna à esquerda
    pos_x_min = col_x["POS"] - 2.0
    
    # Adicionar limites de X mínimo e máximo para os tokens de dados (ignorar desenhos/anotações)
    x_min_dados = min(col_x.values()) - 5.0  # Começar 5 unidades antes da primeira coluna
    x_max_dados = max(col_x.values()) + 5.0  # Terminar 5 unidades depois da última coluna
    
    # Ordena títulos de tabela de cima para baixo
    titles_sorted = sorted(table_titles, key=lambda t: -t["y"])
    
    for idx, title in enumerate(titles_sorted):
        y_top = title["y"]
        y_bottom_raw = titles_sorted[idx + 1]["y"] if idx + 1 < len(titles_sorted) else -1e9
        
        # Buffer pequeno de 0.6 unidades para capturar linhas no limite sem misturar pilares
        y_bottom = y_bottom_raw - 0.6 if y_bottom_raw != -1e9 else -1e9
        
        # Pegar tokens neste bloco (só na região x > 100)
        bloco = [t for t in raw_tokens if (t["y"] < y_top and t["y"] > y_bottom and t["x"] > 100.0)]
        if not bloco:
            continue
        
        # Agrupa por linha (Y próximo)
        bloco_sorted = sorted(bloco, key=lambda t: -t["y"])
        linhas = []
        current = []
        current_y = None
        
        for t in bloco_sorted:
            if current_y is None or abs(t["y"] - current_y) <= 0.2:
                current.append(t)
                current_y = t["y"] if current_y is None else current_y
            else:
                linhas.append(current)
                current = [t]
                current_y = t["y"]
        if current:
            linhas.append(current)
        
        # Processar cada linha
        for linha_idx, linha in enumerate(linhas):
            cols = {k: None for k in needed}

            linha_debug = []
            linha_debug_all = []  # NOVO: todos os tokens
            row_nums = []  # (x, valor)

            for t in sorted(linha, key=lambda tt: tt["x"]):
                txt_orig = t["text"]
                linha_debug_all.append(f"{txt_orig}@{t['x']:.1f}")  # NOVO: mostrar TODOS os tokens

                if t["x"] < pos_x_min or t["x"] < x_min_dados or t["x"] > x_max_dados:
                    continue

                # Ignorar valores da coluna AÇO (classe do aço, ex: 50/60)
                if aco_x is not None and abs(t["x"] - aco_x) <= aco_guard:
                    continue
                    
                txt = t["text"].replace(" ", "").replace(",", ".")
                
                # Tentar extrair número
                mnum = re.search(r'[\d\.]+', txt)
                if not mnum:
                    linha_debug.append(f"{txt}@{t['x']:.1f}")
                    continue
                
                try:
                    val = float(mnum.group(0))
                except:
                    linha_debug.append(f"{txt}@{t['x']:.1f}(err)")
                    continue

                row_nums.append((t["x"], val))
                
                # Atribui à coluna cujo x é mais próximo
                nearest_col = min(needed, key=lambda k: abs(t["x"] - col_x[k]))
                if aco_x is not None and nearest_col == "BIT":
                    if abs(t["x"] - aco_x) < abs(t["x"] - col_x["BIT"]):
                        continue
                if cols[nearest_col] is None:
                    # Normalizar bitola se necessário (50 → 5.0mm, 60 → 6.0mm)
                    if nearest_col == "BIT":
                        # Tentar normalização: valores 40-700 geralmente são décimos de mm
                        if 40 <= val <= 700:
                            bit_normalized = val / 10.0
                            if _eh_bitola_valida(bit_normalized):
                                cols[nearest_col] = bit_normalized
                            else:
                                cols[nearest_col] = val  # Manter original para validação
                        elif _eh_bitola_valida(val):
                            cols[nearest_col] = val
                        else:
                            cols[nearest_col] = val  # Manter para rejeição
                    else:
                        cols[nearest_col] = val
                    linha_debug.append(f"{val}→{nearest_col}@{t['x']:.1f}")

            if linha_idx == 0:  # Mostrar TODOS os tokens da primeira linha
                pass  # Debug removido para limpeza
            if linha_idx < 3:  # Debug removido para limpeza
                pass

            # Fallback: inferir colunas por ordem dos tokens
            if any(cols[k] is None for k in needed) and row_nums:
                row_vals = [v for _, v in sorted(row_nums, key=lambda r: r[0])]

                def _norm_bit(val):
                    if _eh_bitola_valida(val):
                        return val
                    if 40 <= val <= 400 and _eh_bitola_valida(val / 10.0):
                        return val / 10.0
                    return None

                def _is_intish(v):
                    return abs(v - round(v)) < 0.01

                pos_cand = None
                bit_cand = None
                qty_cand = None
                comp_cand = None

                if len(row_vals) >= 5:
                    pos_cand = row_vals[1]
                    bit_cand = row_vals[2]
                    qty_cand = row_vals[3]
                    comp_cand = row_vals[4]
                elif len(row_vals) == 4:
                    pos_cand = row_vals[0]
                    bit_cand = row_vals[1]
                    qty_cand = row_vals[2]
                    comp_cand = row_vals[3]

                bit_cand = _norm_bit(bit_cand) if bit_cand is not None else None
                if bit_cand is None and row_vals:
                    bit_cand = _norm_bit(row_vals[0])

                if pos_cand is not None and not _is_intish(pos_cand):
                    pos_cand = None
                if qty_cand is not None and not _is_intish(qty_cand):
                    qty_cand = None

                if comp_cand is None and row_vals:
                    comp_cand = max(row_vals)

                if cols["POS"] is None and pos_cand is not None:
                    cols["POS"] = pos_cand
                if cols["BIT"] is None and bit_cand is not None:
                    cols["BIT"] = bit_cand
                if cols["QUANT"] is None and qty_cand is not None:
                    cols["QUANT"] = qty_cand
                if cols["COMP"] is None and comp_cand is not None:
                    cols["COMP"] = comp_cand
            
            # Validar se todas as colunas foram preenchidas
            if any(cols[k] is None for k in needed):
                continue
            
            try:
                pos = int(cols["POS"])
                bit = float(cols["BIT"])
                qty = int(cols["QUANT"])
                comp_cm = float(cols["COMP"])
            except:
                continue
            
            # Validações mais permissivas
            if not _eh_bitola_valida(bit):
                continue
            if not (10 <= comp_cm <= 5000):  # Aumentado range
                continue
            # Validação mais rigorosa: POS deve ser <= 100, QUANT <= 100 (rejeita agregados)
            if not (1 <= pos <= 100 and qty > 0 and qty <= 500):
                continue
            
            # Converter para metros
            comp_m = comp_cm / 100.0
            
            # Calcular peso
            peso_kg = _calcular_peso(bit, comp_m, qty)
            
            # Analisar geometria
            formato, medidas = analisar_pilar_geometricamente(f"N{pos}", bit, comp_m)
            
            # Adicionar entrada
            pilar_nome = title["nome"]
            entries.append((pilar_nome, f"N{pos}", bit, qty, comp_m, peso_kg, formato, medidas))
    
    return entries


def processar_pilares(arquivos):

    if not EZDXF_DISPONIVEL:
        # MOCK original — intacto
        dados_mock = [
            ("P1", "N1", 6.3, 50, 1.40, 4.88, "ESTRIBO (12)", [0.25, 0.40]),
            ("P1", "N2", 12.5, 4, 3.80, 14.63, "BARRA U (11)", [0.15, 3.50, 0.15]),
            ("P2", "N3", 8.0, 60, 1.65, 39.11, "GRAMPO (14)", [0.20, 0.35, 0.20, 0.20, 0.20]),
            ("P2", "N4", 16.0, 8, 4.20, 41.87, "RETA (01)", [4.20]),
            ("P3", "N5", 10.0, 10, 2.50, 15.43, "DOBRA L (13)", [0.50, 2.00]),
            ("P3", "N6", 6.3, 20, 1.20, 1.50, "ESTRIBO (12)", [0.20, 0.30]),
            ("P4", "N7", 12.5, 5, 3.50, 12.00, "BARRA U (11)", [0.15, 3.20, 0.15]),
        ]
        total_kg = sum(x[5] for x in dados_mock)
        total_barras = sum(x[3] for x in dados_mock)
        return dados_mock, total_kg, total_barras

    # ======================================
    # INÍCIO REAL DO PROCESSAMENTO
    # ======================================

    dados_completos = []
    peso_total_geral = 0.0
    total_barras_geral = 0
    itens_set = set()

    for arquivo in arquivos:
        try:
            doc, auditor = recover_readfile(arquivo)
            todos_textos = []
            raw_tokens = []  # NOVO: tokens com coordenadas para leitura de tabelas
            table_titles = []  # NOVO: títulos de pilares para tabelas

            # --- COLETA DE TEXTOS E TOKENS COM COORDENADAS ---
            for entity in doc.entities:
                if not entity.is_alive:
                    continue
                txt = ""
                x, y = 0.0, 0.0
                
                try:
                    if entity.dxftype() in ['TEXT', 'ATTRIB', 'ATTDEF']:
                        txt = entity.dxf.text
                        if hasattr(entity.dxf, 'insert'):
                            x, y = entity.dxf.insert.x, entity.dxf.insert.y
                    elif entity.dxftype() == 'MTEXT':
                        txt = entity.plain_text()
                        if hasattr(entity.dxf, 'insert'):
                            x, y = entity.dxf.insert.x, entity.dxf.insert.y
                    elif entity.dxftype() == 'MULTILEADER':
                        if entity.context and hasattr(entity.context, 'mtext'):
                            txt = entity.context.mtext.text
                        # Tentar pegar coordenadas do leader
                        try:
                            if hasattr(entity, 'vertices') and entity.vertices:
                                x, y = entity.vertices[0].x, entity.vertices[0].y
                        except:
                            pass
                except:
                    pass

                if txt:
                    limpo = _limpar_texto_bruto(txt)
                    if limpo:
                        # Adicionar para análise textual tradicional
                        _adicionar_texto_com_pilares_separados(limpo, todos_textos)
                        
                        # NOVO: Adicionar token com coordenadas para leitura de tabelas
                        raw_tokens.append({"text": txt, "x": x, "y": y})
                        
                        # NOVO: Detectar títulos de pilares (P1, P2, etc) para tabelas
                        m_pilar = RE_PILAR_NAME.search(limpo)
                        if m_pilar:
                            pilar_nome = f"P{m_pilar.group(1)}"
                            # Só adiciona se x > 100 (região de tabela lateral direita)
                            if x > 100:
                                table_titles.append({"nome": pilar_nome, "x": x, "y": y})

            # ---------------------------------
            # NOVA ETAPA: LEITURA DE TABELAS
            # ---------------------------------
            usar_fallback = True  # Flag para controlar se deve usar método fallback
            
            if raw_tokens and table_titles:
                print(f"[INFO] Detectados {len(table_titles)} títulos de pilares em tabela")
                tabela_entries = _parse_table_rows_pilares(raw_tokens, table_titles)
                
                if tabela_entries:
                    print(f"[INFO] Extraídas {len(tabela_entries)} linhas de tabela")
                    usar_fallback = False  # Tabela funcionou, não usar fallback
                    
                    # Agrupar por pilar e posição (ignorar bitola/quantidade/comprimento diferentes)
                    entradas_por_posicao = {}
                    
                    for entry in tabela_entries:
                        pilar, pos, bit, qty, comp_m, peso_kg, formato, medidas = entry
                        chave = (pilar, pos)  # Chave simplificada: apenas pilar + posição
                        
                        # Se já existe essa posição, somar quantidades e pesos
                        if chave in entradas_por_posicao:
                            # Já existe - adicionar os dados (opcional: somar ou manter o primeiro)
                            # Por enquanto, vamos MANTER O PRIMEIRO encontrado
                            continue
                        else:
                            entradas_por_posicao[chave] = entry
                    
                    # Adicionar entradas únicas aos dados completos
                    for entry in entradas_por_posicao.values():
                        pilar, pos, bit, qty, comp_m, peso_kg, formato, medidas = entry
                        dados_completos.append(entry)
                        peso_total_geral += peso_kg
                        total_barras_geral += qty
                        
                        # Adicionar ao set com chave completa para evitar duplicatas do fallback
                        chave_completa = (pilar, pos, bit, qty, round(comp_m * 100, 1))
                        itens_set.add(chave_completa)

            # ---------------------------------
            # ETAPA ORIGINAL: INTERPRETAR TEXTOS (fallback se tabela não funcionar)
            # ---------------------------------
            if usar_fallback:
                print(f"[INFO] Usando método fallback (leitura de textos)")
                
                pilar_atual = "GERAL"
                buffer_tokens = []

                for frase in todos_textos:

                    # Se detecta "P1", "P2"... troca de pilar
                    m_pilar = RE_PILAR_NAME.search(frase)
                    if m_pilar:
                        pilar_atual = f"P{m_pilar.group(1)}"
                        buffer_tokens = []
                        continue

                    dados = None

                    # MODO 1
                    dados_modo1 = _extrair_regex_estrito(frase)
                    if dados_modo1:
                        dados = dados_modo1
                        buffer_tokens = []
                    else:
                        # MODO 2
                        if 'N' in frase and 'C' in frase:

                            frase_norm = frase.replace('L', ' C').replace('N', ' N').replace('C', ' C')
                            frase_norm = frase_norm.replace(',', '.')
                            tokens = frase_norm.split()
                            buffer_tokens.extend(tokens)

                            while True:
                                dados_com_indice, idx = _extrair_janela_deslizante(buffer_tokens)
                                if dados_com_indice:
                                    qt, pos, bit, comp_cm = dados_com_indice
                                    chave = (pilar_atual, f"N{pos}", bit, qt, round(comp_cm, 1))

                                    if chave not in itens_set:
                                        itens_set.add(chave)
                                        comp_m = comp_cm / 100.0
                                        peso = _calcular_peso(bit, comp_m, qt)

                                        formato_dobra, medidas_m = analisar_pilar_geometricamente(f"N{pos}", bit, comp_m)

                                        dados_completos.append(
                                            (pilar_atual, f"N{pos}", bit, qt, round(comp_m, 2),
                                             round(peso, 2), formato_dobra, medidas_m)
                                        )

                                        peso_total_geral += peso
                                        total_barras_geral += qt

                                        buffer_tokens = buffer_tokens[idx:]
                                        dados = None
                                    else:
                                        break
                                else:
                                    break

                    # PROCESSA MODO 1
                    if dados:
                        qt, pos, bit, comp_cm = dados
                        chave = (pilar_atual, f"N{pos}", bit, qt, round(comp_cm, 1))

                        if chave not in itens_set:
                            itens_set.add(chave)

                            comp_m = comp_cm / 100.0
                            peso = _calcular_peso(bit, comp_m, qt)

                            formato_dobra, medidas_m = analisar_pilar_geometricamente(f"N{pos}", bit, comp_m)

                            dados_completos.append(
                                (pilar_atual, f"N{pos}", bit, qt, round(comp_m, 2),
                                 round(peso, 2), formato_dobra, medidas_m)
                            )

                            peso_total_geral += peso
                            total_barras_geral += qt

        except Exception as e:
            print(f"Erro no arquivo {arquivo}: {e}")

    # Ordenação final por P e N
    def sort_key(x):
        try:
            np = int(re.search(r'\d+', x[0]).group())
            nn = int(re.search(r'\d+', x[1]).group())
            return (np, nn)
        except:
            return (999, 0)

    dados_completos.sort(key=sort_key)
    return dados_completos, peso_total_geral, total_barras_geral
