# core/pilares_motor_dual.py - MOTOR DUAL: Rápido (desenhos) + Completo (tabelas)
import re
import os
from datetime import datetime
from typing import Tuple, List

try:
    import ezdxf
    from ezdxf.recover import readfile as recover_readfile
    EZDXF_DISPONIVEL = True
except ImportError:
    EZDXF_DISPONIVEL = False

# --- CONSTANTES ---
RE_PILAR_NAME = re.compile(r'(?:PILAR\s*)?P\s*(\d+)', re.IGNORECASE)
# Captura a nomenclatura completa (P14, P14-P32, P14=P32(X2), P14/P32, etc)
RE_PILAR_FULL = re.compile(
    r'(?:PILAR\s*)?'  # Opcional: palavra "PILAR"
    r'(P\d+(?:[\s]*[-=/][\s]*P?\d+(?:\s*\(\s*X\s*\d+\s*\))?)*'  # Expansões
    r'(?:\s*\(\s*X\s*\d+\s*\))?)',
    re.IGNORECASE
)
BITOLAS_VALIDAS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0, 40.0]

# --- FUNÇÕES AUXILIARES ---
def _calcular_peso(bitola_mm, comp_m, qtde):
    """Calcula peso em kg: (bitola² × 0.00617) × comprimento × quantidade"""
    peso_por_metro = (bitola_mm ** 2) * 0.00617
    return peso_por_metro * comp_m * qtde

def _limpar_texto_bruto(texto):
    """Limpa formatação do DXF"""
    if not texto:
        return ""
    t = str(texto).upper()
    t = re.sub(r'\\[ACFHQWLOT]\d+;', '', t)
    t = re.sub(r'\\[LIOK]', '', t)
    t = t.replace('\\P', ' ')
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

def _limpar_texto_titulo(texto):
    """Limpa texto de título preservando operadores de expansão (=, -, /, ;, X)."""
    if not texto:
        return ""
    t = str(texto).upper()
    t = re.sub(r'\\[ACFHQWLOT]\d+;', '', t)
    t = re.sub(r'\\[LIOK]', '', t)
    t = t.replace('\\P', ' ')
    t = t.replace('{', ' ').replace('}', ' ')
    t = t.replace('%%C', ' ')
    t = t.replace('\n', ' ').replace('\t', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def analisar_pilar_geometricamente(pos: str, bitola: float, comp_m: float) -> Tuple[str, List[float]]:
    """Analisa geometria da barra"""
    comp_cm = comp_m * 100
    
    if bitola <= 8.0 and comp_m < 2.0:
        gancho = max(10, 12 * bitola / 10)
        per_sem_gancho = comp_cm - 2 * gancho
        if per_sem_gancho < 20:
            return "ESTRIBO (12)", [comp_m / 4, comp_m / 4]
        return "ESTRIBO (12)", [comp_m / 4, comp_m / 4]
    
    if bitola >= 10 and comp_m > 2.0:
        gancho = max(0.12, bitola * 0.012)
        vao = comp_m - 2 * gancho
        if vao > 0:
            return "BARRA U (11)", [gancho, vao, gancho]
    
    return "RETA (01)", [comp_m]

def _eh_bitola_valida(valor):
    """Valida bitola"""
    for b in BITOLAS_VALIDAS:
        if abs(valor - b) < 0.3:
            return True
    return False

# ============================================================
# MOTOR RÁPIDO - Para desenhos (x < 100)
# ============================================================
def _processar_textos_fragmentados(textos_com_posicao):
    """
    Processa arquivos com textos fragmentados (cada campo separado)
    Agrupa textos pela posição Y e detecta colunas por X
    """
    dados = []
    pilar_atual = None
    
    # Agrupar textos por linha (Y)
    linhas = {}
    for texto, x, y in textos_com_posicao:
        y_round = round(y, 1)  # Tolerância de 0.1
        if y_round not in linhas:
            linhas[y_round] = []
        # Converter %%c para ø
        texto_limpo = texto.replace('%%c', 'ø').replace('%%C', 'ø')
        linhas[y_round].append((x, texto_limpo))
    
    # Processar cada linha
    for y in sorted(linhas.keys(), reverse=True):  # De cima para baixo
        textos_linha = sorted(linhas[y], key=lambda t: t[0])  # Ordenar por X
        
        # Detectar pilar na linha
        for x, txt in textos_linha:
            m_pilar = RE_PILAR_NAME.search(txt)
            if m_pilar:
                pilar_atual = f"P{m_pilar.group(1)}"
        
        # Tentar montar linha de dados
        # Padrão comum: POS | BIT | QUANT | COMPRIMENTO
        valores = []
        i = 0
        while i < len(textos_linha):
            x, txt = textos_linha[i]
            txt = txt.strip()
            
            # Pular vazios e separadores
            if not txt or txt in ['|', '-', 'ACO', 'RESUMO', 'AÇO', 'POS', 'BIT', 'QUANT', 'COMPRIMENTO']:
                i += 1
                continue
            
            # Se é ø sozinho, juntar com próximo valor
            if txt in ['ø', 'Ø'] and i + 1 < len(textos_linha):
                _, prox_txt = textos_linha[i + 1]
                valores.append(f"ø{prox_txt}")
                i += 2
                continue
            
            valores.append(txt)
            i += 1
        
        # Tentar extrair: POS, bitola (com ø), quantidade, comprimento
        if len(valores) >= 4:
            try:
                # Procurar em ordem específica para evitar confusão
                pos = None
                bitola = None
                qtd = None
                comp = None
                
                indices_usados = set()
                
                # 1. POS: sempre primeiro (N1, N2, etc)
                for i, val in enumerate(valores):
                    if not pos and re.match(r'^N\d+$', val):
                        pos_match = re.search(r'(\d+)', val)
                        if pos_match:
                            pos = int(pos_match.group(1))
                            indices_usados.add(i)
                            break
                
                # 2. Bitola: sempre tem ø
                for i, val in enumerate(valores):
                    if i in indices_usados:
                        continue
                    if not bitola and ('ø' in val or 'Ø' in val):
                        bit_match = re.search(r'(\d+[.,]?\d*)', val)
                        if bit_match:
                            bitola = float(bit_match.group(1).replace(',', '.'))
                            indices_usados.add(i)
                            break
                
                # 3. Quantidade e Comprimento: ambos são números
                # Quantidade geralmente é menor, comprimento é maior
                numeros_restantes = []
                for i, val in enumerate(valores):
                    if i in indices_usados:
                        continue
                    if re.match(r'^\d+[.,]?\d*$', val):
                        try:
                            n = float(val.replace(',', '.'))
                            numeros_restantes.append((i, n))
                        except:
                            pass
                
                # Separar quantidade (menor, ≤10000) de comprimento (maior, ≥10)
                for i, n in numeros_restantes:
                    if not qtd and 1 <= int(n) <= 10000 and n < 100:
                        qtd = int(n)
                        indices_usados.add(i)
                    elif not comp and 10 <= n <= 5000:
                        comp = n
                        indices_usados.add(i)
                
                # Se encontrou todos os dados
                if pos and bitola and qtd and comp and pilar_atual:
                    comp_m = comp / 100.0
                    peso = _calcular_peso(bitola, comp_m, qtd)
                    formato, medidas = analisar_pilar_geometricamente(f"N{pos}", bitola, comp_m)
                    
                    dados.append((
                        pilar_atual, f"N{pos}", bitola, qtd, round(comp_m, 2),
                        round(peso, 2), formato, medidas
                    ))
            except:
                pass
    
    return dados

def _motor_rapido_desenhos(todos_textos, textos_com_posicao=None):
    """
    Motor rápido para leitura de desenhos/detalhes
    Padrão 1: "4 N1 ø12.5 C=280" (formato estruturado)
    Padrão 2: Textos fragmentados (cada campo separado) - requer textos_com_posicao
    """
    dados = []
    pilar_atual = None
    
    # Padrão regex: qtd N posição ø bitola C= comprimento
    regex = re.compile(
        r'(\d+)\s*N\s*(\d+)\s*.*?[Ø]?\s*(\d+[.]?\d*)\s*.*[CL]\s*[=:\s]?\s*(\d+[.]?\d*)',
        re.IGNORECASE
    )
    
    matches_count = 0
    for texto in todos_textos:
        # Detectar mudança de pilar
        m_pilar = RE_PILAR_NAME.search(texto)
        if m_pilar:
            pilar_atual = f"P{m_pilar.group(1)}"
            continue
        
        # Procurar padrão estruturado
        match = regex.search(texto)
        if match:
            matches_count += 1
            try:
                qtd = int(match.group(1))
                pos = int(match.group(2))
                bitola = float(match.group(3))
                comp_cm = float(match.group(4))
                
                # Validações
                if not _eh_bitola_valida(bitola):
                    continue
                if not (10 <= comp_cm <= 5000):
                    continue
                if not (1 <= pos <= 100 and qtd > 0 and qtd <= 10000):
                    continue
                
                comp_m = comp_cm / 100.0
                peso = _calcular_peso(bitola, comp_m, qtd)
                formato, medidas = analisar_pilar_geometricamente(f"N{pos}", bitola, comp_m)
                
                dados.append((
                    pilar_atual, f"N{pos}", bitola, qtd, round(comp_m, 2),
                    round(peso, 2), formato, medidas
                ))
            except:
                pass
    
    # Se não encontrou dados com padrão estruturado E tem dados com posição, tentar fragmentados
    if not dados and textos_com_posicao:
        print("[MOTOR RAPIDO] Padrão estruturado não encontrado, tentando fragmentados...")
        dados = _processar_textos_fragmentados(textos_com_posicao)
    
    return dados

# ============================================================
# MOTOR COMPLETO - Para tabelas (x > 100)
# ============================================================
# ============================================================
# MOTOR COMPLETO - Para tabelas (x > 100)
# ============================================================
def _expandir_titulos_pilares(titulo_texto):
    """
    Expande nomenclaturas de pilares.
    
    IMPORTANTE: P14=P32(X2) significa que os MESMOS dados valem para P14 e P32
    (não é um intervalo P14-P32, é exatamente 2 pilares: 14 e 32)
    
    Exemplos:
    - "P1" → ["P1"] (pilare simples)
    - "P14-P32" → [P14, P15, ..., P32] (intervalo com hífen)
    - "P14=P32" → [P14, P32] (dois pilares iguais, dados compartilhados)
    - "P14=P32(X2)" → [P14, P32] (confirmação: 2 pilares compartilham dados)
    - "P14=P32=P35(X3)" → [P14, P32, P35] (3 pilares com mesmos dados)
    - "P32(X2)" → [P32] (pilare único, (X2) é apenas confirmação)
    - "P14;P32" → [P14, P32] (separado)
    - "P14/P32" → [P14, P32] (separado)
    
    Retorna lista de nomes de pilares expandidos
    """
    
    # Remover (X2), (X3), etc (multiplicador de confirmação)
    titulo = titulo_texto.split('(')[0].strip()
    
    titulos = []
    
    # Padrão: P1-P5 (intervalo com hífen)
    if '-' in titulo and '=' not in titulo:
        partes = titulo.split('-')
        if len(partes) == 2:
            m1 = re.search(r'P(\d+)', partes[0].strip())
            m2 = re.search(r'P(\d+)', partes[1].strip())
            
            if m1 and m2:
                num1 = int(m1.group(1))
                num2 = int(m2.group(1))
                
                # Gerar intervalo
                for n in range(min(num1, num2), max(num1, num2) + 1):
                    titulos.append(f"P{n}")
    
    # Padrão: P14=P32=P35 (múltiplos pilares com dados compartilhados)
    elif '=' in titulo:
        partes = titulo.split('=')
        for parte in partes:
            m = re.search(r'P(\d+)', parte.strip())
            if m:
                titulos.append(f"P{m.group(1)}")
    
    # Padrão: P1;P3 ou P1/P3 (separados)
    elif ';' in titulo or '/' in titulo:
        sep = ';' if ';' in titulo else '/'
        partes = titulo.split(sep)
        
        for parte in partes:
            m = re.search(r'P(\d+)', parte.strip())
            if m:
                titulos.append(f"P{m.group(1)}")
    
    # Padrão simples: P1, P2, etc
    else:
        m = re.search(r'P\d+', titulo, re.IGNORECASE)
        if m:
            titulos.append(m.group(0).upper())
    
    return titulos

def _motor_completo_tabelas(raw_tokens, table_titles):
    """
    Motor completo para tabelas estruturadas
    Detecta colunas: POS, BIT, QTD, COMP
    """
    entries = []
    
    if not table_titles or not raw_tokens:
        return entries
    
    # Detectar headers - buscar em X > 70 (inclui tabelas entre 70-130)
    header_keywords = {"POS", "BIT", "BITOLA", "QUANT", "QTD", "QTDE", "COMP", "COMPRIMENTO"}
    header_tokens = [t for t in raw_tokens if t["x"] > 70.0 and 
                     any(kw in t["text"].upper().replace(" ", "") for kw in header_keywords)]
    
    if not header_tokens:
        return entries
    
    # Agrupar headers por Y
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
    
    groups = sorted(groups, key=lambda g: -g["y"])
    header_tokens = groups[0]["tokens"] if groups else []
    
    # Mapear colunas - BUSCA EXPLÍCITA pelos headers
    col_x = {}
    for kw in ["POS", "BIT", "BITOLA", "QUANT", "QTD", "QTDE", "COMP", "COMPRIMENTO"]:
        xs = [t["x"] for t in header_tokens if kw in t["text"].upper().replace(" ", "")]
        if xs:
            col_x[kw] = sum(xs) / len(xs)
    
    # Se não encontrou POS, tentar inferir pela estrutura típica
    # POS geralmente é a primeira coluna numérica (após classe do aço)
    if "POS" not in col_x:
        # Procurar valores 1, 2, 3, 4... em sequência na tabela
        numeros_por_x = {}
        for t in raw_tokens:
            # Detectar POS/BIT/QUANT/COMP entre X=70 e X=120 (qualquer tabela)
            if t["x"] > 70 and t["x"] < 120:
                txt = t["text"].replace(" ", "")
                if txt.isdigit() and 1 <= int(txt) <= 20:
                    x_round = round(t["x"])
                    if x_round not in numeros_por_x:
                        numeros_por_x[x_round] = []
                    numeros_por_x[x_round].append(int(txt))
        
        # Procurar X com sequência 1,2,3,4,5...
        melhor_x = None
        melhor_score = 0
        for x, nums in numeros_por_x.items():
            # Contar quantos são sequenciais
            nums_unicos = sorted(set(nums))
            score = 0
            for i, n in enumerate(nums_unicos):
                if i == 0 and n == 1:
                    score += 10
                elif i > 0 and n == nums_unicos[i-1] + 1:
                    score += 5
            
            if score > melhor_score:
                melhor_score = score
                melhor_x = x
        
        if melhor_x:
            col_x["POS"] = melhor_x
            print(f"[MOTOR COMPLETO] POS inferida em X={melhor_x}")
    
    # Normalizar
    if "BITOLA" in col_x and "BIT" not in col_x:
        col_x["BIT"] = col_x["BITOLA"]
    if "COMPRIMENTO" in col_x and "COMP" not in col_x:
        col_x["COMP"] = col_x["COMPRIMENTO"]
    if any(k in col_x for k in ["QTD", "QTDE"]) and "QUANT" not in col_x:
        col_x["QUANT"] = col_x.get("QTD", col_x.get("QTDE"))
    
    needed = ["POS", "BIT", "QUANT", "COMP"]
    if not all(k in col_x for k in needed):
        return entries
    
    print(f"[MOTOR COMPLETO] Colunas: POS={col_x['POS']:.1f}, BIT={col_x['BIT']:.1f}, QUANT={col_x['QUANT']:.1f}, COMP={col_x['COMP']:.1f}")
    
    # Processar cada pilar - com suporte a nomenclatura expandida (P14-P32, etc)
    titles_sorted = sorted(table_titles, key=lambda t: -t["y"])
    
    # Remover títulos duplicados (manter ordem)
    seen = set()
    titles_unique = []
    for t in titles_sorted:
        # Normalizar nome: remover espaços extras e converter para uppercase para comparação
        nome_normalizado = ' '.join(t['nome'].split()).upper()
        if nome_normalizado not in seen:
            seen.add(nome_normalizado)
            titles_unique.append(t)
    
    for idx, title in enumerate(titles_unique):
        y_top = title["y"]
        y_bottom = titles_unique[idx + 1]["y"] if idx + 1 < len(titles_unique) else -1e9
        
        # Textos desta seção - apenas X > 100 (arquivos l1-020 e similares)
        bloco = [t for t in raw_tokens if y_bottom < t["y"] < y_top and t["x"] > 100.0]
        if not bloco:
            continue
        # Agrupar por linha
        bloco_sorted = sorted(bloco, key=lambda t: -t["y"])
        linhas = []
        current = []
        current_y = None
        
        for t in bloco_sorted:
            if current_y is None or abs(t["y"] - current_y) <= 0.2:
                current.append(t)
                current_y = t["y"]
            else:
                linhas.append(current)
                current = [t]
                current_y = t["y"]
        
        if current:
            linhas.append(current)
        
        # Processar linhas
        linhas_por_posicao = {}  # Agrupar por posição para evitar duplicatas
        
        for linha in linhas:
            cols = {k: None for k in needed}
            
            # Coletar todos os números da linha com suas posições X
            numeros_linha = []
            
            for t in sorted(linha, key=lambda tt: tt["x"]):
                # Ignorar coluna de classe do aço (X≈108, valores 50/60)
                if 107 <= t["x"] <= 109:
                    continue
                
                txt = t["text"].replace(" ", "").replace(",", ".")
                mnum = re.search(r'[\d\.]+', txt)
                if not mnum:
                    continue
                
                try:
                    val = float(mnum.group(0))
                    numeros_linha.append({"x": t["x"], "val": val})
                except:
                    continue
            
            # Mapear números para colunas pela proximidade de X
            for num in numeros_linha:
                nearest_col = min(needed, key=lambda k: abs(num["x"] - col_x[k]))
                
                # Se a coluna ainda não foi preenchida
                if cols[nearest_col] is None:
                    val = num["val"]
                    
                    if nearest_col == "BIT":
                        # Normalizar bitola
                        if 40 <= val <= 700:
                            bit_norm = val / 10.0
                            cols[nearest_col] = bit_norm if _eh_bitola_valida(bit_norm) else val
                        else:
                            cols[nearest_col] = val if _eh_bitola_valida(val) else val
                    else:
                        cols[nearest_col] = val
            
            # Validar
            if any(cols[k] is None for k in needed):
                continue
            
            try:
                pos = int(cols["POS"])
                bit = float(cols["BIT"])
                qty = int(cols["QUANT"])
                comp_cm = float(cols["COMP"])
            except:
                continue
            
            if not _eh_bitola_valida(bit):
                continue
            if not (10 <= comp_cm <= 5000):
                continue
            # Validação ajustada: permite até 10000 barras (para grampos/estribos)
            if not (1 <= pos <= 100 and qty > 0 and qty <= 10000):
                continue
            
            # Agrupar por posição - manter apenas a primeira ocorrência
            pos_key = f"N{pos}"
            if pos_key not in linhas_por_posicao:
                comp_m = comp_cm / 100.0
                peso = _calcular_peso(bit, comp_m, qty)
                formato, medidas = analisar_pilar_geometricamente(pos_key, bit, comp_m)
                
                linhas_por_posicao[pos_key] = (
                    title["nome"], pos_key, bit, qty, comp_m, peso, formato, medidas
                )
        
        # NOVO: Expandir títulos com nomenclatura especial (P14-P32, P32(X2), etc)
        # e replicar dados para cada pilar expandido
        titulos_expandidos = _expandir_titulos_pilares(title["nome"])
        
        # Se houve expansão, replicar dados para cada pilar
        if len(titulos_expandidos) > 1:
            # Há múltiplos pilares na nomenclatura
            # Se '=' presente: dividir quantidades (tabela tem soma)
            # Se '-' presente: replicar quantidades (tabela tem por pilar)
            dividir_quantidade = '=' in title["nome"]
            num_pilares = len(titulos_expandidos)
            
            for titulo_expandido in titulos_expandidos:
                for entrada_original in linhas_por_posicao.values():
                    nome_original, pos_key, bit, qty, comp_m, peso, formato, medidas = entrada_original
                    
                    # Se '=' (dados compartilhados): dividir quantidade e peso
                    if dividir_quantidade:
                        qty_ajustado = qty // num_pilares
                        peso_ajustado = peso / num_pilares
                    else:
                        qty_ajustado = qty
                        peso_ajustado = peso
                    
                    entries.append((
                        titulo_expandido,
                        pos_key, bit, qty_ajustado, comp_m, peso_ajustado, formato, medidas
                    ))
        else:
            # Não houve expansão, adicionar normalmente
            for entry in linhas_por_posicao.values():
                entries.append(entry)
    
    return entries

def _motor_completo_tabelas_minor(raw_tokens, table_titles):
    """
    Processa tabelas em 60 < X <= 100 (como arquivo pilares-032/028.DXF)
    """
    entries = []
    
    if not table_titles or not raw_tokens:
        return entries
    
    # Detectar headers em 60 < X <= 100
    header_keywords = {"POS", "BIT", "BITOLA", "QUANT", "QTD", "QTDE", "COMP", "COMPRIMENTO"}
    header_tokens = [t for t in raw_tokens if 60 < t["x"] < 105 and 
                     any(kw in t["text"].upper().replace(" ", "") for kw in header_keywords)]
    
    if not header_tokens:
        return entries
    
    # Agrupar headers por Y
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
    
    groups = sorted(groups, key=lambda g: -g["y"])
    header_tokens = groups[0]["tokens"] if groups else []
    
    # Mapear colunas
    col_x = {}
    for kw in ["POS", "BIT", "BITOLA", "QUANT", "QTD", "QTDE", "COMP", "COMPRIMENTO"]:
        for t in header_tokens:
            if kw in t["text"].upper().replace(" ", ""):
                col_x[kw] = t["x"]
                break
    
    # Normalizar
    if "BITOLA" in col_x and "BIT" not in col_x:
        col_x["BIT"] = col_x["BITOLA"]
    if "COMPRIMENTO" in col_x and "COMP" not in col_x:
        col_x["COMP"] = col_x["COMPRIMENTO"]
    if any(k in col_x for k in ["QTD", "QTDE"]) and "QUANT" not in col_x:
        col_x["QUANT"] = col_x.get("QTD", col_x.get("QTDE"))
    
    needed = ["POS", "BIT", "QUANT", "COMP"]
    if not all(k in col_x for k in needed):
        return entries
    
    print(f"[MOTOR COMPLETO-MINOR] Colunas (headers): POS={col_x['POS']:.1f}, BIT={col_x['BIT']:.1f}, QUANT={col_x['QUANT']:.1f}, COMP={col_x['COMP']:.1f}")
    
    # Processar cada pilar
    titles_sorted = sorted(table_titles, key=lambda t: -t["y"])
    
    # Remover títulos duplicados
    seen = set()
    titles_unique = []
    for t in titles_sorted:
        nome_normalizado = ' '.join(t['nome'].split()).upper()
        if nome_normalizado not in seen:
            seen.add(nome_normalizado)
            titles_unique.append(t)
    
    for idx, title in enumerate(titles_unique):
        y_top = title["y"]
        y_bottom = titles_unique[idx + 1]["y"] if idx + 1 < len(titles_unique) else -1e9
        
        # Textos desta seção - X entre 60 e 105
        bloco = [t for t in raw_tokens if y_bottom < t["y"] < y_top and 60 < t["x"] < 105]
        if not bloco:
            continue
        
        # Agrupar por linha (tolerância reduzida para evitar agrupamento incorreto)
        bloco_sorted = sorted(bloco, key=lambda t: -t["y"])
        linhas = []
        current = []
        current_y = None
        
        for t in bloco_sorted:
            if current_y is None or abs(t["y"] - current_y) <= 0.15:
                current.append(t)
                current_y = t["y"]
            else:
                linhas.append(current)
                current = [t]
                current_y = t["y"]
        
        if current:
            linhas.append(current)
        
        # Processar linhas (não agrupa por posição - cada linha é única)
        linhas_validas = []
        
        for linha in linhas:
            cols = {k: None for k in needed}
            
            # Coletar números (ignorar coluna AÇO em várias posições)
            numeros_linha = []
            
            for t in sorted(linha, key=lambda tt: tt["x"]):
                # Ignorar coluna AÇO (valores 50/60/CA50/CA60 em diferentes posições)
                txt_clean = t["text"].replace(" ", "").upper()
                if txt_clean in ["50", "60", "CA50", "CA60", "AÇO", "ACO"]:
                    continue
                
                txt = t["text"].replace(" ", "").replace(",", ".")
                mnum = re.search(r'[\d\.]+', txt)
                if not mnum:
                    continue
                
                try:
                    val = float(mnum.group(0))
                    
                    # Ignorar valores 50/60 que estão muito longe das colunas esperadas
                    # (provavelmente são tipo de aço, não posições)
                    if val in [50, 60]:
                        # Verificar se está perto de alguma coluna esperada
                        dists = [abs(t["x"] - col_x[k]) for k in needed]
                        if min(dists) > 1.5:  # Muito longe de todas as colunas
                            continue
                    
                    numeros_linha.append({"x": t["x"], "val": val})
                except:
                    continue
            
            # Mapear para colunas
            for num in numeros_linha:
                nearest_col = min(needed, key=lambda k: abs(num["x"] - col_x[k]))
                
                # Evitar mapear valores muito distantes (tolerância 2.5)
                distancia = abs(num["x"] - col_x[nearest_col])
                if distancia > 2.5:
                    continue
                
                if cols[nearest_col] is None:
                    val = num["val"]
                    
                    if nearest_col == "BIT":
                        if 40 <= val <= 700:
                            bit_norm = val / 10.0
                            cols[nearest_col] = bit_norm if _eh_bitola_valida(bit_norm) else val
                        else:
                            cols[nearest_col] = val if _eh_bitola_valida(val) else val
                    else:
                        cols[nearest_col] = val
            
            # Validar
            if any(cols[k] is None for k in needed):
                continue
            
            try:
                pos = int(cols["POS"])
                bit = float(cols["BIT"])
                qty = int(cols["QUANT"])
                comp_cm = float(cols["COMP"])
            except:
                continue
            
            if not _eh_bitola_valida(bit):
                continue
            if not (10 <= comp_cm <= 5000):
                continue
            if not (1 <= pos <= 100 and qty > 0 and qty <= 10000):
                continue
            
            # Adicionar linha válida (sem agrupar - cada linha é independente)
            pos_key = f"N{pos}"
            comp_m = comp_cm / 100.0
            peso = _calcular_peso(bit, comp_m, qty)
            formato, medidas = analisar_pilar_geometricamente(pos_key, bit, comp_m)
            
            linhas_validas.append((
                title["nome"], pos_key, bit, qty, comp_m, peso, formato, medidas
            ))
        
        # Expandir nomenclaturas e adicionar
        titulos_expandidos = _expandir_titulos_pilares(title["nome"])
        
        if titulos_expandidos:
            for entry in linhas_validas:
                dividir_quantidade = '=' in title["nome"]
                num_pilares = len(titulos_expandidos)
                
                if dividir_quantidade and num_pilares > 0:
                    qty_ajustado = entry[3] // num_pilares
                    peso_ajustado = entry[5] / num_pilares
                else:
                    qty_ajustado = entry[3]
                    peso_ajustado = entry[5]
                
                for titulo_expandido in titulos_expandidos:
                    entries.append((
                        titulo_expandido,
                        entry[1], entry[2], qty_ajustado, entry[4], peso_ajustado, entry[6], entry[7]
                    ))
        else:
            for entry in linhas_validas:
                entries.append(entry)
    
    return entries

# ============================================================
# FUNÇÃO PRINCIPAL - INTEGRAÇÃO DOS DOIS MOTORES
# ============================================================
def processar_pilares(arquivos):
    """
    Processa pilares com dual motor:
    1. Motor Rápido para desenhos (x < 100)
    2. Motor Completo para tabelas (x > 100)
    3. Motor Completo-Minor para tabelas em X < 90
    """
    
    if not EZDXF_DISPONIVEL:
        # MOCK original
        dados_mock = [
            ("P1", "N1", 6.3, 50, 1.40, 4.88, "ESTRIBO (12)", [0.25, 0.40]),
            ("P1", "N2", 12.5, 4, 3.80, 14.63, "BARRA U (11)", [0.15, 3.50, 0.15]),
        ]
        total_kg = sum(x[5] for x in dados_mock)
        total_barras = sum(x[3] for x in dados_mock)
        return dados_mock, total_kg, total_barras
    
    dados_completos = []
    peso_total = 0.0
    total_barras = 0
    pilares_encontrados = set()
    
    for arquivo in arquivos:
        try:
            doc, auditor = recover_readfile(arquivo)
            msp = doc.modelspace()  # Adicionar modelspace
            todos_textos = []
            raw_tokens = []
            table_titles = []
            
            # Coleta de textos COM posições para fragmentados
            textos_com_posicao = []  # Para Motor Rápido fragmentado
            
            # Coleta de textos - usar query() para capturar MTEXT corretamente
            for entity in list(msp.query('TEXT')) + list(msp.query('MTEXT')):
                if not entity.is_alive:
                    continue
                
                txt = ""
                x, y = 0.0, 0.0
                
                try:
                    if entity.dxftype() == 'TEXT':
                        txt = entity.dxf.text
                        x, y = entity.dxf.insert.x, entity.dxf.insert.y
                    elif entity.dxftype() == 'MTEXT':
                        txt = entity.plain_text()
                        x, y = entity.dxf.insert.x, entity.dxf.insert.y
                except:
                    pass
                
                if txt:
                    # Motor Rápido processa textos BRUTOS (sem limpeza agressiva)
                    # Coletar para Motor Rápido SEM filtro X < 100 (pode estar em qualquer lugar)
                    todos_textos.append(txt)  # Texto BRUTO para motor rápido
                    # Guardar também com posição para fragmentados
                    textos_com_posicao.append((txt, x, y))
                    
                    # Motor Completo usa textos limpos
                    limpo = _limpar_texto_bruto(txt)
                    if limpo:
                        # Adicionar para método completo (tabelas)
                        raw_tokens.append({"text": txt, "x": x, "y": y})
                        
                        # Detectar títulos de pilares preservando expansão
                        titulo_limpo = _limpar_texto_titulo(txt)
                        titulo_sem_espacos = re.sub(r'\s+', '', titulo_limpo)
                        # Ignorar linhas-resumo com muitos pilares separados por '/'
                        if '/' in titulo_sem_espacos and titulo_sem_espacos.count('P') > 2:
                            m_pilar = None
                        else:
                            m_pilar = RE_PILAR_FULL.search(titulo_limpo)
                        if m_pilar:
                            pilar_nome = re.sub(r'\s+', '', m_pilar.group(1))
                            # Buscar em X > 100 (arquivo l1-020)
                            # OU em X < 100 com tabela perto (arquivo 032/028)
                            # Usar heurística: se tem título de pilar e x < 100, é tabela menor
                            if x > 100 or (x < 100 and any(p in pilar_nome for p in ['P', 'p'])):
                                table_titles.append({"nome": pilar_nome, "x": x, "y": y})
                            for p in _expandir_titulos_pilares(pilar_nome):
                                pilares_encontrados.add(p)
            
            # ========== PRIORIDADE 1: MOTOR COMPLETO (Tabelas X > 100) ==========
            print(f"\n[PROCESSAMENTO] Iniciando leitura do arquivo: {arquivo}")
            
            pilares_processados = set()  # Inicializar
            
            # Separar títulos por faixa X
            table_titles_major = [t for t in table_titles if t["x"] > 100]
            table_titles_minor = [t for t in table_titles if 60 < t["x"] <= 100]  # Intermediários
            
            # Motor Completo para X > 100
            if raw_tokens and table_titles_major:
                tabela_dados = _motor_completo_tabelas(raw_tokens, table_titles_major)
                
                # Só considera sucesso se extrair dados SIGNIFICATIVOS (mínimo 5 linhas)
                if tabela_dados and len(tabela_dados) >= 5:
                    print(f"[MOTOR COMPLETO] Detectados {len(table_titles_major)} títulos, extraidas {len(tabela_dados)} linhas")
                    
                    for entry in tabela_dados:
                        dados_completos.append(entry)
                        peso_total += entry[5]
                        total_barras += entry[3]
                    
                    # Remover pilares processados APENAS se realmente extraiu dados
                    pilares_processados = {entry[0] for entry in tabela_dados}
                # Se não extraiu dados SUFICIENTES, deixa pilares_processados vazio para Motor Rápido tentar
            
            # Motor Completo-Minor para X < 70
            if raw_tokens and table_titles_minor and not pilares_processados:
                tabela_dados_minor = _motor_completo_tabelas_minor(raw_tokens, table_titles_minor)
                
                # Só considera sucesso se extrair dados SIGNIFICATIVOS (mínimo 5 linhas)
                if tabela_dados_minor and len(tabela_dados_minor) >= 5:
                    print(f"[MOTOR COMPLETO-MINOR] Detectados {len(table_titles_minor)} títulos, extraidas {len(tabela_dados_minor)} linhas")
                    
                    for entry in tabela_dados_minor:
                        dados_completos.append(entry)
                        peso_total += entry[5]
                        total_barras += entry[3]
                    
                    # Remover pilares processados APENAS se realmente extraiu dados
                    pilares_processados = {entry[0] for entry in tabela_dados_minor}
                # Se não extraiu dados SUFICIENTES, deixa pilares_processados vazio para Motor Rápido tentar
            
            # ========== PRIORIDADE 2: MOTOR RÁPIDO (Desenhos) ==========
            # Apenas para pilares NÃO processados pela tabela
            if todos_textos:
                rapido_dados = _motor_rapido_desenhos(todos_textos, textos_com_posicao)
                
                # Filtrar apenas pilares ainda não processados
                if rapido_dados:
                    rapido_dados_filtrado = [d for d in rapido_dados if d[0] not in pilares_processados]
                    
                    if rapido_dados_filtrado:
                        print(f"[MOTOR RÁPIDO] Extraidas {len(rapido_dados_filtrado)} linhas de desenhos")
                        
                        for entry in rapido_dados_filtrado:
                            dados_completos.append(entry)
                            peso_total += entry[5]
                            total_barras += entry[3]
                    else:
                        # Se não processou NADA, avisar
                        if not pilares_processados:
                            print(f"[AVISO] Detectados pilares {sorted(pilares_encontrados)} mas formato não compatível")
                            print(f"[AVISO] Arquivo pode ter tabela com textos muito fragmentados")
                        else:
                            print(f"[MOTOR RÁPIDO] Nenhum pilar novo encontrado (tabela processou todos)")
                else:
                    # rapido_dados está vazio
                    if not pilares_processados:
                        print(f"[AVISO] Detectados pilares {sorted(pilares_encontrados)} mas formato não compatível")
                        print(f"[AVISO] Arquivo pode ter tabela com textos muito fragmentados")
                    else:
                        print(f"[MOTOR RÁPIDO] Nenhum pilar novo encontrado (tabela processou todos)")
        
        except Exception as e:
            print(f"[ERRO] Arquivo {arquivo}: {e}")
            import traceback
            traceback.print_exc()
    
    # Ordenação final
    def sort_key(x):
        try:
            np = int(re.search(r'\d+', x[0]).group())
            nn = int(re.search(r'\d+', x[1]).group())
            return (np, nn)
        except:
            return (999, 0)
    
    dados_completos.sort(key=sort_key)
    
    print(f"\n[RESULTADO FINAL] Total: {total_barras} barras, {peso_total:.2f} kg")
    print(f"[PILARES] {sorted(pilares_encontrados)}\n")
    
    return dados_completos, peso_total, total_barras
