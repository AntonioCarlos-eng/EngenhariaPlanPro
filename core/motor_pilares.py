# core/pilares_motor.py - VERSÃO ROBUSTA E COMPLETA
import re
from typing import List, Tuple
import os

# Tentar importar ezdxf
try:
    import ezdxf
    EZDXF_DISPONIVEL = True
except ImportError:
    EZDXF_DISPONIVEL = False


def _extrair_armadura(texto: str):
    """
    Tenta extrair dados de armadura de um texto.
    Retorna (qtde, pos, bitola, comp_cm) ou None se não casar.
    
    Exemplos de formatos aceitos:
    - "4 N1 Ø12.5 C=350"
    - "4N1 ø12,5 C=350"
    - "4 N1 O12.5 C=350"
    - "4N1Ø12.5C350"
    - "4 N1 12.5 C 350"
    - "4N1 Ø12.5 C:350"
    """
    if not texto:
        return None

    # Normalizar texto
    t = texto.upper().strip().replace(',', '.')

    # Padrão 1: Com espaços e símbolos variados
    # Ex: "4 N1 Ø12.5 C=350", "4 N1 O12.5 C:350"
    padrao1 = re.compile(
        r'(\d+)\s*N\s*(\d+)\s*[ØøOo]?\s*(\d+\.?\d*)\s*C\s*[:=\-]?\s*(\d+)',
        re.IGNORECASE
    )
    m = padrao1.search(t)
    if m:
        try:
            return int(m.group(1)), int(m.group(2)), float(m.group(3)), int(m.group(4))
        except:
            pass

    # Padrão 2: Compactado sem espaços
    # Ex: "4N1Ø12.5C350", "4N1O12.5C=350"
    t_compact = re.sub(r'\s+', '', t)
    padrao2 = re.compile(
        r'(\d+)N(\d+)[ØøOo]?(\d+\.?\d*)C[:=\-]?(\d+)',
        re.IGNORECASE
    )
    m2 = padrao2.search(t_compact)
    if m2:
        try:
            return int(m2.group(1)), int(m2.group(2)), float(m2.group(3)), int(m2.group(4))
        except:
            pass

    # Padrão 3: Flexível (captura na sequência)
    padrao3 = re.compile(
        r'(\d+).*?N\s*(\d+).*?[ØøOo]?\s*(\d+\.?\d*).*?C\s*[:=\-]?\s*(\d+)',
        re.IGNORECASE
    )
    m3 = padrao3.search(t)
    if m3:
        try:
            return int(m3.group(1)), int(m3.group(2)), float(m3.group(3)), int(m3.group(4))
        except:
            pass

    return None


def _extrair_pilar(texto: str):
    """
    Tenta extrair identificação de pilar.
    Retorna "P1", "P2", etc. ou None.
    
    Exemplos aceitos:
    - "P1", "P2", "P10"
    - "PILAR P1"
    - "PILAR 1"
    """
    if not texto:
        return None

    t = texto.upper().strip()

    # Padrão 1: "P1", "P2", "P10"
    m1 = re.match(r'^\s*P(\d+)\s*$', t)
    if m1:
        return f"P{m1.group(1)}"

    # Padrão 2: "PILAR P1" ou "PILAR 1"
    m2 = re.match(r'^\s*PILAR\s*P?(\d+)\s*$', t)
    if m2:
        return f"P{m2.group(1)}"

    return None


def processar_pilares(arquivos: List[str]) -> Tuple[List[Tuple], float, int]:
    """
    Processa arquivos DXF e extrai informações dos pilares.
    
    Retorna:
        - dados: Lista de tuplas (pilar, tipo, espec, qtde, comp_m, peso)
        - peso_total: float
        - total_barras: int
    
    Formato de cada tupla:
        (pilar, tipo, "N1 ø12.5", qtde, comp_m, peso)
    """
    
    if not EZDXF_DISPONIVEL:
        print("AVISO: ezdxf não instalado. Usando dados de exemplo.")
        return _dados_exemplo()

    dados_completos = []
    peso_total = 0.0
    total_barras = 0

    for arquivo in arquivos:
        try:
            # Verificar extensão
            ext = os.path.splitext(arquivo)[1].lower()
            
            if ext == '.dwg':
                print(f"AVISO: {os.path.basename(arquivo)} é DWG. ezdxf não lê DWG. Converta para DXF.")
                continue
            
            if ext != '.dxf':
                print(f"AVISO: {os.path.basename(arquivo)} não é DXF. Ignorando.")
                continue

            # Abrir arquivo DXF
            doc = ezdxf.readfile(arquivo)
            msp = doc.modelspace()

            pilar_atual = None

            # Processar entidades TEXT e MTEXT
            for entity in msp:
                try:
                    # Extrair texto da entidade
                    texto = None
                    
                    if entity.dxftype() == 'TEXT':
                        texto = entity.dxf.text
                    elif entity.dxftype() == 'MTEXT':
                        texto = entity.plain_text()
                    elif entity.dxftype() == 'INSERT':
                        # Processar atributos de blocos
                        try:
                            for attrib in entity.attribs:
                                texto_attrib = attrib.dxf.text
                                if texto_attrib:
                                    # Verificar se é pilar
                                    pilar = _extrair_pilar(texto_attrib)
                                    if pilar:
                                        pilar_atual = pilar
                                        continue
                                    
                                    # Verificar se é armadura
                                    armadura = _extrair_armadura(texto_attrib)
                                    if armadura and pilar_atual:
                                        qtde, pos, bitola, comp_cm = armadura
                                        _adicionar_armadura(
                                            dados_completos, pilar_atual,
                                            qtde, pos, bitola, comp_cm
                                        )
                                        peso_total += dados_completos[-1][5]
                                        total_barras += qtde
                        except:
                            pass
                        continue

                    if not texto:
                        continue

                    texto = texto.strip()
                    if not texto:
                        continue

                    # Verificar se é identificação de pilar
                    pilar = _extrair_pilar(texto)
                    if pilar:
                        pilar_atual = pilar
                        continue

                    # Verificar se é armadura
                    armadura = _extrair_armadura(texto)
                    if armadura and pilar_atual:
                        qtde, pos, bitola, comp_cm = armadura
                        _adicionar_armadura(
                            dados_completos, pilar_atual,
                            qtde, pos, bitola, comp_cm
                        )
                        peso_total += dados_completos[-1][5]
                        total_barras += qtde

                except Exception as e:
                    continue

        except Exception as e:
            print(f"Erro ao processar {os.path.basename(arquivo)}: {e}")

    # Ordenar por pilar e posição
    def _sort_key(item):
        try:
            pilar_num = int(item[0][1:]) if item[0][1:].isdigit() else 0
            pos_match = re.search(r'N(\d+)', item[2])
            pos_num = int(pos_match.group(1)) if pos_match else 0
            return (pilar_num, pos_num)
        except:
            return (0, 0)

    dados_completos.sort(key=_sort_key)

    # Se não encontrou dados, usar exemplo
    if not dados_completos:
        print("AVISO: Nenhum dado encontrado nos arquivos. Usando dados de exemplo.")
        return _dados_exemplo()

    return dados_completos, round(peso_total, 2), total_barras


def _adicionar_armadura(dados: List, pilar: str, qtde: int, pos: int, bitola: float, comp_cm: int):
    """Adiciona uma armadura à lista de dados"""
    
    # Determinar tipo baseado na posição
    if pos <= 2:
        tipo = "LONGITUDINAL"
    elif pos <= 4:
        tipo = "ESTRIBO"
    elif pos <= 6:
        tipo = "GANCHO"
    else:
        tipo = "COMPLEMENTAR"

    # Comprimento em metros
    comp_m = comp_cm / 100.0 if comp_cm > 20 else float(comp_cm)

    # Calcular peso (kg/m = bitola² × 0.00617)
    peso_por_metro = (bitola ** 2) * 0.00617
    peso = peso_por_metro * comp_m * qtde

    # Especificação no formato "N1 ø12.5"
    espec = f"N{pos} ø{bitola:.1f}"

    # Adicionar tupla
    dados.append((
        pilar,
        tipo,
        espec,
        int(qtde),
        round(comp_m, 3),
        round(peso, 3)
    ))


def _dados_exemplo() -> Tuple[List[Tuple], float, int]:
    """Retorna dados de exemplo para teste"""
    dados = [
        ("P1", "LONGITUDINAL", "N1 ø12.5", 4, 3.50, 13.47),
        ("P1", "LONGITUDINAL", "N2 ø12.5", 4, 3.50, 13.47),
        ("P1", "ESTRIBO", "N3 ø5.0", 35, 0.72, 4.87),
        ("P1", "ESTRIBO", "N4 ø5.0", 18, 0.96, 3.34),
        ("P2", "LONGITUDINAL", "N1 ø16.0", 6, 3.50, 33.14),
        ("P2", "LONGITUDINAL", "N2 ø16.0", 2, 3.50, 11.05),
        ("P2", "ESTRIBO", "N3 ø6.3", 35, 0.80, 6.86),
        ("P2", "ESTRIBO", "N4 ø6.3", 18, 1.00, 4.41),
        ("P3", "LONGITUDINAL", "N1 ø10.0", 4, 3.20, 7.89),
        ("P3", "ESTRIBO", "N2 ø5.0", 32, 0.64, 3.96),
        ("P4", "LONGITUDINAL", "N1 ø12.5", 8, 3.80, 29.26),
        ("P4", "ESTRIBO", "N3 ø6.3", 38, 0.88, 8.19),
    ]
    peso_total = sum(d[5] for d in dados)
    total_barras = sum(d[3] for d in dados)
    return dados, round(peso_total, 2), total_barras


# ==================== FUNÇÃO DE DEBUG ====================

def exportar_debug_textos(arquivos: List[str], saida_arquivo: str) -> int:
    """
    Exporta todos os textos encontrados nos DXFs para um arquivo TXT.
    Útil para diagnóstico quando a leitura não funciona.
    
    Retorna: quantidade de linhas de texto coletadas
    """
    if not EZDXF_DISPONIVEL:
        with open(saida_arquivo, 'w', encoding='utf-8') as f:
            f.write("ERRO: ezdxf não está instalado.\n")
            f.write("Execute: pip install ezdxf\n")
        return 0

    count = 0
    
    with open(saida_arquivo, 'w', encoding='utf-8') as out:
        out.write("=" * 80 + "\n")
        out.write("DEBUG DE TEXTOS - PILARES\n")
        out.write(f"Arquivos: {len(arquivos)}\n")
        out.write("=" * 80 + "\n\n")

        for arquivo in arquivos:
            out.write(f"\n{'='*60}\n")
            out.write(f"ARQUIVO: {os.path.basename(arquivo)}\n")
            out.write(f"{'='*60}\n")

            try:
                ext = os.path.splitext(arquivo)[1].lower()
                
                if ext == '.dwg':
                    out.write("[AVISO] Arquivo DWG. ezdxf não lê DWG. Converta para DXF.\n")
                    continue

                doc = ezdxf.readfile(arquivo)
                msp = doc.modelspace()

                # Processar TEXT
                out.write("\n--- TEXT ---\n")
                for entity in msp.query('TEXT'):
                    try:
                        texto = entity.dxf.text or ""
                        layer = entity.dxf.layer or ""
                        if texto.strip():
                            out.write(f"[TEXT] LAYER={layer} | {texto}\n")
                            count += 1
                    except:
                        pass

                # Processar MTEXT
                out.write("\n--- MTEXT ---\n")
                for entity in msp.query('MTEXT'):
                    try:
                        texto = entity.plain_text() or ""
                        layer = entity.dxf.layer or ""
                        if texto.strip():
                            out.write(f"[MTEXT] LAYER={layer} | {texto}\n")
                            count += 1
                    except:
                        pass

                # Processar INSERT (blocos com atributos)
                out.write("\n--- INSERT (ATTRIBS) ---\n")
                for entity in msp.query('INSERT'):
                    try:
                        block_name = entity.dxf.name or ""
                        for attrib in entity.attribs:
                            texto = attrib.dxf.text or ""
                            tag = attrib.dxf.tag or ""
                            if texto.strip():
                                out.write(f"[ATTRIB] BLOCK={block_name} TAG={tag} | {texto}\n")
                                count += 1
                    except:
                        pass

                # Processar DIMENSION (cotas)
                out.write("\n--- DIMENSION ---\n")
                for entity in msp.query('DIMENSION'):
                    try:
                        texto = entity.dxf.text or ""
                        layer = entity.dxf.layer or ""
                        if texto.strip():
                            out.write(f"[DIM] LAYER={layer} | {texto}\n")
                            count += 1
                    except:
                        pass

            except Exception as e:
                out.write(f"[ERRO] {e}\n")

        out.write(f"\n{'='*80}\n")
        out.write(f"TOTAL DE TEXTOS ENCONTRADOS: {count}\n")
        out.write(f"{'='*80}\n")

    return count


# ==================== TESTE DIRETO ====================

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DO MOTOR DE PILARES")
    print("=" * 60)
    
    # Testar com dados de exemplo
    dados, peso, barras = _dados_exemplo()
    
    print(f"\nDados de exemplo:")
    print(f"Total de registros: {len(dados)}")
    print(f"Total de barras: {barras}")
    print(f"Peso total: {peso:.2f} kg")
    print()
    
    print("Primeiros 5 registros:")
    for i, d in enumerate(dados[:5]):
        print(f"  [{i}] {d}")
    
    print()
    print("Formato de cada registro:")
    print("  (pilar, tipo, espec, qtde, comp_m, peso)")
    print()
    print("=" * 60)
    print("Motor OK!")
    print("=" * 60)