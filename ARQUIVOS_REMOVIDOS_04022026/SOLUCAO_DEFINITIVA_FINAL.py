"""
SOLUCAO_DEFINITIVA_FINAL.py
---------------------------
Corrige o preview para mostrar as edições do editor

PROBLEMA: Preview carrega PNGs antigos (sem edições)
SOLUÇÃO: Regerar PNGs COM customizações antes de abrir preview
"""

import re
import shutil
from datetime import datetime

def criar_backup():
    """Cria backup do arquivo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"vigas_app_backup_final_{timestamp}.py"
    shutil.copy('vigas_app.py', backup_name)
    print(f"✅ Backup criado: {backup_name}")
    return backup_name

def aplicar_correcao_definitiva():
    """Aplica correção no método _confirmar_e_imprimir_etiquetas"""
    
    # Criar backup
    backup = criar_backup()
    
    with open('vigas_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Procurar o método _confirmar_e_imprimir_etiquetas
    # e adicionar código para regerar PNGs ANTES de coletar pngs_preview
    
    # Padrão: logo antes de "pngs_preview = []"
    padrao_antigo = r'(\s+)# Pegar PNGs de TODAS as selecionadas COM VERIFICAÇÃO\s+pngs_preview = \[\]'
    
    codigo_novo = r'''\1# ===== REGERAR PNGs COM CUSTOMIZAÇÕES DO EDITOR =====
\1print("[PREVIEW] Regerando PNGs com customizações do editor...")
\1try:
\1    from core.etiquetas_generator import GeradorEtiquetasDinamico
\1    
\1    # Obter arquivos DXF
\1    arquivos_dxf = []
\1    if hasattr(self, 'arquivos_selecionados') and self.arquivos_selecionados:
\1        arquivos_dxf = self.arquivos_selecionados
\1    elif hasattr(self, 'lista_arquivos'):
\1        arquivos_dxf = [item[0] for item in self.lista_arquivos if item[0].lower().endswith('.dxf')]
\1    
\1    if arquivos_dxf:
\1        # Criar gerador
\1        gerador = GeradorEtiquetasDinamico(
\1            arquivos_dxf=arquivos_dxf,
\1            pasta_etiquetas="etiquetas",
\1            obra=self.var_obra.get() if hasattr(self, 'var_obra') else "OBRA 001",
\1            pavimento=self.var_pavimento.get() if hasattr(self, 'var_pavimento') else "TÉRREO"
\1        )
\1        
\1        # COPIAR customizações do editor
\1        if hasattr(self, 'medidas_customizadas') and self.medidas_customizadas:
\1            gerador.medidas_customizadas = self.medidas_customizadas.copy()
\1            print(f"[PREVIEW] ✅ {len(self.medidas_customizadas)} customizações de medidas copiadas")
\1        
\1        if hasattr(self, 'formas_customizadas') and self.formas_customizadas:
\1            gerador.formas_customizadas = self.formas_customizadas.copy()
\1            print(f"[PREVIEW] ✅ {len(self.formas_customizadas)} customizações de formas copiadas")
\1        
\1        # REGERAR apenas as selecionadas
\1        gerador.dados = [self.dados_processados[i] for i in selecionadas]
\1        
\1        # Gerar PNGs ATUALIZADOS
\1        caminhos_novos = gerador.gerar_e_salvar_etiquetas_png()
\1        
\1        # Atualizar lista de PNGs
\1        for i, idx in enumerate(selecionadas):
\1            if i < len(caminhos_novos) and idx < len(self.caminhos_etiquetas_geradas):
\1                self.caminhos_etiquetas_geradas[idx] = caminhos_novos[i]
\1        
\1        print(f"[PREVIEW] ✅ {len(caminhos_novos)} PNG(s) regerado(s) COM EDIÇÕES!")
\1    else:
\1        print("[PREVIEW] ⚠️ Nenhum arquivo DXF encontrado")
\1        
\1except Exception as e:
\1    print(f"[PREVIEW] ⚠️ Erro ao regerar PNGs: {e}")
\1    print("[PREVIEW] ⚠️ Usando PNGs existentes (podem estar desatualizados)")
\1    import traceback
\1    traceback.print_exc()
\1
\1# Pegar PNGs de TODAS as selecionadas COM VERIFICAÇÃO
\1pngs_preview = []'''
    
    # Aplicar substituição
    content_novo, num_subs = re.subn(padrao_antigo, codigo_novo, content)
    
    if num_subs > 0:
        # Salvar arquivo modificado
        with open('vigas_app.py', 'w', encoding='utf-8') as f:
            f.write(content_novo)
        
        print("\n" + "="*70)
        print("✅ CORREÇÃO APLICADA COM SUCESSO!")
        print("="*70)
        print(f"\n📝 Modificações: {num_subs} bloco(s) corrigido(s)")
        print(f"💾 Backup: {backup}")
        print("\n🔧 O que foi feito:")
        print("   1. Antes de abrir o preview, o sistema agora:")
        print("      - Cria novo GeradorEtiquetasDinamico")
        print("      - COPIA suas customizações do editor")
        print("      - REGERA os PNGs com as edições")
        print("      - Atualiza a lista de PNGs")
        print("   2. Preview agora mostra PNGs ATUALIZADOS!")
        print("\n🔄 PRÓXIMO PASSO:")
        print("   1. FECHE o vigas_app.py")
        print("   2. Execute: python vigas_app.py")
        print("   3. Processe → Etiquetas → Edite → IMPRIMIR SELECIONADAS")
        print("   4. O preview agora mostrará suas edições!")
        print("\n💡 VALIDAÇÃO:")
        print("   No console, você verá:")
        print("   [PREVIEW] Regerando PNGs com customizações do editor...")
        print("   [PREVIEW] ✅ X customizações de medidas copiadas")
        print("   [PREVIEW] ✅ Y PNG(s) regerado(s) COM EDIÇÕES!")
        print("="*70)
        return True
    else:
        print("❌ ERRO: Padrão não encontrado no código!")
        print("O arquivo pode ter sido modificado.")
        print(f"Restaurando backup: {backup}")
        shutil.copy(backup, 'vigas_app.py')
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SOLUÇÃO DEFINITIVA FINAL")
    print("Corrige preview para mostrar edições do editor")
    print("="*70 + "\n")
    
    sucesso = aplicar_correcao_definitiva()
    
    if not sucesso:
        print("\n⚠️ Se o erro persistir, me avise para análise manual.")
