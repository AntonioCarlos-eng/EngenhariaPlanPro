import os
from pathlib import Path
from PIL import Image, ImageWin, ImageTk
import win32ui
import win32print
import win32con
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import mm
import tkinter as tk
from tkinter import messagebox

DPI_PADRAO = 300
LARGURA_ETIQUETA_MM = 100
ALTURA_ETIQUETA_MM = 150

def mm_to_px(mm, dpi=DPI_PADRAO):
    return int(round((mm / 25.4) * dpi))

class EtiquetaImpressao:
    def __init__(self, pasta_etiquetas, dados_etiquetas):
        self.pasta_etiquetas = Path(pasta_etiquetas)
        self.dados = dados_etiquetas
        self.largura_px = mm_to_px(LARGURA_ETIQUETA_MM)
        self.altura_px = mm_to_px(ALTURA_ETIQUETA_MM)
    def obter_caminhos_png_validos(self):
        pngs = sorted(self.pasta_etiquetas.glob("*.png"))
        pngs_validos = []
        for d in self.dados:
            v = d.get('viga') if isinstance(d, dict) else d[0]
            pos = d.get('pos') if isinstance(d, dict) else d[1]
            esperado = f"ETIQUETA_{v}_{pos}.png"
            caminho_esperado = self.pasta_etiquetas / esperado
            if caminho_esperado.exists():
                pngs_validos.append(caminho_esperado)
            else:
                if pngs:
                    pngs_validos.append(pngs.pop(0))
                else:
                    messagebox.showwarning("Aviso", f"PNG faltando para etiqueta {v} {pos}")
        return pngs_validos
    def gerar_pdf_com_pngs(self, arquivo_pdf_saida):
        c = pdf_canvas.Canvas(arquivo_pdf_saida, pagesize=(LARGURA_ETIQUETA_MM * mm, ALTURA_ETIQUETA_MM * mm))
        c.setTitle("Etiquetas Geradas com Imagens PNG")
        pngs = self.obter_caminhos_png_validos()
        if not pngs:
            raise FileNotFoundError("Nenhuma imagem PNG válida encontrada.")
        for idx, caminho_png in enumerate(pngs):
            c.drawImage(str(caminho_png), 0, 0, width=LARGURA_ETIQUETA_MM * mm, height=ALTURA_ETIQUETA_MM * mm)
            c.showPage()
        c.save()
        print(f"PDF gerado em: {arquivo_pdf_saida}")
        return arquivo_pdf_saida
    def imprimir_pngs_gdi(self, impressora):
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(impressora)
        hDC.SetMapMode(win32con.MM_TEXT)
        hDC.StartDoc("Impressão de Etiquetas PNG")
        pngs = self.obter_caminhos_png_validos()
        if not pngs:
            raise FileNotFoundError("Nenhuma imagem PNG válida para imprimir.")
        for idx, caminho_png in enumerate(pngs):
            img = Image.open(caminho_png).convert("RGB")
            img = img.resize((self.largura_px, self.altura_px), Image.Resampling.LANCZOS)
            dib = ImageWin.Dib(img)
            hDC.StartPage()
            dib.draw(hDC.GetHandleOutput(), (0, 0, self.largura_px, self.altura_px))
            hDC.EndPage()
            print(f"Etiqueta {idx+1} enviada para impressora.")
        hDC.EndDoc()
        hDC.DeleteDC()
        print("Impressão concluída com sucesso.")
    def preview_etiquetas_tkinter(self):
        root = tk.Tk()
        root.title("Preview Etiquetas PNG")
        canvas = tk.Canvas(root, width=self.largura_px + 40, height=600, scrollregion=(0,0,self.largura_px + 40, len(self.dados)*(self.altura_px + 20)))
        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        imagens_refs = []
        pngs = self.obter_caminhos_png_validos()
        y_pos = 10
        for caminho in pngs:
            img = Image.open(caminho).convert("RGBA")
            img_redim = img.resize((self.largura_px, self.altura_px), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img_redim)
            imagens_refs.append(img_tk)
            canvas.create_image(20, y_pos, image=img_tk, anchor="nw")
            y_pos += self.altura_px + 20
        root.mainloop()

if __name__ == "__main__":
    pasta = r"c:\EngenhariaPlanPro\etiquetas"
    dados = [
        {'viga': 'V1', 'pos': 'N1'},
        {'viga': 'V2', 'pos': 'N2'},
    ]
    impressora = win32print.GetDefaultPrinter()
    etiqueta_imp = EtiquetaImpressao(pasta, dados)
    pdf_path = os.path.join(pasta, "etiquetas_compiladas.pdf")
    etiqueta_imp.gerar_pdf_com_pngs(pdf_path)
    etiqueta_imp.preview_etiquetas_tkinter()
    etiqueta_imp.imprimir_pngs_gdi(impressora)
