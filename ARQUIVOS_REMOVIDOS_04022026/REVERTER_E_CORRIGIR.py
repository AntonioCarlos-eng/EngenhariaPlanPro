"""
REVERTER_E_CORRIGIR.py
----------------------
Script para REVERTER a mudança errada e aplicar a correção CORRETA

PROBLEMA REAL:
- EDITOR (desenhar_etiquetas_com_selecao) está CORRETO ✅
- PREVIEW (desenhar_preview_com_pngs_gerados) está ERRADO ❌

SOLUÇÃO:
- PREVIEW deve usar o MESMO código do EDITOR (redesenhar com customizações)
"""

import os
import shutil
from datetime import datetime

def reverter_e_corrigir():
    """Reverte mudança errada e aplica correção correta"""
    
    arquivo = "vigas_app.py"
    backup = f"vigas_app_backup_correcao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    print("\n" + "="*70)
    print("REVERTENDO E CORRIGINDO: Preview = Editor")
    print("="*70)
    
    # Backup
    print(f"\n📦 Criando backup: {backup}")
    shutil.copy2(arquivo, backup)
    
    # Ler arquivo
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # REVERTER: Trocar de volta para desenhar_pagina_etiquetas_vigas_fase4
    print(f"\n🔄 Revertendo chamadas...")
    substituicoes = conteudo.count("self.desenhar_preview_com_pngs_gerados()")
    conteudo = conteudo.replace(
        "self.desenhar_preview_com_pngs_gerados()",
        "self.desenhar_etiquetas_com_selecao()"  # ← USAR O MESMO DO EDITOR!
    )
    print(f"✅ {substituicoes} chamadas revertidas para desenhar_etiquetas_com_selecao()")
    
    # Salvar
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print("\n" + "="*70)
    print("✅ CORREÇÃO APLICADA!")
    print("="*70)
    print(f"\nAgora PREVIEW e EDITOR usam o MESMO método:")
    print(f"  → desenhar_etiquetas_com_selecao()")
    print(f"\nIsso significa:")
    print(f"  ✅ Preview mostra suas edições (reto, dobras, estribos)")
    print(f"  ✅ Preview = Editor (100% idêntico)")
    print(f"  ✅ Quando você edita, preview atualiza automaticamente")
    print("\n" + "="*70 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        reverter_e_corrigir()
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
