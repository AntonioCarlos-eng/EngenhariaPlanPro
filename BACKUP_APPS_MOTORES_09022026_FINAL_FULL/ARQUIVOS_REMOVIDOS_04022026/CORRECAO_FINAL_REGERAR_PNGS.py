"""
CORRECAO_FINAL_REGERAR_PNGS.py
---------------------------------
PROBLEMA REAL: Preview carrega PNGs ANTIGOS (gerados antes das edições)
SOLUÇÃO: REGERAR os PNGs com as customizações ANTES de abrir o preview
"""

import re

def aplicar_correcao():
    """Adiciona código para regerar PNGs antes do preview"""
    
    with open('vigas_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Procurar o bloco que abre o preview (linha ~4480)
    # Adicionar ANTES de "pngs_preview = []" um código para regerar os PNGs
    
    codigo_antigo = """                # Pegar PNGs de TODAS as selecionadas COM VERIFICAÇÃO
                pngs_preview = []"""
    
    codigo_novo = """                # ===== REGERAR PNGs COM CUSTOMIZAÇÕES =====
                print("[PREVIEW] Regerando PNGs com customizações...")
                
                # Criar gerador com customizações
                try:
                    from core.etiquetas_generator import GeradorEtiquetasDinamico
                    
                    # Obter arquivos DXF
                    arquivos_dxf = []
                    if hasattr(self, 'arquivos_selecionados') and self.arquivos_selecionados:
                        arquivos_dxf = self.arquivos_selecionados
                    
                    # Criar gerador
                    gerador = GeradorEtiquetasDinamico(
                        arquivos_dxf=arquivos_dxf,
                        pasta_etiquetas="etiquetas",
                        obra=self.var_obra.get() if hasattr(self, 'var_obra') else "OBRA 001",
                        pavimento=self.var_pavimento.get() if hasattr(self, 'var_pavimento') else "TÉRREO"
                    )
                    
                    # COPIAR customizações do editor
                    if hasattr(self, 'medidas_customizadas'):
                        gerador.medidas_customizadas = self.medidas_customizadas.copy()
                        print(f"[PREVIEW] Copiadas {len(self.medidas_customizadas)} customizações de medidas")
                    
                    if hasattr(self, 'formas_customizadas'):
                        gerador.formas_customizadas = self.formas_customizadas.copy()
                        print(f"[PREVIEW] Copiadas {len(self.formas_customizadas)} customizações de formas")
                    
                    # REGERAR apenas as selecionadas
                    gerador.dados = [self.dados_processados[i] for i in selecionadas]
                    
                    # Gerar PNGs com customizações
                    caminhos_novos = gerador.gerar_e_salvar_etiquetas_png()
                    
                    # Atualizar lista de PNGs
                    for i, idx in enumerate(selecionadas):
                        if i < len(caminhos_novos):
                            self.caminhos_etiquetas_geradas[idx] = caminhos_novos[i]
                    
                    print(f"[PREVIEW] {len(caminhos_novos)} PNG(s) regerado(s) com customizações!")
                    
                except Exception as e:
                    print(f"[AVISO] Erro ao regerar PNGs: {e}")
                    print("[AVISO] Usando PNGs existentes (podem estar desatualizados)")
                
                # Pegar PNGs de TODAS as selecionadas COM VERIFICAÇÃO
                pngs_preview = []"""
    
    if codigo_antigo in content:
        content = content.replace(codigo_antigo, codigo_novo)
        
        # Salvar
        with open('vigas_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ CORREÇÃO APLICADA!")
        print("\nO que foi feito:")
        print("- Adicionado código para REGERAR PNGs antes do preview")
        print("- PNGs agora incluem as customizações do editor")
        print("- Preview mostrará exatamente o que foi editado")
        print("\n🔄 REINICIE o programa para ver o efeito!")
        return True
    else:
        print("❌ Código antigo não encontrado!")
        print("O arquivo pode ter sido modificado.")
        return False

if __name__ == "__main__":
    print("="*70)
    print("CORREÇÃO FINAL: Regerar PNGs com Customizações")
    print("="*70)
    print()
    
    sucesso = aplicar_correcao()
    
    if sucesso:
        print("\n" + "="*70)
        print("✅ SUCESSO!")
        print("="*70)
        print("\nPRÓXIMOS PASSOS:")
        print("1. FECHE o vigas_app.py se estiver aberto")
        print("2. Execute: python vigas_app.py")
        print("3. Processe → Etiquetas → Edite → IMPRIMIR SELECIONADAS")
        print("4. O preview agora mostrará suas edições!")
        print("="*70)
    else:
        print("\n❌ Falha na correção. Verifique o arquivo manualmente.")
