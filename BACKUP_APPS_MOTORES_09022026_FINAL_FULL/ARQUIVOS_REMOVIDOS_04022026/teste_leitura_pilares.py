import ezdxf

def testar_leitura_dxf(arquivo):
    print("\n==============================")
    print(f"📌 LENDO DXF: {arquivo}")
    print("==============================\n")

    try:
        doc = ezdxf.readfile(arquivo)
        msp = doc.modelspace()

        print("✔ ENTIDADES TEXT ENCONTRADAS:")
        print("------------------------------")
        for e in msp.query("TEXT"):
            try:
                print(f"[TEXT] -> '{e.dxf.text}'")
            except:
                pass

        print("\n✔ ENTIDADES MTEXT ENCONTRADAS:")
        print("------------------------------")
        for e in msp.query("MTEXT"):
            try:
                print(f"[MTEXT] -> '{e.plain_text()}'")
            except:
                pass

        print("\n✔ ENTIDADES ATTRIB ENCONTRADAS:")
        print("------------------------------")
        for e in msp.query("ATTRIB"):
            try:
                print(f"[ATTRIB] -> '{e.dxf.text}'")
            except:
                pass

        print("\n==============================")
        print("LEITURA FINALIZADA")
        print("==============================\n")

    except Exception as e:
        print("❌ ERRO AO LER O ARQUIVO:")
        print(str(e))


if __name__ == "__main__":
    # COLE AQUI O CAMINHO DO DXF
    arquivo = r"C:\Users\orqui\OneDrive\Área de Trabalho\projetos\ENV P 1 COTACAO BLOCO ARRAQUE E PILARES - Copia.dxf"  # <-- altere para seu arquivo real
    testar_leitura_dxf(arquivo)
