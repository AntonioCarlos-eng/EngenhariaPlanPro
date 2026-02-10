# core/vigas_motor.py - Motor para processar VIGAS (ROBUSTO + RETROCOMPATÍVEL)
import re
from typing import List, Tuple


def processar_vigas(arquivos: List[str]) -> Tuple[List[Tuple], float, int]:
    """
    Processa arquivos DXF/DWG e extrai dados de VIGAS.
    Mantém compatibilidade TOTAL com seu motor antigo.
    """
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from core.reader import ler_dxf, ler_dwg
    from core.peso import peso_linear_kg_m

    dados = []

    print(f"\n[VIGAS MOTOR] Processando {len(arquivos)} arquivo(s)")

    # ==========================================================
    # REGEX ULTRA-ROBUSTA PARA BARRAS
    # Aceita:
    #   2 N1 Ø10 C510
    #   6 N1 Ø8.0 C=305
    #   22 N3 Ø5 C=141
    #   2x17 N3 Ø6.3 C=164
    # ==========================================================
    REGEX_BARRA = re.compile(
        r"""
        (?:(\d+)x)?         # quantidade multiplicada (opcional)   ex: 2x17
        (\d+)               # quantidade principal                 ex: 2
        \s*N(\d+)           # posição N1, N2, N3...
        \s*[Øø∅]?\s*
        (\d+(?:[.,]\d+)?)   # bitola
        \s*C\s*=?\s*
        (\d+(?:[.,]\d+)?)   # comprimento
        """,
        re.IGNORECASE | re.VERBOSE
    )

    # ==========================================================
    # PROCESSAMENTO DOS ARQUIVOS
    # ==========================================================
    for arquivo in arquivos:
        print(f"[VIGAS MOTOR] Lendo: {os.path.basename(arquivo)}")

        ext = arquivo.lower().split(".")[-1]
        if ext == "dxf":
            textos = ler_dxf(arquivo)
        elif ext == "dwg":
            textos = ler_dwg(arquivo)
        else:
            print(f"[VIGAS MOTOR] Extensão não suportada: {ext}")
            continue

        print(f"[VIGAS MOTOR] {len(textos)} textos encontrados")

        viga_atual = None

        # ==========================================================
        # PROCESSAR LINHA A LINHA
        # ==========================================================
        for texto in textos:
            t = texto.strip()
            t_nospace = t.replace(" ", "")

            # ------------------------------------------------------
            # DETECTOR ROBUSTO DE VIGA
            # Aceita:
            #   V10
            #   VN3-25A
            #   V5
            #   V14
            #   VM2
            # ------------------------------------------------------
            if re.match(r'^(V[NTPB]?\d[\w\-]*)$', t_nospace, re.IGNORECASE):
                viga_atual = t_nospace.upper()
                print(f"[VIGAS MOTOR] Viga atual = {viga_atual}")
                continue

            if not viga_atual:
                continue

            # ------------------------------------------------------
            # TENTAR BATER COM A REGEX PRINCIPAL
            # ------------------------------------------------------
            m = REGEX_BARRA.search(t)
            if m:
                mult = m.group(1)
                qtd = int(m.group(2))
                pos = f"N{m.group(3)}"
                bitola = float(m.group(4).replace(",", "."))
                comp_val = float(m.group(5).replace(",", "."))

                # aplicar multiplicador 2x17
                if mult:
                    qtd *= int(mult)

                # transformar comprimento
                comp_m = comp_val / 100 if comp_val > 20 else comp_val

                peso = peso_linear_kg_m(bitola) * comp_m * qtd

                dados.append(
                    (viga_atual, pos, bitola, qtd, round(comp_m, 2), round(peso, 3))
                )

                print(f"[VIGAS MOTOR] Barra: {viga_atual} {pos} Ø{bitola} x{qtd} C={comp_m:.2f}m")
                continue

    # ==========================================================
    # TOTAIS
    # ==========================================================
    total_kg = sum(d[5] for d in dados)
    total_barras = sum(d[3] for d in dados)

    # ==========================================================
    # ORDENADOR ORIGINAL (mantido sem alterar nada)
    # ==========================================================
    def extrair_ordem_viga(nome_viga: str):
        nome_upper = nome_viga.upper()

        if nome_upper.startswith('VN'):
            tipo = 1
            resto = nome_upper[2:]
        elif nome_upper.startswith('VT'):
            tipo = 2
            resto = nome_upper[2:]
        elif nome_upper.startswith('VP'):
            tipo = 3
            resto = nome_upper[2:]
        elif nome_upper.startswith('VB'):
            tipo = 4
            resto = nome_upper[2:]
        elif nome_upper.startswith('V'):
            tipo = 0
            resto = nome_upper[1:]
        else:
            tipo = 99
            resto = nome_upper

        match = re.match(r'(\d+)', resto)
        if match:
            numero_principal = int(match.group(1))
            sufixo = resto[len(match.group(1)):]
        else:
            numero_principal = 9999
            sufixo = resto

        numero_secundario = 9999
        letra_final = ''

        if '-' in sufixo:
            partes = sufixo.split('-', 1)
            m2 = re.match(r'(\d+)([A-Z]*)', partes[1])
            if m2:
                numero_secundario = int(m2.group(1))
                letra_final = m2.group(2)

        return (tipo, numero_principal, numero_secundario, letra_final)

    # ordenar
    dados.sort(key=lambda x: (extrair_ordem_viga(x[0]), int(x[1][1:])))

    print("[VIGAS MOTOR] Dados ordenados com sucesso")
    print(f"[VIGAS MOTOR] Total: {len(dados)} itens, {total_barras} barras, {total_kg:.2f} kg")

    return dados, round(total_kg, 2), total_barras
