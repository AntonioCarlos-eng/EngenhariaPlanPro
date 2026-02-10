# core/lajes_motor.py - MOTOR DE EXTRAÇÃO PARA LAJES (Leitura Estrutural de Tabelas)
import re
import os
from typing import Tuple, List, Any, Optional, Dict

# Extração baseada em estrutura de tabela (linhas e colunas)
try:
    import ezdxf
    from ezdxf.recover import readfile as recover_readfile
    EZDXF_DISPONIVEL = True
except ImportError:
    EZDXF_DISPONIVEL = False

# --- CONSTANTES ---
BITOLAS_VALIDAS = [
    3.4, 4.0, 4.2, 5.0, 6.0, 6.3, 8.0, 
    10.0, 12.5, 16.0, 20.0, 22.0, 25.0, 32.0, 40.0
]

# Padrões para detectar tipo de armadura no DXF
RE_ARMADURA_POS = re.compile(r'POSITIV|INFERIOR|INF\b|POS\b', re.IGNORECASE)
RE_ARMADURA_NEG = re.compile(r'NEGATIV|SUPERIOR|SUP\b|NEG\b|TOPO', re.IGNORECASE)
RE_ARMADURA_H = re.compile(r'HORIZONTAL|HORIZ|H\b', re.IGNORECASE)
RE_ARMADURA_V = re.compile(r'VERTICAL|VERT|V\b', re.IGNORECASE)

# --- FUNÇÕES AUXILIARES ---

def _calcular_peso(bitola_mm, comp_m, qtde):
    """Função auxiliar genérica para cálculo de peso."""
    peso_por_metro = (bitola_mm ** 2) * 0.00617
    return peso_por_metro * comp_m * qtde

def _eh_bitola_valida(valor):
    """Verifica se é bitola comercial com tolerância."""
    for b in BITOLAS_VALIDAS:
        if abs(valor - b) < 0.3:
            return True
    return False

def _detectar_tipo_armadura(titulo_texto: str) -> Tuple[str, str]:
    """
    Detecta o tipo de armadura (POSITIVA/NEGATIVA, HORIZONTAL/VERTICAL).
    Retorna: (classificacao, direcao)
    """
    classificacao = "NEGATIVA"  # padrão
    if RE_ARMADURA_POS.search(titulo_texto):
        classificacao = "POSITIVA"
    
    direcao = "HORIZONTAL"  # padrão
    if RE_ARMADURA_V.search(titulo_texto):
        direcao = "VERTICAL"
    
    return classificacao, direcao

def _agrupar_textos_por_coordenada(textos_com_coords: List[Tuple[str, float, float]], tolerancia_y=0.2) -> List[List[Tuple[str, float, float]]]:
    """
    Agrupa textos por coordenada Y (linhas da tabela), depois ordena por X (colunas).
    """
    if not textos_com_coords:
        return []
    
    # Ordenar por Y para facilitar agrupamento
    textos_ordenados = sorted(textos_com_coords, key=lambda t: t[2], reverse=True)
    
    linhas = []
    linha_atual = []
    y_ref = None
    
    for texto, x, y in textos_ordenados:
        if y_ref is None:
            y_ref = y
            linha_atual = [(texto, x, y)]
        elif abs(y - y_ref) <= tolerancia_y:
            # Mesma linha
            linha_atual.append((texto, x, y))
        else:
            # Nova linha
            if linha_atual:
                # Ordena a linha atual por X (da esquerda para direita)
                linha_atual_ordenada = sorted(linha_atual, key=lambda t: t[1])
                linhas.append(linha_atual_ordenada)
            y_ref = y
            linha_atual = [(texto, x, y)]
    
    # Adiciona última linha
    if linha_atual:
        linha_atual_ordenada = sorted(linha_atual, key=lambda t: t[1])
        linhas.append(linha_atual_ordenada)
    
    return linhas

def _eh_cabecalho(tokens: List[str]) -> bool:
    """Detecta se uma linha é cabeçalho de tabela."""
    palavras_cabecalho = ['AÇO', 'POS', 'BIT', 'QUANT', 'COMP', 'PESO', 'QTD', 'UNIT', 'TOTAL']
    for token in tokens:
        for palavra in palavras_cabecalho:
            if palavra in token.upper():
                return True
    return False

def _extrair_dados_tabela(linhas_tabela: List[List[Tuple[str, float, float]]]) -> List[Tuple[int, float, int, int, bool]]:
    """
    Extrai dados estruturados de uma tabela: (posicao, bitola, comprimento_cm, quantidade, comp_total).
    Usa as colunas por coordenada X (POS, BIT, QUANT, COMP, TOTAL) para evitar mistura de tokens.
    Suporta medidas variáveis: quando COMP = "--VAR--", usa coluna TOTAL.
    """
    dados = []
    
    # Detecta colunas pelo cabeçalho
    header_idx = None
    col_x = {}
    for idx, linha in enumerate(linhas_tabela):
        textos = [t for t, _, _ in linha]
        if _eh_cabecalho(textos):
            for texto, x, _ in linha:
                up = texto.upper()
                if 'POS' in up:
                    col_x['pos'] = x
                elif 'BIT' in up:
                    col_x['bit'] = x
                elif 'QUANT' in up or 'QTD' in up:
                    col_x['quant'] = x
                elif 'COMP' in up and 'UNIT' not in up:  # Coluna COMPRIMENTO (pode ser UNIT ou TOTAL)
                    col_x['comp'] = x
                elif 'UNIT' in up:  # Coluna COMPRIMENTO UNITÁRIO
                    col_x['comp_unit'] = x
                elif 'TOTAL' in up:  # Coluna COMPRIMENTO TOTAL (para variáveis)
                    col_x['comp_total'] = x
                elif 'AÇO' in up or 'ACO' in up:
                    col_x['aco'] = x
            header_idx = idx
            break
    
    # Se encontrou cabeçalho, tenta detectar UNIT/TOTAL nas linhas seguintes
    if header_idx is not None:
        for linha in linhas_tabela[header_idx + 1:header_idx + 4]:
            for texto, x, _ in linha:
                up = texto.upper()
                if 'UNIT' in up and 'comp_unit' not in col_x:
                    col_x['comp_unit'] = x
                elif 'TOTAL' in up and 'comp_total' not in col_x:
                    col_x['comp_total'] = x

    # Se não encontrou cabeçalho, tenta parsing simples por ordem
    if header_idx is None or not all(k in col_x for k in ['pos', 'bit', 'quant']):
        # Fallback: parsing simples sem detecção de coluna
        for tokens in linhas_tabela:
            textos = [t for t, _, _ in tokens]
            if _eh_cabecalho(textos) or len(textos) < 5:
                continue
            tokens_clean = [t.strip() for t in textos if t.strip()]
            if len(tokens_clean) < 5:
                continue
            try:
                posicao = int(tokens_clean[1])
                bitola = float(tokens_clean[2].replace(',', '.'))
                quantidade = int(tokens_clean[3])
                comprimento = int(tokens_clean[4])
                if _eh_bitola_valida(bitola) and 0 < posicao < 200 and quantidade > 0 and comprimento > 0:
                    dados.append((posicao, bitola, comprimento, quantidade, False))
            except (ValueError, IndexError):
                continue
        return dados
    
    # Função para pegar token mais próximo da coluna
    def _token_proximo(linha, x_alvo, regex_num=None, tolerancia=0.8, permitir_var=False):
        candidato = None
        menor = None
        for texto, x, _ in linha:
            texto_strip = texto.strip()
            
            # Se permite "variável" e encontrou, retorna especial
            if permitir_var and ('VAR' in texto_strip.upper() or '--VAR' in texto_strip):
                dist = abs(x - x_alvo)
                if dist <= tolerancia:
                    return "--VAR--"
            
            # Caso contrário, procura por número
            if regex_num and not re.match(regex_num, texto_strip):
                continue
            elif not regex_num:
                # Se não tem regex, procura por algo que pareça número
                if not re.match(r'^[\d\s.,]+$', texto_strip):
                    continue
            
            dist = abs(x - x_alvo)
            if menor is None or dist < menor:
                menor = dist
                candidato = texto_strip
        
        if menor is not None and menor <= tolerancia:
            return candidato
        return None
    
    # Lê linhas após o cabeçalho
    for linha in linhas_tabela[header_idx + 1:]:
        pos_str = _token_proximo(linha, col_x['pos'], r'^\d+$')
        bit_str = _token_proximo(linha, col_x['bit'], r'^\d+[.,]?\d*$')
        qtd_str = _token_proximo(linha, col_x['quant'], r'^\d+$')
        
        # Tenta coluna UNIT primeiro (se existir), senão usa COMP
        comp_col = col_x.get('comp_unit', col_x.get('comp'))
        comp_str = _token_proximo(linha, comp_col, r'^\d+$|^--VAR', permitir_var=True)
        
        # Se encontrou "--VAR--" na coluna unitária, tenta pegar da coluna TOTAL
        comp_total = False
        if comp_str == "--VAR--":
            if 'comp_total' in col_x:
                comp_str = _token_proximo(linha, col_x['comp_total'], r'^\d+$')
            else:
                # fallback: procurar o número mais próximo à direita da coluna COMP
                total_candidato = None
                menor = None
                for texto, x, _ in linha:
                    if x <= comp_col:
                        continue
                    texto_strip = texto.strip()
                    if not re.match(r'^\d+$', texto_strip):
                        continue
                    dist = abs(x - comp_col)
                    if menor is None or dist < menor:
                        menor = dist
                        total_candidato = texto_strip
                if total_candidato:
                    comp_str = total_candidato
            if comp_str:
                comp_total = True
        
        if not (pos_str and bit_str and qtd_str and comp_str):
            continue
        
        try:
            posicao = int(pos_str)
            bitola = float(bit_str.replace(',', '.'))
            quantidade = int(qtd_str)
            comprimento = int(comp_str)
            if _eh_bitola_valida(bitola) and 0 < posicao < 200 and quantidade > 0 and comprimento > 0:
                dados.append((posicao, bitola, comprimento, quantidade, comp_total))
        except ValueError:
            continue
    
    return dados

def analisar_barra_geometricamente(pos: str, bitola: float, comp_m: float, classificacao: str) -> Tuple[str, List[float]]:
    """Classifica reforços de laje como RETA, L ou U."""
    gancho = 0.15 
    
    # Regra da laje: POSITIVA = reta, NEGATIVA = dobra dos dois lados (U)
    if classificacao == "POSITIVA":
        return "RETA (01)", [comp_m]

    if classificacao == "NEGATIVA":
        vao_u = comp_m - 2 * gancho
        if vao_u < 0:
            vao_u = 0.0
        return "BARRA U (11)", [gancho, vao_u, gancho]
            
    return "RETA (01)", [comp_m]


def processar_lajes(arquivos):
    """
    Processa arquivos DXF lendo tabelas estruturalmente.
    Detecta tipo de armadura, agrupa por posição, soma Ns repetidos.
    Retorna (elemento, pos_tipo, bitola, qtde, comp_m, largura_m, peso_kg, formato_dobra, medidas_m)
    """
    if not EZDXF_DISPONIVEL:
        print("ezdxf não disponível")
        return [], 0.0, 0
    
    if not arquivos:
        return [], 0.0, 0
         
    dados_completos = []
    peso_total_geral = 0.0
    total_pecas_geral = 0
    
    for arquivo in arquivos:
        try:
            print(f"\nProcessando: {os.path.basename(arquivo)}")
            doc, auditor = recover_readfile(arquivo)
            
            # Extrai todos os textos com suas coordenadas
            textos_com_coords = []
            titulo_armadura = ""
            
            for entity in doc.entities:
                if not entity.is_alive:
                    continue
                    
                txt = ""
                x, y = 0.0, 0.0
                
                try:
                    if entity.dxftype() == 'TEXT':
                        txt = entity.dxf.text
                        x = entity.dxf.insert[0]
                        y = entity.dxf.insert[1]
                    elif entity.dxftype() == 'MTEXT':
                        txt = entity.plain_text()
                        x = entity.dxf.insert[0]
                        y = entity.dxf.insert[1]
                except:
                    pass
                
                if txt and txt.strip():
                    textos_com_coords.append((txt.strip(), x, y))
                    # Procura por titulo de armadura
                    if any(palavra in txt.upper() for palavra in ['ARMAD', 'POSITIV', 'NEGATIV']):
                        titulo_armadura = txt
            
            print(f"  Textos encontrados: {len(textos_com_coords)}")
            
            # Determina tipo de armadura
            classificacao, direcao = _detectar_tipo_armadura(titulo_armadura)
            print(f"  Tipo: {classificacao} {direcao}")
            
            # Determina nome da laje
            laje_name_parts = os.path.basename(arquivo).replace('.DXF', '').replace('.DWG', '').replace('-', ' ').split()
            laje_atual = f"LAJE {laje_name_parts[-1].upper()}"
            
            # Agrupa textos por linha (coordenada Y)
            linhas_agrupadas = _agrupar_textos_por_coordenada(textos_com_coords, tolerancia_y=0.25)
            print(f"  Linhas agrupadas: {len(linhas_agrupadas)}")
            
            # Extrai dados da tabela (usando coordenadas X das colunas)
            dados_tabela = _extrair_dados_tabela(linhas_agrupadas)
            print(f"  Linhas de tabela extraídas: {len(dados_tabela)}")
            
            # Agrupa por posição (soma Ns repetidos)
            # (pos, bitola) -> (qtde_total, comp_cm, comp_total)
            agrupado_por_pos: Dict[Tuple[int, float], Tuple[int, int, bool]] = {}
            
            for pos, bitola, comp_cm, quantidade, comp_total in dados_tabela:
                chave = (pos, bitola)
                if chave in agrupado_por_pos:
                    qtde_atual, comp_atual, comp_total_atual = agrupado_por_pos[chave]
                    qtde_somada = qtde_atual + quantidade
                    if comp_total or comp_total_atual:
                        # Se algum for total, mantém como total (soma se ambos forem totais)
                        if comp_total and comp_total_atual:
                            comp_novo = comp_atual + int(comp_cm)
                        else:
                            comp_novo = int(comp_cm) if comp_total else comp_atual
                        agrupado_por_pos[chave] = (qtde_somada, comp_novo, True)
                    else:
                        agrupado_por_pos[chave] = (qtde_somada, int(comp_cm), False)
                else:
                    agrupado_por_pos[chave] = (quantidade, int(comp_cm), comp_total)
            
            print(f"  Posições únicas (após agrupar): {len(agrupado_por_pos)}")
            
            # Processa posições
            for (pos, bitola), (qtde_total, comp_cm, comp_total) in agrupado_por_pos.items():
                # Tipo de armadura expandido: NEG/HOR, NEG/VER, POS/HOR, POS/VER
                classif_completa = "NEG" if classificacao == "NEGATIVA" else "POS"
                direcao_completa = "HOR" if direcao == "HORIZONTAL" else "VER"
                tipo_armadura = f"{classif_completa}/{direcao_completa}"
                
                # ELEMENTO: LAJE + tipo (sem número da laje)
                elemento_completo = f"LAJE {tipo_armadura}"
                
                # TIPO/POS: apenas N1, N2, etc (sem tag)
                pos_tipo = f"N{pos}"
                
                comp_m = comp_cm / 100.0
                if comp_total:
                    peso = _calcular_peso(bitola, comp_m, 1)
                else:
                    peso = _calcular_peso(bitola, comp_m, qtde_total)

                formato_dobra, medidas_m = analisar_barra_geometricamente(pos_tipo, bitola, comp_m, classificacao)
                
                # Usar coluna largura para indicar se é VARIÁVEL ou NORMAL
                largura_info = "VARIÁVEL" if comp_total else "NORMAL"
                
                dados_completos.append((
                    elemento_completo, pos_tipo, bitola, float(qtde_total), round(comp_m, 2), 
                    largura_info, 
                    round(peso, 2), formato_dobra, medidas_m
                ))
                peso_total_geral += peso
                total_pecas_geral += qtde_total

        except Exception as e:
            print(f"Erro ao processar arquivo {arquivo}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nTotal: {len(dados_completos)} posicoes | {total_pecas_geral} barras | {peso_total_geral:.2f} kg")
    
    # Ordenar dados por laje e depois por número da posição
    def extrair_numero_posicao(dado):
        pos_str = dado[1]  # pos_tipo é o segundo elemento
        match = re.search(r'N(\d+)', pos_str)
        return int(match.group(1)) if match else 999
    
    dados_completos_ordenados = sorted(dados_completos, key=lambda d: (d[0], extrair_numero_posicao(d)))
    
    return dados_completos_ordenados, peso_total_geral, total_pecas_geral
