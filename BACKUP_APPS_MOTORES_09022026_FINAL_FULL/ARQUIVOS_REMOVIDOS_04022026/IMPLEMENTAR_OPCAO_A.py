"""
IMPLEMENTAR_OPCAO_A.py
----------------------
SOLUÇÃO DEFINITIVA: Preview Renderizado (sem cache de PNGs)

Substitui o preview que carrega PNGs por um preview que RENDERIZA
as etiquetas no canvas (como o editor faz), garantindo que as
customizações sempre apareçam.
"""

import re
import shutil
from datetime import datetime

def criar_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"vigas_app_backup_opcaoA_{timestamp}.py"
    shutil.copy('vigas_app.py', backup_name)
    print(f"✅ Backup: {backup_name}")
    return backup_name

def aplicar_solucao_opcao_a():
    """
    Substitui o método _confirmar_e_imprimir_etiquetas para usar
    preview renderizado ao invés de carregar PNGs
    """
    backup = criar_backup()
    
    with open('vigas_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar o método _confirmar_e_imprimir_etiquetas e substituir completamente
    # Procurar início do método
    padrao_inicio = r'(    def _confirmar_e_imprimir_etiquetas\(self, selecionadas\):.*?""")'
    
    # Novo código do método
    novo_metodo = r'''\1
        """
        # Criar janela de preview RENDERIZADO (sem carregar PNGs)
        janela_preview = tk.Toplevel(self.root)
        janela_preview.title(f"Preview - {len(selecionadas)} Etiqueta(s) Selecionada(s)")
        janela_preview.geometry("900x700")
        
        # Frame principal
        frame_main = ttk.Frame(janela_preview)
        frame_main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas com scrollbar
        canvas = tk.Canvas(frame_main, bg='white', width=850, height=600)
        scrollbar = ttk.Scrollbar(frame_main, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Armazenar referências de imagens
        self._preview_images = []
        
        # Renderizar etiquetas selecionadas
        y_offset = 20
        for idx in selecionadas:
            if idx >= len(self.dados_processados):
                continue
            
            dados = self.dados_processados[idx]
            
            # Obter customizações se existirem
            medidas_custom = None
            forma_custom = None
            
            if hasattr(self, 'medidas_customizadas'):
                chave = f"{dados.get('viga', '')}_{dados.get('pos', '')}"
                medidas_custom = self.medidas_customizadas.get(chave)
            
            if hasattr(self, 'formas_customizadas'):
                chave = f"{dados.get('viga', '')}_{dados.get('pos', '')}"
                forma_custom = self.formas_customizadas.get(chave)
            
            # Renderizar etiqueta no canvas (mesmo código do editor)
            try:
                self._renderizar_etiqueta_preview(
                    canvas, dados, y_offset, 
                    medidas_custom, forma_custom, idx
                )
                y_offset += 620  # Espaço para próxima etiqueta
            except Exception as e:
                print(f"[PREVIEW] Erro ao renderizar etiqueta {idx}: {e}")
                # Desenhar placeholder de erro
                canvas.create_rectangle(
                    50, y_offset, 800, y_offset + 600,
                    outline="red", width=2
                )
                canvas.create_text(
                    425, y_offset + 300,
                    text=f"❌ Erro ao renderizar etiqueta #{idx+1}",
                    font=("Arial", 12),
                    fill="red"
                )
                y_offset += 620
        
        # Configurar scroll region
        canvas.configure(scrollregion=(0, 0, 850, y_offset + 20))
        
        # Frame de botões
        frame_botoes = ttk.Frame(janela_preview)
        frame_botoes.pack(fill=tk.X, padx=10, pady=10)
        
        def confirmar_impressao():
            janela_preview.destroy()
            # Gerar PNGs e imprimir
            self._gerar_e_imprimir_final(selecionadas)
        
        ttk.Button(
            frame_botoes,
            text="✅ Confirmar e Imprimir",
            command=confirmar_impressao
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame_botoes,
            text="❌ Cancelar",
            command=janela_preview.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        # Label de info
        ttk.Label(
            frame_botoes,
            text=f"📋 {len(selecionadas)} etiqueta(s) | Preview renderizado com suas edições",
            font=("Arial", 9)
        ).pack(side=tk.RIGHT, padx=5)
    
    def _renderizar_etiqueta_preview(self, canvas, dados, y_offset, medidas_custom, forma_custom, idx):
        """Renderiza uma etiqueta no canvas do preview"""
        # Usar mesmo código de renderização do editor
        # (simplificado para o preview)
        
        x_base = 50
        largura_etiq = 750
        altura_etiq = 600
        
        # Fundo branco
        canvas.create_rectangle(
            x_base, y_offset,
            x_base + largura_etiq, y_offset + altura_etiq,
            fill="white", outline="black", width=2
        )
        
        # Título
        canvas.create_text(
            x_base + largura_etiq//2, y_offset + 30,
            text=f"Etiqueta #{idx+1} - {dados.get('viga', 'N/A')} / {dados.get('pos', 'N/A')}",
            font=("Arial", 14, "bold"),
            fill="black"
        )
        
        # Informações
        y_info = y_offset + 70
        infos = [
            f"Bitola: {dados.get('bitola', 'N/A')} mm",
            f"Quantidade: {dados.get('qtde', 'N/A')}",
            f"Comprimento: {dados.get('comp_unit', 'N/A')} m",
            f"Peso: {dados.get('peso_kg', 'N/A')} kg"
        ]
        
        for info in infos:
            canvas.create_text(
                x_base + 20, y_info,
                text=info,
                font=("Arial", 11),
                fill="black",
                anchor="w"
            )
            y_info += 25
        
        # Mostrar customizações se existirem
        if medidas_custom or forma_custom:
            y_custom = y_info + 20
            canvas.create_text(
                x_base + 20, y_custom,
                text="✏️ CUSTOMIZAÇÕES APLICADAS:",
                font=("Arial", 10, "bold"),
                fill="blue",
                anchor="w"
            )
            y_custom += 25
            
            if medidas_custom:
                canvas.create_text(
                    x_base + 40, y_custom,
                    text=f"Medidas: {medidas_custom}",
                    font=("Arial", 9),
                    fill="blue",
                    anchor="w"
                )
                y_custom += 20
            
            if forma_custom:
                canvas.create_text(
                    x_base + 40, y_custom,
                    text=f"Forma: {forma_custom}",
                    font=("Arial", 9),
                    fill="blue",
                    anchor="w"
                )
        
        # Desenho técnico (se disponível)
        try:
            caminho_desenho = dados.get('caminho_desenho')
            if caminho_desenho and os.path.exists(caminho_desenho):
                from PIL import Image, ImageTk
                img = Image.open(caminho_desenho)
                img.thumbnail((400, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self._preview_images.append(photo)
                canvas.create_image(
                    x_base + largura_etiq//2,
                    y_offset + altura_etiq - 200,
                    image=photo
                )
        except Exception as e:
            print(f"[PREVIEW] Aviso: Desenho não carregado: {e}")
    
    def _gerar_e_imprimir_final(self, selecionadas):
        """Gera PNGs finais e imprime"""
        print(f"[IMPRESSÃO] Gerando PNGs finais para {len(selecionadas)} etiqueta(s)...")
        
        try:
            from core.etiquetas_generator import GeradorEtiquetasDinamico
            
            # Obter arquivos DXF
            arquivos_dxf = []
            if hasattr(self, 'arquivos_selecionados') and self.arquivos_selecionados:
                arquivos_dxf = self.arquivos_selecionados
            elif hasattr(self, 'lista_arquivos'):
                arquivos_dxf = [item[0] for item in self.lista_arquivos if item[0].lower().endswith('.dxf')]
            
            # Criar gerador
            gerador = GeradorEtiquetasDinamico(
                arquivos_dxf=arquivos_dxf,
                pasta_etiquetas="etiquetas",
                obra=self.var_obra.get() if hasattr(self, 'var_obra') else "OBRA 001",
                pavimento=self.var_pavimento.get() if hasattr(self, 'var_pavimento') else "TÉRREO"
            )
            
            # Copiar customizações
            if hasattr(self, 'medidas_customizadas'):
                gerador.medidas_customizadas = self.medidas_customizadas.copy()
            if hasattr(self, 'formas_customizadas'):
                gerador.formas_customizadas = self.formas_customizadas.copy()
            
            # Filtrar selecionadas
            gerador.dados = [self.dados_processados[i] for i in selecionadas]
            
            # Gerar e imprimir
            sucesso = gerador.gerar_e_imprimir_direto(
                impressora=None,  # Usar impressora padrão
                dpi_x=300,
                dpi_y=300
            )
            
            if sucesso:
                messagebox.showinfo("Sucesso", f"{len(selecionadas)} etiqueta(s) enviada(s) para impressão!")
            else:
                messagebox.showerror("Erro", "Falha ao imprimir etiquetas")
                
        except Exception as e:
            print(f"[ERRO] Falha na impressão: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao imprimir: {e}")'''
    
    # Aplicar substituição
    # Primeiro, encontrar onde termina o método antigo
    padrao_metodo_completo = r'    def _confirmar_e_imprimir_etiquetas\(self, selecionadas\):.*?(?=\n    def [a-z_]|\nclass |\Z)'
    
    content_novo = re.sub(padrao_metodo_completo, novo_metodo, content, flags=re.DOTALL)
    
    if content_novo == content:
        print("❌ ERRO: Método não encontrado ou não substituído!")
        return False
    
    # Salvar
    with open('vigas_app.py', 'w', encoding='utf-8') as f:
        f.write(content_novo)
    
    print("\n" + "="*70)
    print("✅ SOLUÇÃO OPÇÃO A APLICADA COM SUCESSO!")
    print("="*70)
    print("\n🔧 O que foi feito:")
    print("   1. Preview agora RENDERIZA etiquetas no canvas")
    print("   2. Não usa mais PNGs (sem cache)")
    print("   3. Mostra customizações em tempo real")
    print("   4. Botão 'Confirmar' gera PNGs e imprime")
    print("\n🔄 PRÓXIMO PASSO:")
    print("   1. FECHE o vigas_app.py")
    print("   2. Execute: python vigas_app.py")
    print("   3. Processe → Etiquetas → Edite → IMPRIMIR SELECIONADAS")
    print("   4. Preview agora mostrará suas edições!")
    print("="*70)
    return True

if __name__ == "__main__":
    print("\n" + "="*70)
    print("IMPLEMENTAÇÃO OPÇÃO A: Preview Renderizado")
    print("="*70 + "\n")
    
    sucesso = aplicar_solucao_opcao_a()
    
    if not sucesso:
        print("\n⚠️ Falha na aplicação. Verifique o código manualmente.")
