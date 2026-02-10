"""
aplicar_correcao_preview.py
---------------------------
Script para aplicar automaticamente a correção do preview de etiquetas

EXECUÇÃO:
    python aplicar_correcao_preview.py

O script irá:
1. Fazer backup do vigas_app.py original
2. Adicionar o novo método desenhar_preview_com_pngs_gerados()
3. Substituir todas as chamadas do método antigo
4. Salvar o arquivo corrigido
"""

import os
import shutil
from datetime import datetime

def aplicar_correcao():
    """Aplica a correção no vigas_app.py"""
    
    arquivo_original = "vigas_app.py"
    arquivo_backup = f"vigas_app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    print("\n" + "="*70)
    print("APLICANDO CORREÇÃO: Preview = Gerador")
    print("="*70)
    
    # 1. Verificar se arquivo existe
    if not os.path.exists(arquivo_original):
        print(f"\n❌ ERRO: Arquivo {arquivo_original} não encontrado!")
        return False
    
    print(f"\n✅ Arquivo encontrado: {arquivo_original}")
    
    # 2. Fazer backup
    print(f"📦 Criando backup: {arquivo_backup}")
    shutil.copy2(arquivo_original, arquivo_backup)
    print(f"✅ Backup criado com sucesso!")
    
    # 3. Ler conteúdo
    print(f"\n📖 Lendo arquivo...")
    with open(arquivo_original, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # 4. Adicionar novo método (após ultima_pagina)
    novo_metodo = '''
    def desenhar_preview_com_pngs_gerados(self):
        """
        NOVO: Carrega e exibe os PNGs já gerados pelo GeradorEtiquetasDinamico
        Garante que PREVIEW = IMPRESSÃO (100% idêntico)
        """
        print("\\n[PREVIEW] Carregando PNGs gerados...")
        
        # Limpar canvas
        self.canvas_etiq.delete("all")
        self._barcode_images = []
        self._desenho_images = []
        
        # Verificar se há PNGs gerados
        if not hasattr(self, 'caminhos_etiquetas_geradas') or not self.caminhos_etiquetas_geradas:
            # Fallback: tentar localizar PNGs na pasta
            pasta_etiquetas = r"c:\\EngenhariaPlanPro\\etiquetas"
            print(f"[PREVIEW] Procurando PNGs em: {pasta_etiquetas}")
            
            if os.path.exists(pasta_etiquetas):
                pngs = sorted([os.path.join(pasta_etiquetas, f) 
                              for f in os.listdir(pasta_etiquetas) 
                              if f.startswith('ETIQUETA_') and f.endswith('.png')])
                self.caminhos_etiquetas_geradas = pngs
                print(f"[PREVIEW] Encontrados {len(pngs)} PNG(s)")
            else:
                print(f"[PREVIEW] Pasta não existe: {pasta_etiquetas}")
        
        if not self.caminhos_etiquetas_geradas:
            messagebox.showerror(
                "Erro - Etiquetas não geradas", 
                "Nenhuma etiqueta PNG foi gerada!\\n\\n"
                "Por favor, processe os arquivos DXF primeiro.\\n"
                "O sistema irá gerar as etiquetas automaticamente."
            )
            return
        
        # Calcular índices da página atual
        inicio = self.pagina_atual * self.etiquetas_por_pagina
        fim = min(inicio + self.etiquetas_por_pagina, len(self.caminhos_etiquetas_geradas))
        
        print(f"[PREVIEW] Página {self.pagina_atual + 1}: exibindo etiquetas {inicio+1} a {fim}")
        
        # Dimensões e posicionamento
        canvas_w = int(self.canvas_etiq.cget('width'))
        margem = 20
        y_cursor = margem
        
        # Carregar e exibir cada PNG
        for idx in range(inicio, fim):
            caminho_png = self.caminhos_etiquetas_geradas[idx]
            
            try:
                # Carregar PNG gerado
                img = Image.open(caminho_png)
                print(f"[PREVIEW] Carregando: {os.path.basename(caminho_png)} ({img.size[0]}x{img.size[1]}px)")
                
                # Redimensionar para caber no canvas (mantendo proporção)
                max_width = canvas_w - (2 * margem)
                max_height = 600
                
                # Calcular escala mantendo proporção
                scale_w = max_width / img.size[0] if img.size[0] > max_width else 1.0
                scale_h = max_height / img.size[1] if img.size[1] > max_height else 1.0
                scale = min(scale_w, scale_h)
                
                if scale < 1.0:
                    new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    print(f"[PREVIEW] Redimensionado para: {new_size[0]}x{new_size[1]}px")
                
                # Converter para PhotoImage
                photo = ImageTk.PhotoImage(img)
                self._desenho_images.append(photo)
                
                # Centralizar horizontalmente
                x_center = canvas_w // 2
                
                # Desenhar no canvas
                self.canvas_etiq.create_image(x_center, y_cursor, image=photo, anchor="n")
                
                # Adicionar label com número da etiqueta
                self.canvas_etiq.create_text(
                    x_center, y_cursor + img.height + 10,
                    text=f"Etiqueta #{idx + 1} de {len(self.caminhos_etiquetas_geradas)}",
                    font=("Arial", 9, "bold"),
                    fill="#ff6f00"
                )
                
                # Adicionar nome do arquivo (para debug)
                self.canvas_etiq.create_text(
                    x_center, y_cursor + img.height + 25,
                    text=os.path.basename(caminho_png),
                    font=("Arial", 7),
                    fill="gray"
                )
                
                # Atualizar cursor
                y_cursor += img.height + 50
                
            except Exception as e:
                print(f"[ERRO] Falha ao carregar PNG {caminho_png}: {e}")
                import traceback
                traceback.print_exc()
                
                # Desenhar placeholder de erro
                self.canvas_etiq.create_rectangle(
                    margem, y_cursor, canvas_w - margem, y_cursor + 200,
                    outline="red", width=2, fill="#ffe6e6"
                )
                self.canvas_etiq.create_text(
                    canvas_w // 2, y_cursor + 100,
                    text=f"❌ ERRO ao carregar\\n{os.path.basename(caminho_png)}\\n\\n{str(e)}",
                    font=("Arial", 10),
                    fill="red",
                    justify="center"
                )
                y_cursor += 220
        
        # Atualizar scroll region
        self.canvas_etiq.configure(scrollregion=(0, 0, canvas_w, y_cursor + margem))
        
        # Atualizar label de página
        if hasattr(self, 'label_pagina'):
            self.label_pagina.config(text=f"Página {self.pagina_atual + 1} de {self.total_paginas}")
        
        print(f"[PREVIEW] ✅ Preview atualizado com sucesso!\\n")
'''
    
    # Procurar onde inserir (após ultima_pagina)
    if "def ultima_pagina(self):" in conteudo:
        # Encontrar o final do método ultima_pagina
        pos_ultima = conteudo.find("def ultima_pagina(self):")
        # Procurar próximo método após ultima_pagina
        pos_proximo = conteudo.find("\n    def ", pos_ultima + 50)
        
        if pos_proximo > 0:
            # Inserir novo método antes do próximo
            conteudo = conteudo[:pos_proximo] + novo_metodo + conteudo[pos_proximo:]
            print("✅ Novo método adicionado após ultima_pagina()")
        else:
            print("⚠️ Não foi possível localizar posição exata, adicionando no final da classe")
            # Adicionar antes do final do arquivo
            conteudo = conteudo.rstrip() + "\n" + novo_metodo + "\n"
    else:
        print("❌ ERRO: Método ultima_pagina() não encontrado!")
        return False
    
    # 5. Substituir chamadas
    print("\n🔄 Substituindo chamadas do método antigo...")
    substituicoes = conteudo.count("self.desenhar_pagina_etiquetas_vigas_fase4()")
    conteudo = conteudo.replace(
        "self.desenhar_pagina_etiquetas_vigas_fase4()",
        "self.desenhar_preview_com_pngs_gerados()"
    )
    print(f"✅ {substituicoes} substituições realizadas")
    
    # 6. Salvar arquivo corrigido
    print(f"\n💾 Salvando arquivo corrigido...")
    with open(arquivo_original, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print(f"✅ Arquivo salvo com sucesso!")
    
    # 7. Resumo
    print("\n" + "="*70)
    print("✅ CORREÇÃO APLICADA COM SUCESSO!")
    print("="*70)
    print(f"\n📁 Arquivos:")
    print(f"   Original (corrigido): {arquivo_original}")
    print(f"   Backup: {arquivo_backup}")
    print(f"\n📊 Mudanças:")
    print(f"   ✅ Novo método adicionado: desenhar_preview_com_pngs_gerados()")
    print(f"   ✅ {substituicoes} chamadas substituídas")
    print(f"\n🧪 Próximos passos:")
    print(f"   1. Execute: python vigas_app.py")
    print(f"   2. Processe um arquivo DXF")
    print(f"   3. Clique em 'Etiquetas'")
    print(f"   4. Verifique que preview mostra os PNGs gerados")
    print(f"\n💡 Se houver problemas:")
    print(f"   - Restaure o backup: copy {arquivo_backup} {arquivo_original}")
    print(f"   - Execute: python test_correcao_preview.py")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        sucesso = aplicar_correcao()
        if not sucesso:
            print("\n❌ Correção não foi aplicada!")
            exit(1)
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
