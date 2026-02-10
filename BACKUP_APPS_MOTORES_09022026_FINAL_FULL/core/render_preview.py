#!/usr/bin/env python3
# core/render_preview.py
# Render DXF -> PNG (tentativa automática). Aceita --out ou --saida (alias em PT).
#
# Uso:
# 1) a partir da pasta do projeto (onde está o DXF):
#    python core\render_preview.py "nome do arquivo.dxf" --out preview.png
# ou (alias pt)
#    python core\render_preview.py "nome do arquivo.dxf" --saida preview.png
#
import os
import sys
import argparse

try:
    import ezdxf
except Exception:
    print("ezdxf não instalado. Instale com: pip install ezdxf")
    sys.exit(1)

def try_render(dxf_path, out_png):
    try:
        # tentativa usando ezdxf.addons.drawing (matplotlib)
        from ezdxf.addons.drawing import matplotlib as ezdxf_matplotlib
        # qsave faz render direto para arquivo
        ezdxf_matplotlib.qsave(dxf_path, out_png, dpi=150)
        print("Render salvo em:", out_png)
        return True
    except Exception as e:
        print("Render com ezdxf+matplotlib falhou (ambiente). Erro:", e)
        return False

def main():
    parser = argparse.ArgumentParser(description="Render DXF para PNG (preview)")
    parser.add_argument("dxf", help="arquivo DXF (caminho ou nome)")
    parser.add_argument("--out", help="arquivo PNG de saída", default=None)
    parser.add_argument("--saida", help="alias em português para --out", default=None)
    args = parser.parse_args()

    dxf_path = args.dxf
    # se recebeu --saida, usar como out
    out = args.out or args.saida or (os.path.splitext(os.path.basename(dxf_path))[0] + ".png")

    # normalize paths
    dxf_path = os.path.expanduser(dxf_path)
    out = os.path.expanduser(out)

    print("CWD:", os.getcwd())
    print("Tentando DXF:", dxf_path)
    if not os.path.exists(dxf_path):
        print("Arquivo não encontrado:", dxf_path)
        print("Liste o diretório atual com: dir (Windows) ou ls (Linux/Mac) e verifique o nome exato.")
        sys.exit(1)

    ok = try_render(dxf_path, out)
    if not ok:
        print("\n--- Instrucoes alternativas (manual) ---")
        print("Se o render automatico falhar, abra o DXF no seu CAD e exporte PNG (Export/Plot -> PNG).")
        print("Salve em alta resolucao (>=150 DPI) e coloque o arquivo PNG na mesma pasta do DXF.")
    else:
        print("Render OK:", out)

if __name__ == "__main__":
    main()