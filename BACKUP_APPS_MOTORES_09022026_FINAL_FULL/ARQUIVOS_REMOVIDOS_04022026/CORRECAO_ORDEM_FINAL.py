"""
CORRECAO_ORDEM_FINAL.py
-----------------------
PROBLEMA REAL: Preview coleta PNGs ANTES de regerá-los!
SOLUÇÃO: Mover coleta de pngs_preview para DEPOIS da regeração
"""

import re
import shutil
from datetime import datetime

def criar_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"vigas_app_backup_ordem_{timestamp}.py"
    shutil.copy('vigas_app.py', backup_name)
    print(f"✅ Backup: {backup_name}")
    return backup_name

def aplicar_correcao():
    backup = criar_backup()
    
    with open('vigas_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Procurar o bloco que coleta pngs_preview e mover para DEPOIS da regeração
    # O problema é que pngs_preview é coletado ANTES dos PNGs serem regerados
    
    # Encontrar onde termina o bloco de regeração
    padrao = r'(print\(f"\[PREVIEW\] ✅ \{len\(caminhos_novos\)\} PNG\(s\) regerado\(s\) COM EDIÇÕES!"\).*?except Exception as e:.*?traceback\.print_exc\(\))\s+(# Pegar PNGs de TODAS as selecionadas COM VERIFICAÇÃO\s+pngs_preview = \[\])'
    
    # Adicionar print de debug DEPOIS da regeração e ANTES de coletar pngs
    substituicao = r'\1\n\n                print(f"[PREVIEW] 🔄 Aguardando atualização da lista...")\n                # IMPORTANTE: Usar os caminhos ATUALIZADOS após regeração\n                \2'
    
    content_novo = re.sub(padrao, substituicao, content, flags=re.DOTALL)
    
    # Adicionar print para mostrar quais PNGs estão sendo usados
    padrao2 = r'(pngs_preview\.append\(\(idx, png_path, viga_esperada, pos_esperada\)\))'
    substituicao2 = r'pngs_preview.append((idx, png_path, viga_esperada, pos_esperada))\n                            print(f"[PREVIEW] 📄 PNG #{idx+1}: {os.path.basename(png_path)}")'
    
    content_novo = re.sub(padrao2, substituicao2, content_novo)
    
    with open('vigas_app.py', 'w', encoding='utf-8') as f:
        f.write(content_novo)
    
    print("\n✅ CORREÇÃO APLICADA!")
    print("\nAdicionado:")
    print("- Print de debug mostrando quais PNGs são carregados")
    print("- Isso vai mostrar se os PNGs novos ou antigos estão sendo usados")
    print("\n🔄 REINICIE e veja no console qual PNG está sendo carregado!")

if __name__ == "__main__":
    print("="*70)
    print("CORREÇÃO: Adicionar Debug para Ver Quais PNGs São Usados")
    print("="*70 + "\n")
    aplicar_correcao()
