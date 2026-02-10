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

def _extrair_dados_tabela(linhas_tabela: List[List[str]]) -> List[Tuple[int, float, int, int]]:
    """
    Extrai dados estruturados de uma tabela: (posicao, bitola, comprimento_cm, quantidade).
    """
    dados = []
    
    for tokens in linhas_tabela:
        if _eh_cabecalho(tokens) or len(tokens) < 3:
            continue
        
        # Limpa tokens
        tokens_clean = [t.strip() for t in tokens if t.strip()]
        
        # Procura por POS, BIT, QUANT, COMPR em ordem
        posicao = None
        bitola = None
        quantidade = None
        comprimento = None
        
        # Estratégia: procura por padrões em sequência
        for token in tokens_clean:
            token_upper = token.upper()
            
            # POS (número simples como N1, 1, etc)
            if posicao is None:
                match_pos = re.search(r'N?(\d+)', token_upper)
                if match_pos:
                    try:
                        pos_num = int(match_pos.group(1))
                        if pos_num < 100:  # Número de posição válido
                            posicao = pos_num
                            continue
                    except:
                        pass
            
            # BITOLA (ex: 6.3, 8, 10.0, %%c 6.3)
            if bitola is None:
                match_bit = re.search(r'(\d+[.,]?\d*)', token)
                if match_bit:
                    try:
                        bit_val = float(match_bit.group(1).replace(',', '.'))
                        if _eh_bitola_valida(bit_val):
                            bitola = bit_val
                            continue
                    except:
                        pass
            
            # QUANTIDADE (número grande como 25, 350, 1246)
            if quantidade is None and posicao is not None:
                match_qty = re.search(r'^(\d+)$', token)
                if match_qty:
                    try:
                        qty_val = int(match_qty.group(1))
                        if qty_val > 0 and qty_val < 10000:  # Quantidade válida
                            quantidade = qty_val
                            continue
                    except:
                        pass
            
            # COMPRIMENTO (ex: 486, 569, C=486)
            if comprimento is None:
                match_comp = re.search(r'C?=?(\d+)', token)
                if match_comp:
                    try:
                        comp_val = int(match_comp.group(1))
                        if comp_val > 50 and comp_val < 5000:  # Comprimento válido (cm)
                            comprimento = comp_val
                            continue
                    except:
                        pass
        
        # Validação
        if posicao is not None and bitola is not None and quantidade is not None and comprimento is not None:
            dados.append((posicao, bitola, comprimento, quantidade))
    
    return dados

def analisar_barra_geometricamente(pos: str, bitola: float, comp_m: float, classificacao: str) -> Tuple[str, List[float]]:
    """Classifica reforços de laje como RETA, L ou U."""
    gancho = 0.15 
    
    if classificacao == "POSITIVA" or comp_m < 3.0:
        return "RETA (01)", [comp_m]

    elif classificacao == "NEGATIVA":
        if comp_m < 5.0: 
            vao_l = comp_m - gancho
            if vao_l > 0.5:
                return "DOBRA L (13)", [gancho, vao_l]
        
        vao_u = comp_m - 2 * gancho
        if vao_u > 1.0:
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
            
            # Extrai dados da tabela
            linhas_tokens = [[texto for texto, x, y in linha] for linha in linhas_agrupadas]
            dados_tabela = _extrair_dados_tabela(linhas_tokens)
            print(f"  Linhas de tabela extraídas: {len(dados_tabela)}")
            
            # Agrupa por posição (soma Ns repetidos)
            agrupado_por_pos: Dict[Tuple[int, float], Tuple[int, int]] = {}  # (pos, bitola) -> (qtde_total, comp_cm)
            
            for pos, bitola, comp_cm, quantidade in dados_tabela:
                chave = (pos, bitola)
                if chave in agrupado_por_pos:
                    qtde_atual, comp_atual = agrupado_por_pos[chave]
                    agrupado_por_pos[chave] = (qtde_atual + quantidade, comp_cm)  # Soma quantidade, última comprimento
                else:
                    agrupado_por_pos[chave] = (quantidade, int(comp_cm))
            
            print(f"  Posições únicas (após agrupar): {len(agrupado_por_pos)}")
            
            # Processa posições
            for (pos, bitola), (qtde_total, comp_cm) in agrupado_por_pos.items():
                classif_tag = f" ({classificacao[0]}/{direcao[0]})"
                pos_tipo = f"N{pos}{classif_tag}"
                
                comp_m = comp_cm / 100.0
                peso = _calcular_peso(bitola, comp_m, qtde_total)

                formato_dobra, medidas_m = analisar_barra_geometricamente(pos_tipo, bitola, comp_m, classificacao)
                
                dados_completos.append((
                    laje_atual, pos_tipo, bitola, float(qtde_total), round(comp_m, 2), 
                    0.0, 
                    round(peso, 2), formato_dobra, medidas_m
                ))
                peso_total_geral += peso
                total_pecas_geral += qtde_total

        except Exception as e:
            print(f"❌ Erro ao processar arquivo {arquivo}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ Total: {len(dados_completos)} posições | {total_pecas_geral} barras | {peso_total_geral:.2f} kg")
    
    # Ordenar dados por laje e depois por número da posição
    def extrair_numero_posicao(dado):
        pos_str = dado[1]  # pos_tipo é o segundo elemento
        match = re.search(r'N(\d+)', pos_str)
        return int(match.group(1)) if match else 999
    
    dados_completos_ordenados = sorted(dados_completos, key=lambda d: (d[0], extrair_numero_posicao(d)))
    
    return dados_completos_ordenados, peso_total_geral, total_pecas_geral
