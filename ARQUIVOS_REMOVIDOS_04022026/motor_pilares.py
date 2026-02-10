import ezdxf
import re

def processar_pilares(arquivos):
    dados = []
    total_peso = 0.0
    total_barras = 0

    for arquivo in arquivos:
        doc = ezdxf.readfile(arquivo)
        msp = doc.modelspace()

        pilares = {}
        pilar_atual = None
        ultima_posicao = None

        for e in msp:

            if e.dxftype() == "TEXT":
                texto = e.dxf.text.strip().upper()

                m = re.match(r"^P(\d+)$", texto)
                if m:
                    pilar_atual = f"P{m.group(1)}"
                    pilares.setdefault(pilar_atual, [])
                    continue

                m = re.match(r"^([A-Z]+)(\d+)$", texto)
                if pilar_atual and m:
                    ultima_posicao = m.group(0)
                    pilares[pilar_atual].append({
                        "pos": ultima_posicao,
                        "comp": 0
                    })
                    continue

            if e.dxftype() in ["LWPOLYLINE", "POLYLINE"]:
                if pilar_atual and ultima_posicao and pilares[pilar_atual]:
                    try:
                        comp = e.length() / 1000
                        pilares[pilar_atual][-1]["comp"] = round(comp, 2)
                    except:
                        pass

        for pilar, itens in pilares.items():
            for item in itens:
                pos = item["pos"]
                comp = float(item["comp"])

                bitola = 8.0
                if "12" in pos: bitola = 12.5
                if "10" in pos: bitola = 10.0

                qtde = 1
                peso = round(qtde * comp * (bitola / 10), 2)

                total_barras += qtde
                total_peso += peso

                dados.append([
                    pilar, pos, bitola, qtde, comp, peso
                ])

    return dados, total_peso, total_barras
