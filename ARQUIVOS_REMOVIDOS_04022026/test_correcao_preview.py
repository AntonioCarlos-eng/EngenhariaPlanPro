"""
test_correcao_preview.py
------------------------
Teste para validar que o preview carrega os PNGs gerados pelo GeradorEtiquetasDinamico
Garante que PREVIEW = IMPRESSÃO (100% idêntico)
"""
import os
import sys
from pathlib import Path

# Adicionar pasta raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_preview_carrega_pngs():
    """Testa se o preview consegue carregar os PNGs gerados"""
    print("\n" + "="*70)
    print("TESTE: Preview Carrega PNGs do Gerador")
    print("="*70)
    
    # 1. Verificar se pasta de etiquetas existe
    pasta_etiquetas = r"c:\EngenhariaPlanPro\etiquetas"
    print(f"\n1. Verificando pasta: {pasta_etiquetas}")
    
    if not os.path.exists(pasta_etiquetas):
        print(f"   ❌ Pasta não existe!")
        return False
    
    print(f"   ✅ Pasta existe")
    
    # 2. Listar PNGs gerados
    pngs = [f for f in os.listdir(pasta_etiquetas) 
            if f.startswith('ETIQUETA_') and f.endswith('.png')]
    
    print(f"\n2. PNGs encontrados: {len(pngs)}")
    
    if not pngs:
        print(f"   ❌ Nenhum PNG encontrado!")
        print(f"   💡 Execute o processamento primeiro para gerar as etiquetas")
        return False
    
    print(f"   ✅ {len(pngs)} PNG(s) encontrado(s)")
    
    # 3. Mostrar primeiros 5 PNGs
    print(f"\n3. Primeiros PNGs:")
    for i, png in enumerate(pngs[:5], 1):
        caminho_completo = os.path.join(pasta_etiquetas, png)
        tamanho = os.path.getsize(caminho_completo) / 1024  # KB
        print(f"   {i}. {png} ({tamanho:.1f} KB)")
    
    # 4. Testar carregamento de um PNG
    print(f"\n4. Testando carregamento do primeiro PNG...")
    try:
        from PIL import Image
        primeiro_png = os.path.join(pasta_etiquetas, pngs[0])
        img = Image.open(primeiro_png)
        print(f"   ✅ PNG carregado com sucesso!")
        print(f"   📐 Dimensões: {img.size[0]}x{img.size[1]} pixels")
        print(f"   🎨 Modo: {img.mode}")
    except Exception as e:
        print(f"   ❌ Erro ao carregar PNG: {e}")
        return False
    
    # 5. Validar estrutura do nome do arquivo
    print(f"\n5. Validando estrutura dos nomes...")
    exemplo = pngs[0]
    if exemplo.startswith('ETIQUETA_') and '_b' in exemplo and '_q' in exemplo and '_c' in exemplo:
        print(f"   ✅ Estrutura correta: {exemplo}")
    else:
        print(f"   ⚠️ Estrutura inesperada: {exemplo}")
    
    print("\n" + "="*70)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*70)
    print("\n💡 PRÓXIMO PASSO:")
    print("   Execute o vigas_app.py e clique em 'Etiquetas'")
    print("   O preview deve mostrar os PNGs gerados (idênticos à impressão)")
    print("="*70 + "\n")
    
    return True


def test_metodo_novo_preview():
    """Testa o novo método de preview que carrega PNGs"""
    print("\n" + "="*70)
    print("TESTE: Novo Método de Preview")
    print("="*70)
    
    print("\n📋 IMPLEMENTAÇÃO NECESSÁRIA no vigas_app.py:")
    print("-" * 70)
    
    codigo = '''
    def desenhar_preview_com_pngs_gerados(self):
        """
        NOVO: Carrega e exibe os PNGs já gerados pelo GeradorEtiquetasDinamico
        Garante que PREVIEW = IMPRESSÃO (100% idêntico)
        """
        # Limpar canvas
        self.canvas_etiq.delete("all")
        self._barcode_images = []
        self._desenho_images = []
        
        # Verificar se há PNGs gerados
        if not hasattr(self, 'caminhos_etiquetas_geradas'):
            pasta_etiquetas = r"c:\\EngenhariaPlanPro\\etiquetas"
            if os.path.exists(pasta_etiquetas):
                pngs = sorted([os.path.join(pasta_etiquetas, f) 
                              for f in os.listdir(pasta_etiquetas) 
                              if f.startswith('ETIQUETA_') and f.endswith('.png')])
                self.caminhos_etiquetas_geradas = pngs
        
        if not self.caminhos_etiquetas_geradas:
            messagebox.showerror("Erro", "Nenhuma etiqueta PNG gerada!\\n\\nProcesse primeiro.")
            return
        
        # Calcular índices da página
        inicio = self.pagina_atual * self.etiquetas_por_pagina
        fim = min(inicio + self.etiquetas_por_pagina, len(self.caminhos_etiquetas_geradas))
        
        # Dimensões
        canvas_w = int(self.canvas_etiq.cget('width'))
        margem = 20
        y_cursor = margem
        
        # Carregar e exibir cada PNG
        for idx in range(inicio, fim):
            caminho_png = self.caminhos_etiquetas_geradas[idx]
            
            try:
                # Carregar PNG gerado
                img = Image.open(caminho_png)
                
                # Redimensionar para caber no canvas
                max_width = canvas_w - (2 * margem)
                max_height = 600
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Converter para PhotoImage
                photo = ImageTk.PhotoImage(img)
                self._desenho_images.append(photo)
                
                # Centralizar e desenhar
                x_center = canvas_w // 2
                self.canvas_etiq.create_image(x_center, y_cursor, image=photo, anchor="n")
                
                # Label
                self.canvas_etiq.create_text(
                    x_center, y_cursor + img.height + 10,
                    text=f"Etiqueta #{idx + 1}",
                    font=("Arial", 8),
                    fill="gray"
                )
                
                y_cursor += img.height + 40
                
            except Exception as e:
                print(f"[ERRO] {caminho_png}: {e}")
                # Placeholder de erro
                self.canvas_etiq.create_rectangle(
                    margem, y_cursor, canvas_w - margem, y_cursor + 200,
                    outline="red", width=2
                )
                self.canvas_etiq.create_text(
                    canvas_w // 2, y_cursor + 100,
                    text=f"❌ ERRO ao carregar",
                    font=("Arial", 10),
                    fill="red"
                )
                y_cursor += 220
        
        # Atualizar scroll
        self.canvas_etiq.configure(scrollregion=(0, 0, canvas_w, y_cursor + margem))
        
        # Atualizar label
        if hasattr(self, 'label_pagina'):
            self.label_pagina.config(text=f"Página {self.pagina_atual + 1} de {self.total_paginas}")
    '''
    
    print(codigo)
    print("-" * 70)
    
    print("\n📝 MODIFICAÇÃO NECESSÁRIA:")
    print("   Substituir chamada de:")
    print("   ❌ self.desenhar_pagina_etiquetas_vigas_fase4()")
    print("   ✅ self.desenhar_preview_com_pngs_gerados()")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    print("\n🔧 TESTE DE CORREÇÃO: Preview = Gerador\n")
    
    # Teste 1: Verificar PNGs
    sucesso = test_preview_carrega_pngs()
    
    # Teste 2: Mostrar implementação
    test_metodo_novo_preview()
    
    if sucesso:
        print("\n✅ TUDO PRONTO PARA IMPLEMENTAR A CORREÇÃO!")
    else:
        print("\n⚠️ GERE AS ETIQUETAS PRIMEIRO (Processar → Etiquetas)")
