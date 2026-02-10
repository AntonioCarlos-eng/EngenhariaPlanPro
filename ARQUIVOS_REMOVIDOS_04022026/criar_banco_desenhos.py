#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
criar_banco_desenhos.py
-----------------------
Ferramenta para criar banco de imagens de desenhos técnicos a partir de DXF limpo
"""
import os
import json
import ezdxf
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class CriadorBancoDesenhos:
    def __init__(self, caminho_dxf):
        self.caminho_dxf = caminho_dxf
        self.banco_desenhos = {}  # {viga_pos: {x, y, w, h}}
        self.arquivo_banco = "banco_desenhos.json"
        self.pasta_saida = "banco_desenhos"
        
        os.makedirs(self.pasta_saida, exist_ok=True)
        
        # Carregar banco existente
        self.carregar_banco()
        
        # Renderizar DXF
        print("Renderizando DXF completo...")
        self.renderizar_dxf_completo()
        
        # Criar interface
        self.criar_interface()
    
    def renderizar_dxf_completo(self):
        """Renderiza o DXF completo em PIL Image"""
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
            
            # 2 pixels por mm
            self.escala = 2
            self.img_width = int(largura_mm * self.escala)
            self.img_height = int(altura_mm * self.escala)
            
            # Limitar tamanho
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
            raise
    
    def criar_interface(self):
        """Interface Tkinter para captura de desenhos"""
        self.root = tk.Tk()
        self.root.title("Criar Banco de Desenhos")
        self.root.geometry("1400x900")
        
        # Frame esquerdo - entrada manual
        frame_esq = ttk.Frame(self.root, width=300)
        frame_esq.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(frame_esq, text="BANCO DE DESENHOS", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Entrada de identificação
        ttk.Label(frame_esq, text="Identificação:", font=('Arial', 10, 'bold')).pack(pady=(10,5))
        ttk.Label(frame_esq, text="Formato: VIGA-POS\nEx: VN6-9_N1", font=('Arial', 8)).pack()
        
        self.entry_id = ttk.Entry(frame_esq, width=25, font=('Arial', 11))
        self.entry_id.pack(pady=5)
        
        # Botões
        ttk.Button(frame_esq, text="📌 Capturar Região", command=self.capturar_regiao).pack(pady=5, fill=tk.X)
        ttk.Button(frame_esq, text="💾 Salvar Banco", command=self.salvar_banco).pack(pady=5, fill=tk.X)
        ttk.Button(frame_esq, text="🖼️ Gerar Todos PNGs", command=self.gerar_todos_pngs).pack(pady=5, fill=tk.X)
        
        self.label_status = ttk.Label(frame_esq, text="Digite identificação\ne marque região", foreground="blue")
        self.label_status.pack(pady=10)
        
        # Lista de desenhos capturados
        ttk.Label(frame_esq, text="Desenhos capturados:", font=('Arial', 10, 'bold')).pack(pady=(20,5))
        
        self.listbox = tk.Listbox(frame_esq, height=20, width=30)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.atualizar_lista()
        
        # Botão remover
        ttk.Button(frame_esq, text="🗑️ Remover Selecionado", command=self.remover_selecionado).pack(pady=5, fill=tk.X)
        
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
        
        # Adicionar imagem
        self.photo = ImageTk.PhotoImage(self.img_completa)
        self.canvas_img = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))
        
        # Seleção de região
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.regiao_selecionada = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.root.mainloop()
    
    def on_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )
    
    def on_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
    
    def on_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        
        x1 = int(min(self.start_x, end_x))
        y1 = int(min(self.start_y, end_y))
        x2 = int(max(self.start_x, end_x))
        y2 = int(max(self.start_y, end_y))
        
        self.regiao_selecionada = (x1, y1, x2 - x1, y2 - y1)
    
    def capturar_regiao(self):
        """Captura região e salva no banco"""
        identificacao = self.entry_id.get().strip()
        if not identificacao:
            messagebox.showwarning("Aviso", "Digite uma identificação (ex: VN6-9_N1)")
            return
        
        if not self.regiao_selecionada:
            messagebox.showwarning("Aviso", "Arraste um retângulo na imagem")
            return
        
        x, y, w, h = self.regiao_selecionada
        
        self.banco_desenhos[identificacao] = {
            'x': x, 'y': y, 'w': w, 'h': h
        }
        
        self.label_status.config(
            text=f"✅ {identificacao} capturado\n({w}x{h}px)",
            foreground="green"
        )
        
        self.atualizar_lista()
        self.entry_id.delete(0, tk.END)
        self.regiao_selecionada = None
        
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None
    
    def remover_selecionado(self):
        """Remove desenho selecionado do banco"""
        selection = self.listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        chaves = sorted(self.banco_desenhos.keys())
        if idx < len(chaves):
            chave = chaves[idx]
            del self.banco_desenhos[chave]
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", f"Removido: {chave}")
    
    def atualizar_lista(self):
        """Atualiza listbox com desenhos capturados"""
        self.listbox.delete(0, tk.END)
        for chave in sorted(self.banco_desenhos.keys()):
            coords = self.banco_desenhos[chave]
            self.listbox.insert(tk.END, f"{chave} ({coords['w']}x{coords['h']})")
    
    def salvar_banco(self):
        """Salva banco em JSON"""
        try:
            with open(self.arquivo_banco, 'w', encoding='utf-8') as f:
                json.dump(self.banco_desenhos, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Sucesso", f"Banco salvo: {self.arquivo_banco}\n{len(self.banco_desenhos)} desenhos")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def carregar_banco(self):
        """Carrega banco existente"""
        if os.path.exists(self.arquivo_banco):
            try:
                with open(self.arquivo_banco, 'r', encoding='utf-8') as f:
                    self.banco_desenhos = json.load(f)
                print(f"Carregado banco com {len(self.banco_desenhos)} desenhos")
            except Exception as e:
                print(f"Erro ao carregar banco: {e}")
    
    def gerar_todos_pngs(self):
        """Gera PNGs de todos os desenhos do banco"""
        if not self.banco_desenhos:
            messagebox.showwarning("Aviso", "Banco vazio")
            return
        
        gerados = 0
        for identificacao, coords in self.banco_desenhos.items():
            try:
                crop = self.img_completa.crop((
                    coords['x'], coords['y'],
                    coords['x'] + coords['w'], coords['y'] + coords['h']
                ))
                
                arquivo = os.path.join(self.pasta_saida, f"{identificacao}.png")
                crop.save(arquivo)
                gerados += 1
                print(f"✅ {arquivo}")
                
            except Exception as e:
                print(f"❌ Erro ao gerar {identificacao}: {e}")
        
        messagebox.showinfo("Sucesso", f"Gerados {gerados} PNGs em {self.pasta_saida}/")


if __name__ == "__main__":
    caminho_dxf = r"dxf\#PRANCHAS PREDIO Vigas 3 laje VN3 - Copia.dxf"
    
    print("="*60)
    print("CRIAR BANCO DE DESENHOS")
    print("="*60)
    print()
    print("INSTRUÇÕES:")
    print("1. Digite identificação (ex: VN6-9_N1)")
    print("2. Arraste retângulo sobre o desenho")
    print("3. Clique 'Capturar Região'")
    print("4. Repita para todos os desenhos")
    print("5. Clique 'Gerar Todos PNGs'")
    print()
    
    app = CriadorBancoDesenhos(caminho_dxf)
