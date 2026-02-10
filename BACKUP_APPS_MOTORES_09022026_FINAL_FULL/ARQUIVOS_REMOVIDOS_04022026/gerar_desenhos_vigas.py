#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gerar_desenhos_vigas.py
-----------------------
Sistema interativo para capturar desenhos de cada viga do DXF
e salvá-los como PNGs individuais para uso nas etiquetas
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
import ezdxf
import json

class GeradorDesenhosVigas:
    def __init__(self, caminho_dxf, lista_vigas):
        self.caminho_dxf = caminho_dxf
        self.lista_vigas = lista_vigas
        self.mapeamento = {}  # {viga: {N1: {x, y, w, h}, N2: {...}, N3: {...}}}
        self.arquivo_mapeamento = "mapeamento_desenhos.json"
        self.detalhes_por_viga = {viga: ['N1', 'N2', 'N3'] for viga in lista_vigas}
        
        # Carregar mapeamento existente
        self.carregar_mapeamento()
        
        # Renderizar DXF completo
        print("Renderizando DXF completo...")
        self.renderizar_dxf_completo()
        
        # Criar interface
        self.criar_interface()
    
    def renderizar_dxf_completo(self):
        """Renderiza o DXF completo em alta resolução"""
        try:
            doc = ezdxf.readfile(self.caminho_dxf)
            msp = doc.modelspace()
            
            # Calcular bbox
            min_x = min_y = float('inf')
            max_x = max_y = float('-inf')
            
            for entity in msp:
                try:
                    if entity.dxftype() == 'LINE':
                        min_x = min(min_x, entity.dxf.start.x, entity.dxf.end.x)
                        max_x = max(max_x, entity.dxf.start.x, entity.dxf.end.x)
                        min_y = min(min_y, entity.dxf.start.y, entity.dxf.end.y)
                        max_y = max(max_y, entity.dxf.start.y, entity.dxf.end.y)
                except:
                    pass
            
            self.bbox = (min_x, min_y, max_x, max_y)
            
            # Criar imagem em alta resolução
            largura_mm = max_x - min_x
            altura_mm = max_y - min_y
            
            # 2 pixels por mm = boa resolução
            self.escala = 2
            self.img_width = int(largura_mm * self.escala)
            self.img_height = int(altura_mm * self.escala)
            
            # Limitar tamanho máximo
            max_size = 4000
            if self.img_width > max_size or self.img_height > max_size:
                ratio = min(max_size / self.img_width, max_size / self.img_height)
                self.img_width = int(self.img_width * ratio)
                self.img_height = int(self.img_height * ratio)
                self.escala *= ratio
            
            print(f"Imagem: {self.img_width}x{self.img_height}px")
            
            # Renderizar
            img = Image.new('RGB', (self.img_width, self.img_height), 'white')
            draw = ImageDraw.Draw(img)
            
            def transformar(x, y):
                px = int((x - min_x) * self.escala)
                py = int(self.img_height - ((y - min_y) * self.escala))
                return (px, py)
            
            # Desenhar entidades
            count = 0
            for entity in msp:
                try:
                    if entity.dxftype() == 'LINE':
                        p1 = transformar(entity.dxf.start.x, entity.dxf.start.y)
                        p2 = transformar(entity.dxf.end.x, entity.dxf.end.y)
                        draw.line([p1, p2], fill='black', width=1)
                        count += 1
                    
                    elif entity.dxftype() == 'CIRCLE':
                        cx, cy = transformar(entity.dxf.center.x, entity.dxf.center.y)
                        r = int(entity.dxf.radius * self.escala)
                        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline='black', width=1)
                        count += 1
                    
                    elif entity.dxftype() in ('LWPOLYLINE', 'POLYLINE'):
                        points = [transformar(p[0], p[1]) for p in entity.get_points()]
                        if len(points) > 1:
                            draw.line(points, fill='black', width=1)
                            count += 1
                except:
                    pass
            
            print(f"Renderizadas {count} entidades")
            
            self.img_completa = img
            
        except Exception as e:
            print(f"Erro ao renderizar DXF: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def criar_interface(self):
        """Cria interface Tkinter para seleção de regiões"""
        self.root = tk.Tk()
        self.root.title("Gerador de Desenhos de Vigas")
        self.root.geometry("1200x800")
        
        # Frame esquerdo - lista de vigas
        frame_esq = ttk.Frame(self.root, width=250)
        frame_esq.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(frame_esq, text="Vigas:", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Listbox com vigas
        self.listbox = tk.Listbox(frame_esq, height=30)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        
        for viga in self.lista_vigas:
            status = "✅" if viga in self.mapeamento and len(self.mapeamento[viga]) == 3 else "❌"
            self.listbox.insert(tk.END, f"{status} {viga}")
        
        self.listbox.bind('<<ListboxSelect>>', self.on_viga_select)
        
        # Frame para seleção de detalhe
        frame_detalhe = ttk.LabelFrame(frame_esq, text="Detalhe")
        frame_detalhe.pack(pady=5, fill=tk.X, padx=5)
        
        self.var_detalhe = tk.StringVar(value="N1")
        for detalhe in ['N1', 'N2', 'N3']:
            tk.Radiobutton(frame_detalhe, text=detalhe, variable=self.var_detalhe, 
                          value=detalhe, command=self.mudar_detalhe).pack(side=tk.LEFT, padx=5)
        
        # Botões
        ttk.Button(frame_esq, text="📌 Capturar Região", command=self.capturar_regiao).pack(pady=5, fill=tk.X)
        ttk.Button(frame_esq, text="💾 Salvar Mapeamento", command=self.salvar_mapeamento).pack(pady=5, fill=tk.X)
        ttk.Button(frame_esq, text="🖼️ Gerar Todos os PNGs", command=self.gerar_todos_pngs).pack(pady=5, fill=tk.X)
        
        self.label_status = ttk.Label(frame_esq, text="Selecione uma viga", foreground="blue")
        self.label_status.pack(pady=10)

        
        # Frame direito - canvas com imagem
        frame_dir = ttk.Frame(self.root)
        frame_dir.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas com scrollbars
        self.canvas = tk.Canvas(frame_dir, bg='white')
        
        scrollbar_y = ttk.Scrollbar(frame_dir, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_x = ttk.Scrollbar(frame_dir, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Adicionar imagem ao canvas
        self.photo = ImageTk.PhotoImage(self.img_completa)
        self.canvas_img = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))
        
        # Retângulo de seleção
        self.rect = None
        self.start_x = None
        self.start_y = None
        
        # Bindings para seleção de região
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.viga_selecionada = None
        self.detalhe_selecionado = 'N1'
        
        self.root.mainloop()
    
    def mudar_detalhe(self):
        """Callback quando muda o detalhe selecionado"""
        self.detalhe_selecionado = self.var_detalhe.get()
        if self.viga_selecionada:
            self.mostrar_regiao_selecionada()
            self.label_status.config(
                text=f"Viga: {self.viga_selecionada} | Detalhe: {self.detalhe_selecionado}",
                foreground="blue"
            )

    
    def on_viga_select(self, event):
        """Callback quando seleciona uma viga"""
        selection = self.listbox.curselection()
        if selection:
            idx = selection[0]
            self.viga_selecionada = self.lista_vigas[idx]
            self.detalhe_selecionado = 'N1'  # Padrão: N1
            self.label_status.config(text=f"Viga: {self.viga_selecionada} | Detalhe: {self.detalhe_selecionado}")
            self.mostrar_regiao_selecionada()
    
    def mostrar_regiao_selecionada(self):
        """Mostra o retângulo da região já capturada (se houver)"""
        if self.viga_selecionada and self.viga_selecionada in self.mapeamento:
            viga_map = self.mapeamento[self.viga_selecionada]
            if self.detalhe_selecionado in viga_map:
                m = viga_map[self.detalhe_selecionado]
                if self.rect:
                    self.canvas.delete(self.rect)
                self.rect = self.canvas.create_rectangle(
                    m['x'], m['y'], m['x'] + m['w'], m['y'] + m['h'],
                    outline='red', width=2
                )
    
    def on_press(self, event):
        """Início da seleção"""
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        if self.rect:
            self.canvas.delete(self.rect)
        
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )
    
    def on_drag(self, event):
        """Durante o arrasto"""
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
    
    def on_release(self, event):
        """Fim da seleção"""
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        
        x1 = int(min(self.start_x, end_x))
        y1 = int(min(self.start_y, end_y))
        x2 = int(max(self.start_x, end_x))
        y2 = int(max(self.start_y, end_y))
        
        self.regiao_selecionada = (x1, y1, x2 - x1, y2 - y1)
    
    def capturar_regiao(self):
        """Captura a região selecionada para o detalhe atual"""
        if not self.viga_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma viga primeiro")
            return
        
        if not hasattr(self, 'regiao_selecionada'):
            messagebox.showwarning("Aviso", "Desenhe um retângulo na imagem primeiro")
            return
        
        x, y, w, h = self.regiao_selecionada
        
        # Inicializar viga no mapeamento
        if self.viga_selecionada not in self.mapeamento:
            self.mapeamento[self.viga_selecionada] = {}
        
        # Salvar detalhe
        self.mapeamento[self.viga_selecionada][self.detalhe_selecionado] = {
            'x': x, 'y': y, 'w': w, 'h': h
        }
        
        # Contar quantos detalhes foram capturados
        detalhes_capturados = len(self.mapeamento[self.viga_selecionada])
        
        self.label_status.config(
            text=f"✅ {self.viga_selecionada} - {self.detalhe_selecionado} capturado ({detalhes_capturados}/3)",
            foreground="green"
        )
        
        # Passar para próximo detalhe
        detalhes = ['N1', 'N2', 'N3']
        idx = detalhes.index(self.detalhe_selecionado)
        if idx + 1 < len(detalhes):
            self.detalhe_selecionado = detalhes[idx + 1]
            if self.rect:
                self.canvas.delete(self.rect)
                self.rect = None
            self.regiao_selecionada = None
            self.label_status.config(
                text=f"Viga: {self.viga_selecionada} | Detalhe: {self.detalhe_selecionado}",
                foreground="blue"
            )
        else:
            # Todos os 3 detalhes foram capturados
            idx = self.lista_vigas.index(self.viga_selecionada)
            self.listbox.delete(idx)
            self.listbox.insert(idx, f"✅ {self.viga_selecionada}")

    
    def salvar_mapeamento(self):
        """Salva mapeamento em JSON"""
        try:
            with open(self.arquivo_mapeamento, 'w', encoding='utf-8') as f:
                json.dump(self.mapeamento, f, indent=2)
            
            messagebox.showinfo("Sucesso", f"Mapeamento salvo em {self.arquivo_mapeamento}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def carregar_mapeamento(self):
        """Carrega mapeamento existente"""
        if os.path.exists(self.arquivo_mapeamento):
            try:
                with open(self.arquivo_mapeamento, 'r', encoding='utf-8') as f:
                    self.mapeamento = json.load(f)
                print(f"Carregado mapeamento com {len(self.mapeamento)} vigas")
            except Exception as e:
                print(f"Erro ao carregar mapeamento: {e}")
    
    def gerar_todos_pngs(self):
        """Gera PNGs para todos os detalhes de todas as vigas mapeadas"""
        if not self.mapeamento:
            messagebox.showwarning("Aviso", "Nenhuma viga mapeada ainda")
            return
        
        pasta_saida = "export/desenhos_vigas"
        os.makedirs(pasta_saida, exist_ok=True)
        
        gerados = 0
        for viga, detalhes in self.mapeamento.items():
            for detalhe, coords in detalhes.items():
                try:
                    # Crop da imagem
                    crop = self.img_completa.crop((
                        coords['x'], coords['y'],
                        coords['x'] + coords['w'], coords['y'] + coords['h']
                    ))
                    
                    # Salvar como {viga}_{detalhe}.png
                    arquivo = os.path.join(pasta_saida, f"{viga}_{detalhe}.png")
                    crop.save(arquivo)
                    gerados += 1
                    print(f"✅ {arquivo}")
                    
                except Exception as e:
                    print(f"❌ Erro ao gerar PNG de {viga}_{detalhe}: {e}")
        
        messagebox.showinfo("Sucesso", f"Gerados {gerados} PNGs em {pasta_saida}")



if __name__ == "__main__":
    # Configurar
    caminho_dxf = r"dxf\vig terreo f 1-R2 - Copia.DXF"
    lista_vigas = ['V8', 'V9', 'V10', 'VM1', 'VM2']  # Adicionar todas as vigas do projeto
    
    print("="*60)
    print("GERADOR DE DESENHOS DE VIGAS")
    print("="*60)
    print()
    print("INSTRUÇÕES:")
    print("1. Selecione uma viga na lista esquerda")
    print("2. Arraste um retângulo na imagem para marcar o desenho")
    print("3. Clique em 'Capturar Região'")
    print("4. Repita para todas as vigas")
    print("5. Clique em 'Gerar Todos os PNGs'")
    print()
    
    app = GeradorDesenhosVigas(caminho_dxf, lista_vigas)
