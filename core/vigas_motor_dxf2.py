# core/vigas_motor_dxf2.py
# MOTOR NOVO – DXF 2.0
# Feito para projetos novos (VN3-25A tipos modernos)
# Não interfere no motor antigo

import re
from typing import List, Tuple
from core.reader import ler_dxf, ler_dwg
from core.peso import peso_linear_kg_m


# ---------------------------------------------------------
# PADRÕES DE VIGAS MODERNAS
# Aceita: V5, V10, VN3-25A, VM2, VT1, VB12, VP7 etc.
# ---------------------------------------------------------
REGEX_VIGA = re.compile(
    r'^(V|VN|VM|VP|VT|VB)\s*\d+[A-Z0-9\-]*$',
    re.IGNORECASE
)

# ---------------------------------------------------------
# PADRÕES DE BARRAS (NOVOS)
# Aceita TUDO isso:
#  • 2 N1 Ø10 C=510
#  • 2N1Ø10C=515
#  • 22 N3 Ø5 C=141
#  • 17 N1 Ø8.3 C/14  (IGNORAR ESTE!)
# ---------------------------------------------------------
REGEX_BARRAS = [
    r'(\d+)\s*N(\d+)\s*[Ø∅]?\s*([\d.,]+)\s*C\s*=\s*([\d.,]+)',
    r'(\d+)N(\d+)[Ø∅]?([\d.,]+)C=([\d.,]+)',
    r'(\d+)\s*N(\d+)\s*[Ø∅]?\s*([\d.,]+)\s*C\s*([\d.,]+)'
]

# ---------------------------------------------------------
# FRASES QUE DEVEM SER IGNORADAS (não são barras)
# ---------------------------------------------------------
IGNORAR = [
    "C/",           # Distribuição de estribo (ex: C/14)
    "ESPAÇAMENTO",
    "Ø=",
    "E=",           # Elevação
]


def deve_ignorar(texto: str) -> bool:
    """Retorna True se o texto não for barra válida."""
    t = texto.replace(" ", "").upper()
    for palavra in IGNORAR:
        if palavra.upper() in t:
            return True
    return False


# ---------------------------------------------------------
# MOTOR NOVO
# ---------------------------------------------------------
def processar_vigas(arquivos: List[str]) -> Tuple[List[Tuple], float, int]:

    dados = []
    total_barras = 0
    total_peso = 0.0

    print(f"[DXF 2.0] Processando {len(arquivos)} arquivo(s)")

    for caminho in arquivos:

        print(f"[DXF 2.0] Lendo: {caminho}")

        textos = ler_dxf(caminho) if caminho.lower().endswith(".dxf") else ler_dwg(caminho)

        print(f"[DXF 2.0] {len(textos)} textos extraídos")

        viga_atual = None

        for txt in textos:
            t = txt.strip().replace(" ", "")

            # ---------------------------------------------
            # 1) IDENTIFICAÇÃO DE VIGA
            # ---------------------------------------------
            if REGEX_VIGA.match(t):
                viga_atual = t.upper()
                print(f"[DXF 2.0] Viga detectada: {viga_atual}")
                continue

            if not viga_atual:
                continue

            # ---------------------------------------------
            # 2) IGNORAR TEXTOS QUE NÃO SÃO BARRAS
            # ---------------------------------------------
            if deve_ignorar(t):
                continue

            # ---------------------------------------------
            # 3) PROCURAR BARRAS (3 padrões diferentes)
            # ---------------------------------------------
            for regex in REGEX_BARRAS:
                m = re.search(regex, txt, re.IGNORECASE)
                if m:
                    qtd = int(m.group(1))
                    pos = f"N{m.group(2)}"
                    bitola = float(m.group(3).replace(",", "."))

                    comp_val = float(m.group(4).replace(",", "."))
                    comp_m = comp_val / 100 if comp_val > 20 else comp_val

                    peso = peso_linear_kg_m(bitola) * comp_m * qtd

                    dados.append((viga_atual, pos, bitola, qtd, round(comp_m, 3), round(peso, 3)))

                    total_barras += qtd
                    total_peso += peso

                    print(f"[DXF 2.0] Barra → {viga_atual} {pos} Ø{bitola} x{qtd} C={comp_m:.2f}m")
                    break

    # ---------------------------------------------------------
    # ORDENAÇÃO CORRETA
    # ---------------------------------------------------------
    try:
        dados.sort(key=lambda x: (x[0], int(x[1][1:])))
    except:
        dados.sort()

    print(f"[DXF 2.0] Total: {len(dados)} itens, {total_barras} barras, {total_peso:.2f} kg")

    return dados, round(total_peso, 2), total_barras
