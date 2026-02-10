import os
import sys
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.vigas_motor_v2 import processar_vigas

def main():
    # Arquivo de teste
    arquivo = "dxf/vig terreo f 1-R2 - Copia.DXF"

    if not os.path.exists(arquivo):
        print(f"Arquivo não encontrado: {arquivo}")
        return

    print(f"Analisando arquivo: {arquivo}")
    print("=" * 80)

    try:
        import ezdxf
        doc = ezdxf.readfile(arquivo)
        msp = doc.modelspace()

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

        print(f"Arquivo DXF carregado com sucesso")
        print(f"Total de textos encontrados: {len(raw)}")
        print()

        # Detectar títulos como no motor
        RE_VIGA_STRICT = re.compile(r'^(V[NTPB]?\d[\w\-]*)$', re.IGNORECASE)
        RE_VIGA_LOOSE = re.compile(r'\bV[A-Z]?\d[\w\-]*\b', re.IGNORECASE)
        RE_VIGA_FALLBACK = re.compile(r'(?:^|\s)(VIGA|V|VM|VC|VB|VP|VT)\s*-?\s*([A-Z]?\d[\w\-]*)', re.IGNORECASE)

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
                if nome not in titles_dict:
                    titles_dict[nome] = {"nome": nome, "x": t["x"], "y": t["y"], "count": 1}
                else:
                    titles_dict[nome]["count"] += 1

        titles = list(titles_dict.values())
        print(f"Títulos de viga detectados: {len(titles)}")
        for t in sorted(titles, key=lambda x: x["nome"]):
            print(f"  {t['nome']} @ ({t['x']:.2f}, {t['y']:.2f}) - {t['count']} ocorrências")
        print()

        print("Textos extraídos (primeiros 30):")
        for i, t in enumerate(raw[:30], 1):
            print(f" {i:2d}: '{t['text']}' @ ({t['x']:.2f}, {t['y']:.2f})")
        if len(raw) > 30:
            print(f"... e mais {len(raw) - 30} textos")
        print()

    except Exception as e:
        print(f"Erro carregando DXF: {e}")
        return

    print("=" * 80)
    print("Processando com vigas_motor_v2...")

    dados, total_kg, total_barras = processar_vigas([arquivo])

    print(f"Resultado: {len(dados)} entradas, {total_barras} barras, {total_kg:.2f} kg")
    print()

    if dados:
        print("Todas as entradas processadas (ordenadas por viga):")
        viga_atual = None
        for d in sorted(dados, key=lambda x: (x[0], x[1], x[2])):
            if d[0] != viga_atual:
                if viga_atual is not None:
                    print()
                viga_atual = d[0]
                print(f"  {d[0]}:")
            print(f"    {d[1]} Ø{d[2]:.1f} Q{d[3]} C{d[4]:.2f} P{d[5]:.3f}")
        print()

    # Verificar duplicatas
    from collections import Counter
    keys = [(d[0], d[1], d[2]) for d in dados]
    dupes = [k for k, v in Counter(keys).items() if v > 1]
    if dupes:
        print(f"Encontradas {len(dupes)} combinações duplicadas:")
        for dupe in dupes[:5]:
            print(f"  {dupe}")
        if len(dupes) > 5:
            print(f"  ... e mais {len(dupes) - 5}")
    else:
        print("Nenhuma duplicata encontrada nas combinações (viga, pos, bit)")

if __name__ == "__main__":
    main()
